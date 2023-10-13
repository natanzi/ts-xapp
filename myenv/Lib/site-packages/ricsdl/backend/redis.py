# Copyright (c) 2019 AT&T Intellectual Property.
# Copyright (c) 2018-2022 Nokia.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# This source code is part of the near-RT RIC (RAN Intelligent Controller)
# platform project (RICP).
#


"""The module provides implementation of Shared Data Layer (SDL) database backend interface."""
import contextlib
import threading
from typing import (Callable, Dict, Set, List, Optional, Tuple, Union)
import zlib
import redis
from redis import Redis
from redis.sentinel import Sentinel
from redis.lock import Lock
from redis.utils import str_if_bytes
from redis import exceptions as redis_exceptions
from ricsdl.configuration import _Configuration
from ricsdl.exceptions import (
    RejectedByBackend,
    NotConnected,
    BackendError
)
from .dbbackend_abc import DbBackendAbc
from .dbbackend_abc import DbBackendLockAbc


@contextlib.contextmanager
def _map_to_sdl_exception():
    """Translates known redis exceptions into SDL exceptions."""
    try:
        yield
    except redis_exceptions.ResponseError as exc:
        raise RejectedByBackend("SDL backend rejected the request: {}".
                                format(str(exc))) from exc
    except (redis_exceptions.ConnectionError, redis_exceptions.TimeoutError) as exc:
        raise NotConnected("SDL not connected to backend: {}".
                           format(str(exc))) from exc
    except redis_exceptions.RedisError as exc:
        raise BackendError("SDL backend failed to process the request: {}".
                           format(str(exc))) from exc


class PubSub(redis.client.PubSub):
    def __init__(self, event_separator, connection_pool, ignore_subscribe_messages=False):
        super().__init__(connection_pool, shard_hint=None, ignore_subscribe_messages=ignore_subscribe_messages)
        self.event_separator = event_separator

    def handle_message(self, response, ignore_subscribe_messages=False):
        """
        Parses a pub/sub message. If the channel or pattern was subscribed to
        with a message handler, the handler is invoked instead of a parsed
        message being returned.

        Adapted from: https://github.com/andymccurdy/redis-py/blob/master/redis/client.py
        """
        message_type = str_if_bytes(response[0])
        if message_type == 'pmessage':
            message = {
                'type': message_type,
                'pattern': response[1],
                'channel': response[2],
                'data': response[3]
            }
        elif message_type == 'pong':
            message = {
                'type': message_type,
                'pattern': None,
                'channel': None,
                'data': response[1]
            }
        else:
            message = {
                'type': message_type,
                'pattern': None,
                'channel': response[1],
                'data': response[2]
            }

        # if this is an unsubscribe message, remove it from memory
        if message_type in self.UNSUBSCRIBE_MESSAGE_TYPES:
            if message_type == 'punsubscribe':
                pattern = response[1]
                if pattern in self.pending_unsubscribe_patterns:
                    self.pending_unsubscribe_patterns.remove(pattern)
                    self.patterns.pop(pattern, None)
            else:
                channel = response[1]
                if channel in self.pending_unsubscribe_channels:
                    self.pending_unsubscribe_channels.remove(channel)
                    self.channels.pop(channel, None)

        if message_type in self.PUBLISH_MESSAGE_TYPES:
            # if there's a message handler, invoke it
            if message_type == 'pmessage':
                handler = self.patterns.get(message['pattern'], None)
            else:
                handler = self.channels.get(message['channel'], None)
            if handler:
                # Need to send only channel and notification instead of raw
                # message
                message_channel = self._strip_ns_from_bin_key('', message['channel'])
                message_data = message['data'].decode('utf-8')
                messages = message_data.split(self.event_separator)
                handler(message_channel, messages)
                return message_channel, messages
        elif message_type != 'pong':
            # this is a subscribe/unsubscribe message. ignore if we don't
            # want them
            if ignore_subscribe_messages or self.ignore_subscribe_messages:
                return None

        return message

    @classmethod
    def _strip_ns_from_bin_key(cls, ns: str, nskey: bytes) -> str:
        try:
            redis_key = nskey.decode('utf-8')
        except UnicodeDecodeError as exc:
            msg = u'Namespace %s key conversion to string failed: %s' % (ns, str(exc))
            raise RejectedByBackend(msg)
        nskey = redis_key.split(',', 1)
        if len(nskey) != 2:
            msg = u'Namespace %s key:%s has no namespace prefix' % (ns, redis_key)
            raise RejectedByBackend(msg)
        return nskey[1]


class RedisBackend(DbBackendAbc):
    """
    A class providing an implementation of database backend of Shared Data Layer (SDL), when
    backend database solution is Redis.

    Args:
        configuration (_Configuration): SDL configuration, containing credentials to connect to
                                        Redis database backend.
    """
    def __init__(self, configuration: _Configuration) -> None:
        super().__init__()
        self.next_client_event = 0
        self.event_separator = configuration.get_event_separator()
        self.clients = list()
        with _map_to_sdl_exception():
            self.clients = self.__create_redis_clients(configuration)

    def __del__(self):
        self.close()

    def __str__(self):
        out = {"DB type": "Redis"}
        for i, r in enumerate(self.clients):
            out["Redis client[" + str(i) + "]"] = str(r)
        return str(out)

    def is_connected(self):
        is_connected = True
        with _map_to_sdl_exception():
            for c in self.clients:
                if not c.redis_client.ping():
                    is_connected = False
                    break
        return is_connected

    def close(self):
        for c in self.clients:
            c.redis_client.close()

    def set(self, ns: str, data_map: Dict[str, bytes]) -> None:
        db_data_map = self.__add_data_map_ns_prefix(ns, data_map)
        with _map_to_sdl_exception():
            self.__getClient(ns).mset(db_data_map)

    def set_if(self, ns: str, key: str, old_data: bytes, new_data: bytes) -> bool:
        db_key = self.__add_key_ns_prefix(ns, key)
        with _map_to_sdl_exception():
            return self.__getClient(ns).execute_command('SETIE', db_key, new_data, old_data)

    def set_if_not_exists(self, ns: str, key: str, data: bytes) -> bool:
        db_key = self.__add_key_ns_prefix(ns, key)
        with _map_to_sdl_exception():
            return self.__getClient(ns).setnx(db_key, data)

    def get(self, ns: str, keys: List[str]) -> Dict[str, bytes]:
        ret = dict()
        db_keys = self.__add_keys_ns_prefix(ns, keys)
        with _map_to_sdl_exception():
            values = self.__getClient(ns).mget(db_keys)
            for idx, val in enumerate(values):
                # return only key values, which has a value
                if val is not None:
                    ret[keys[idx]] = val
            return ret

    def find_keys(self, ns: str, key_pattern: str) -> List[str]:
        db_key_pattern = self.__add_key_ns_prefix(ns, key_pattern)
        with _map_to_sdl_exception():
            ret = self.__getClient(ns).keys(db_key_pattern)
            return self.__strip_ns_from_bin_keys(ns, ret)

    def find_and_get(self, ns: str, key_pattern: str) -> Dict[str, bytes]:
        # todo: replace below implementation with redis 'NGET' module
        ret = dict()  # type: Dict[str, bytes]
        with _map_to_sdl_exception():
            matched_keys = self.find_keys(ns, key_pattern)
            if matched_keys:
                ret = self.get(ns, matched_keys)
        return ret

    def remove(self, ns: str, keys: List[str]) -> None:
        db_keys = self.__add_keys_ns_prefix(ns, keys)
        with _map_to_sdl_exception():
            self.__getClient(ns).delete(*db_keys)

    def remove_if(self, ns: str, key: str, data: bytes) -> bool:
        db_key = self.__add_key_ns_prefix(ns, key)
        with _map_to_sdl_exception():
            return self.__getClient(ns).execute_command('DELIE', db_key, data)

    def add_member(self, ns: str, group: str, members: Set[bytes]) -> None:
        db_key = self.__add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            self.__getClient(ns).sadd(db_key, *members)

    def remove_member(self, ns: str, group: str, members: Set[bytes]) -> None:
        db_key = self.__add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            self.__getClient(ns).srem(db_key, *members)

    def remove_group(self, ns: str, group: str) -> None:
        db_key = self.__add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            self.__getClient(ns).delete(db_key)

    def get_members(self, ns: str, group: str) -> Set[bytes]:
        db_key = self.__add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            return self.__getClient(ns).smembers(db_key)

    def is_member(self, ns: str, group: str, member: bytes) -> bool:
        db_key = self.__add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            return self.__getClient(ns).sismember(db_key, member)

    def group_size(self, ns: str, group: str) -> int:
        db_key = self.__add_key_ns_prefix(ns, group)
        with _map_to_sdl_exception():
            return self.__getClient(ns).scard(db_key)

    def set_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]],
                        data_map: Dict[str, bytes]) -> None:
        db_data_map = self.__add_data_map_ns_prefix(ns, data_map)
        channels_and_events_prepared = []
        total_events = 0
        channels_and_events_prepared, total_events = self._prepare_channels(ns, channels_and_events)
        with _map_to_sdl_exception():
            return self.__getClient(ns).execute_command(
                "MSETMPUB",
                len(db_data_map),
                total_events,
                *[val for data in db_data_map.items() for val in data],
                *channels_and_events_prepared,
            )

    def set_if_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]], key: str,
                           old_data: bytes, new_data: bytes) -> bool:
        db_key = self.__add_key_ns_prefix(ns, key)
        channels_and_events_prepared = []
        channels_and_events_prepared, _ = self._prepare_channels(ns, channels_and_events)
        with _map_to_sdl_exception():
            ret = self.__getClient(ns).execute_command("SETIEMPUB", db_key, new_data, old_data,
                                                       *channels_and_events_prepared)
            return ret == b"OK"

    def set_if_not_exists_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]],
                                      key: str, data: bytes) -> bool:
        db_key = self.__add_key_ns_prefix(ns, key)
        channels_and_events_prepared, _ = self._prepare_channels(ns, channels_and_events)
        with _map_to_sdl_exception():
            ret = self.__getClient(ns).execute_command("SETNXMPUB", db_key, data,
                                                       *channels_and_events_prepared)
            return ret == b"OK"

    def remove_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]],
                           keys: List[str]) -> None:
        db_keys = self.__add_keys_ns_prefix(ns, keys)
        channels_and_events_prepared, total_events = self._prepare_channels(ns, channels_and_events)
        with _map_to_sdl_exception():
            return self.__getClient(ns).execute_command(
                "DELMPUB",
                len(db_keys),
                total_events,
                *db_keys,
                *channels_and_events_prepared,
            )

    def remove_if_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]], key: str,
                              data: bytes) -> bool:
        db_key = self.__add_key_ns_prefix(ns, key)
        channels_and_events_prepared, _ = self._prepare_channels(ns, channels_and_events)
        with _map_to_sdl_exception():
            ret = self.__getClient(ns).execute_command("DELIEMPUB", db_key, data,
                                                       *channels_and_events_prepared)
            return bool(ret)

    def remove_all_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]]) -> None:
        keys = self.__getClient(ns).keys(self.__add_key_ns_prefix(ns, "*"))
        channels_and_events_prepared, total_events = self._prepare_channels(ns, channels_and_events)
        with _map_to_sdl_exception():
            return self.__getClient(ns).execute_command(
                "DELMPUB",
                len(keys),
                total_events,
                *keys,
                *channels_and_events_prepared,
            )

    def subscribe_channel(self, ns: str, cb: Callable[[str, List[str]], None],
                          channels: List[str]) -> None:
        channels = self.__add_keys_ns_prefix(ns, channels)
        for channel in channels:
            with _map_to_sdl_exception():
                redis_ctx = self.__getClientConn(ns)
                redis_ctx.redis_pubsub.subscribe(**{channel: cb})
                if not redis_ctx.pubsub_thread.is_alive() and redis_ctx.run_in_thread:
                    redis_ctx.pubsub_thread = redis_ctx.redis_pubsub.run_in_thread(sleep_time=0.001,
                                                                                   daemon=True)

    def unsubscribe_channel(self, ns: str, channels: List[str]) -> None:
        channels = self.__add_keys_ns_prefix(ns, channels)
        for channel in channels:
            with _map_to_sdl_exception():
                self.__getClientConn(ns).redis_pubsub.unsubscribe(channel)

    def start_event_listener(self) -> None:
        redis_ctxs = self.__getClientConns()
        for redis_ctx in redis_ctxs:
            if redis_ctx.pubsub_thread.is_alive():
                raise RejectedByBackend("Event loop already started")
            if redis_ctx.redis_pubsub.subscribed and len(redis_ctx.redis_client.pubsub_channels()) > 0:
                redis_ctx.pubsub_thread = redis_ctx.redis_pubsub.run_in_thread(sleep_time=0.001, daemon=True)
            redis_ctx.run_in_thread = True

    def handle_events(self) -> Optional[Tuple[str, List[str]]]:
        if self.next_client_event >= len(self.clients):
            self.next_client_event = 0
        redis_ctx = self.clients[self.next_client_event]
        self.next_client_event += 1
        if redis_ctx.pubsub_thread.is_alive() or redis_ctx.run_in_thread:
            raise RejectedByBackend("Event loop already started")
        try:
            return redis_ctx.redis_pubsub.get_message(ignore_subscribe_messages=True)
        except RuntimeError:
            return None

    def __create_redis_clients(self, config):
        clients = list()
        cfg_params = config.get_params()
        for i, addr in enumerate(cfg_params.db_cluster_addrs):
            port = cfg_params.db_ports[i] if i < len(cfg_params.db_ports) else ""
            sport = cfg_params.db_sentinel_ports[i] if i < len(cfg_params.db_sentinel_ports) else ""
            name = cfg_params.db_sentinel_master_names[i] if i < len(cfg_params.db_sentinel_master_names) else ""

            client = self.__create_redis_client(addr, port, sport, name)
            clients.append(client)
        return clients

    def __create_redis_client(self, addr, port, sentinel_port, master_name):
        new_sentinel = None
        new_redis = None
        if len(sentinel_port) == 0:
            new_redis = Redis(host=addr, port=port, db=0, max_connections=20)
        else:
            sentinel_node = (addr, sentinel_port)
            new_sentinel = Sentinel([sentinel_node])
            new_redis = new_sentinel.master_for(master_name)

        new_redis.set_response_callback('SETIE', lambda r: r and str_if_bytes(r) == 'OK' or False)
        new_redis.set_response_callback('DELIE', lambda r: r and int(r) == 1 or False)

        redis_pubsub = PubSub(self.event_separator, new_redis.connection_pool, ignore_subscribe_messages=True)
        pubsub_thread = threading.Thread(target=None)
        run_in_thread = False

        return _RedisConn(new_redis, redis_pubsub, pubsub_thread, run_in_thread)

    def __getClientConns(self):
        return self.clients

    def __getClientConn(self, ns):
        clients_cnt = len(self.clients)
        client_id = self.__get_hash(ns) % clients_cnt
        return self.clients[client_id]

    def __getClient(self, ns):
        clients_cnt = len(self.clients)
        client_id = 0
        if clients_cnt > 1:
            client_id = self.__get_hash(ns) % clients_cnt
        return self.clients[client_id].redis_client

    @classmethod
    def __get_hash(cls, str):
        return zlib.crc32(str.encode())

    @classmethod
    def __add_key_ns_prefix(cls, ns: str, key: str):
        return '{' + ns + '},' + key

    @classmethod
    def __add_keys_ns_prefix(cls, ns: str, keylist: List[str]) -> List[str]:
        ret_nskeys = []
        for k in keylist:
            ret_nskeys.append('{' + ns + '},' + k)
        return ret_nskeys

    @classmethod
    def __add_data_map_ns_prefix(cls, ns: str, data_dict: Dict[str, bytes]) -> Dict[str, bytes]:
        ret_nsdict = {}
        for key, val in data_dict.items():
            ret_nsdict['{' + ns + '},' + key] = val
        return ret_nsdict

    @classmethod
    def __strip_ns_from_bin_keys(cls, ns: str, nskeylist: List[bytes]) -> List[str]:
        ret_keys = []
        for k in nskeylist:
            try:
                redis_key = k.decode("utf-8")
            except UnicodeDecodeError as exc:
                msg = u'Namespace %s key conversion to string failed: %s' % (ns, str(exc))
                raise RejectedByBackend(msg)
            nskey = redis_key.split(',', 1)
            if len(nskey) != 2:
                msg = u'Namespace %s key:%s has no namespace prefix' % (ns, redis_key)
                raise RejectedByBackend(msg)
            ret_keys.append(nskey[1])
        return ret_keys

    def _prepare_channels(self, ns: str,
                          channels_and_events: Dict[str, List[str]]) -> Tuple[List, int]:
        channels_and_events_prepared = []
        for channel, events in channels_and_events.items():
            one_channel_join_events = None
            for event in events:
                if one_channel_join_events is None:
                    channels_and_events_prepared.append(self.__add_key_ns_prefix(ns, channel))
                    one_channel_join_events = event
                else:
                    one_channel_join_events = one_channel_join_events + self.event_separator + event
            channels_and_events_prepared.append(one_channel_join_events)
        pairs_cnt = int(len(channels_and_events_prepared) / 2)
        return channels_and_events_prepared, pairs_cnt

    def get_redis_connection(self, ns: str):
        """Return existing Redis database connection valid for the namespace."""
        return self.__getClient(ns)


class _RedisConn:
    """
    Internal class container to hold redis client connection
    """

    def __init__(self, redis_client, pubsub, pubsub_thread, run_in_thread):
        self.redis_client = redis_client
        self.redis_pubsub = pubsub
        self.pubsub_thread = pubsub_thread
        self.run_in_thread = run_in_thread

    def __str__(self):
        return str(
            {
                "Client": repr(self.redis_client),
                "Subscrions": self.redis_pubsub.subscribed,
                "PubSub thread": repr(self.pubsub_thread),
                "Run in thread": self.run_in_thread,
            }
        )


class RedisBackendLock(DbBackendLockAbc):
    """
    A class providing an implementation of database backend lock of Shared Data Layer (SDL), when
    backend database solution is Redis.

    Args:
        ns (str): Namespace under which this lock is targeted.
        name (str): Lock name, identifies the lock key in a Redis database backend.
        expiration (int, float): Lock expiration time after which the lock is removed if it hasn't
                                 been released earlier by a 'release' method.
        redis_backend (RedisBackend): Database backend object containing connection to Redis
                                      database.
    """
    lua_get_validity_time = None
    # KEYS[1] - lock name
    # ARGS[1] - token
    # return < 0 in case of failure, otherwise return lock validity time in milliseconds.
    LUA_GET_VALIDITY_TIME_SCRIPT = """
        local token = redis.call('get', KEYS[1])
        if not token then
            return -10
        end
        if token ~= ARGV[1] then
            return -11
        end
        return redis.call('pttl', KEYS[1])
    """

    def __init__(self, ns: str, name: str, expiration: Union[int, float],
                 redis_backend: RedisBackend) -> None:
        super().__init__(ns, name)
        self.__redis = redis_backend.get_redis_connection(ns)
        with _map_to_sdl_exception():
            redis_lockname = '{' + ns + '},' + self._lock_name
            self.__redis_lock = Lock(redis=self.__redis, name=redis_lockname, timeout=expiration)
            self._register_scripts()

    def __str__(self):
        return str(
            {
                "lock DB type": "Redis",
                "lock namespace": self._ns,
                "lock name": self._lock_name,
                "lock status": self._lock_status_to_string()
            }
        )

    def acquire(self, retry_interval: Union[int, float] = 0.1,
                retry_timeout: Union[int, float] = 10) -> bool:
        succeeded = False
        self.__redis_lock.sleep = retry_interval
        with _map_to_sdl_exception():
            succeeded = self.__redis_lock.acquire(blocking_timeout=retry_timeout)
        return succeeded

    def release(self) -> None:
        with _map_to_sdl_exception():
            self.__redis_lock.release()

    def refresh(self) -> None:
        with _map_to_sdl_exception():
            self.__redis_lock.reacquire()

    def get_validity_time(self) -> Union[int, float]:
        validity = 0
        if self.__redis_lock.local.token is None:
            msg = u'Cannot get validity time of an unlocked lock %s' % self._lock_name
            raise RejectedByBackend(msg)

        with _map_to_sdl_exception():
            validity = self.lua_get_validity_time(keys=[self.__redis_lock.name],
                                                  args=[self.__redis_lock.local.token],
                                                  client=self.__redis)
        if validity < 0:
            msg = (u'Getting validity time of a lock %s failed with error code: %d'
                   % (self._lock_name, validity))
            raise RejectedByBackend(msg)
        ftime = validity / 1000.0
        if ftime.is_integer():
            return int(ftime)
        return ftime

    def _register_scripts(self):
        cls = self.__class__
        client = self.__redis
        if cls.lua_get_validity_time is None:
            cls.lua_get_validity_time = client.register_script(cls.LUA_GET_VALIDITY_TIME_SCRIPT)

    def _lock_status_to_string(self) -> str:
        try:
            if self.__redis_lock.locked():
                if self.__redis_lock.owned():
                    return 'locked'
                return 'locked by someone else'
            return 'unlocked'
        except redis_exceptions.RedisError as exc:
            return f'Error: {str(exc)}'
