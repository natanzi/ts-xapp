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

"""The module provides implementation of the syncronous Shared Data Layer (SDL) interface."""
import builtins
import inspect
from typing import (Any, Callable, Dict, Set, List, Optional, Tuple, Union)
from ricsdl.configuration import _Configuration
from ricsdl.syncstorage_abc import (SyncStorageAbc, SyncLockAbc)
import ricsdl.backend
from ricsdl.backend.dbbackend_abc import DbBackendAbc
from ricsdl.exceptions import (SdlException, SdlTypeError)


def func_arg_checker(exception, start_arg_idx, **types):
    """Decorator to validate function arguments."""
    def _check(func):
        if not __debug__:
            return func

        def _validate(*args, **kwds):
            for idx, arg in enumerate(args[start_arg_idx:], start_arg_idx):
                if func.__code__.co_varnames[idx] in types and \
                        not isinstance(arg, types[func.__code__.co_varnames[idx]]):
                    raise exception(r"Wrong argument type: '{}'={}. Must be: {}".
                                    format(func.__code__.co_varnames[idx], type(arg),
                                           types[func.__code__.co_varnames[idx]]))
            for kwdname, kwdval in kwds.items():
                if kwdname in types and not isinstance(kwdval, types[kwdname]):
                    raise exception(r"Wrong argument type: '{}'={}. Must be: {}".
                                    format(kwdname, type(kwdval), types[kwdname]))
            return func(*args, **kwds)
        _validate.__name__ = func.__name__
        return _validate
    return _check


class SyncLock(SyncLockAbc):
    """
    This class implements Shared Data Layer (SDL) abstract 'SyncLockAbc' class.

    A lock instance is created per namespace and it is identified by its `name` within a namespace.

    Args:
        ns (str): Namespace under which this lock is targeted.
        name (str): Lock name, identifies the lock key in SDL storage.
        expiration (int, float): Lock expiration time after which the lock is removed if it hasn't
                                 been released earlier by a 'release' method.
        storage (SyncStorage): Database backend object containing connection to a database.
    """
    @func_arg_checker(SdlTypeError, 1, ns=str, name=str, expiration=(int, float))
    def __init__(self, ns: str, name: str, expiration: Union[int, float],
                 storage: 'SyncStorage') -> None:

        super().__init__(ns, name, expiration)
        self.__configuration = storage.get_configuration()
        self.__dbbackendlock = ricsdl.backend.get_backend_lock_instance(self.__configuration,
                                                                        ns, name, expiration,
                                                                        storage.get_backend())

    def __str__(self):
        return str(
            {
                "namespace": self._ns,
                "name": self._name,
                "expiration": self._expiration,
                "backend lock": str(self.__dbbackendlock)
            }
        )

    @func_arg_checker(SdlTypeError, 1, retry_interval=(int, float),
                      retry_timeout=(int, float))
    def acquire(self, retry_interval: Union[int, float] = 0.1,
                retry_timeout: Union[int, float] = 10) -> bool:
        return self.__dbbackendlock.acquire(retry_interval, retry_timeout)

    def release(self) -> None:
        self.__dbbackendlock.release()

    def refresh(self) -> None:
        self.__dbbackendlock.refresh()

    def get_validity_time(self) -> Union[int, float]:
        return self.__dbbackendlock.get_validity_time()


class SyncStorage(SyncStorageAbc):
    """
    This class implements Shared Data Layer (SDL) abstract 'SyncStorageAbc' class.

    This class provides synchronous access to all the namespaces in SDL storage.
    Data can be written, read and removed based on keys known to clients. Keys are unique within
    a namespace, namespace identifier is passed as a parameter to all the operations.

    Args:
        fake_db_backend (str): Optional parameter. Parameter enables fake DB backend usage for an
                               SDL instance. Fake DB backend is ONLY allowed to use for testing
                               purposes at development phase of SDL clients when more advanced
                               database services are not necessarily needed. Currently value 'dict'
                               is only allowed value for the parameter, which enables dictionary
                               type of fake DB backend.
    """
    def __init__(self, fake_db_backend=None) -> None:
        super().__init__()
        self.__dbbackend = None
        self.__configuration = _Configuration(fake_db_backend)
        self.event_separator = self.__configuration.get_event_separator()
        self.__dbbackend = ricsdl.backend.get_backend_instance(self.__configuration)

    def __del__(self):
        self.close()

    def __str__(self):
        return str(
            {
                "configuration": str(self.__configuration),
                "backend": str(self.__dbbackend)
            }
        )

    def is_active(self):
        try:
            return self.__dbbackend.is_connected()
        except SdlException:
            return False

    def close(self):
        if self.__dbbackend:
            self.__dbbackend.close()

    @func_arg_checker(SdlTypeError, 1, ns=str, data_map=dict)
    def set(self, ns: str, data_map: Dict[str, bytes]) -> None:
        self._validate_key_value_dict(data_map)
        self.__dbbackend.set(ns, data_map)

    @func_arg_checker(SdlTypeError, 1, ns=str, key=str, old_data=bytes, new_data=bytes)
    def set_if(self, ns: str, key: str, old_data: bytes, new_data: bytes) -> bool:
        return self.__dbbackend.set_if(ns, key, old_data, new_data)

    @func_arg_checker(SdlTypeError, 1, ns=str, key=str, data=bytes)
    def set_if_not_exists(self, ns: str, key: str, data: bytes) -> bool:
        return self.__dbbackend.set_if_not_exists(ns, key, data)

    @func_arg_checker(SdlTypeError, 1, ns=str, keys=(str, builtins.set))
    def get(self, ns: str, keys: Union[str, Set[str]]) -> Dict[str, bytes]:
        disordered = self.__dbbackend.get(ns, list(keys))
        return {k: disordered[k] for k in sorted(disordered)}

    @func_arg_checker(SdlTypeError, 1, ns=str, key_pattern=str)
    def find_keys(self, ns: str, key_pattern: str) -> List[str]:
        return self.__dbbackend.find_keys(ns, key_pattern)

    @func_arg_checker(SdlTypeError, 1, ns=str, key_pattern=str)
    def find_and_get(self, ns: str, key_pattern: str) -> Dict[str, bytes]:
        disordered = self.__dbbackend.find_and_get(ns, key_pattern)
        return {k: disordered[k] for k in sorted(disordered)}

    @func_arg_checker(SdlTypeError, 1, ns=str, keys=(str, builtins.set))
    def remove(self, ns: str, keys: Union[str, Set[str]]) -> None:
        self.__dbbackend.remove(ns, list(keys))

    @func_arg_checker(SdlTypeError, 1, ns=str, key=str, data=bytes)
    def remove_if(self, ns: str, key: str, data: bytes) -> bool:
        return self.__dbbackend.remove_if(ns, key, data)

    @func_arg_checker(SdlTypeError, 1, ns=str)
    def remove_all(self, ns: str) -> None:
        keys = self.__dbbackend.find_keys(ns, '*')
        if keys:
            self.__dbbackend.remove(ns, keys)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str, members=(bytes, builtins.set))
    def add_member(self, ns: str, group: str, members: Union[bytes, Set[bytes]]) -> None:
        self.__dbbackend.add_member(ns, group, members)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str, members=(bytes, builtins.set))
    def remove_member(self, ns: str, group: str, members: Union[bytes, Set[bytes]]) -> None:
        self.__dbbackend.remove_member(ns, group, members)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str)
    def remove_group(self, ns: str, group: str) -> None:
        self.__dbbackend.remove_group(ns, group)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str)
    def get_members(self, ns: str, group: str) -> Set[bytes]:
        return self.__dbbackend.get_members(ns, group)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str, member=bytes)
    def is_member(self, ns: str, group: str, member: bytes) -> bool:
        return self.__dbbackend.is_member(ns, group, member)

    @func_arg_checker(SdlTypeError, 1, ns=str, group=str)
    def group_size(self, ns: str, group: str) -> int:
        return self.__dbbackend.group_size(ns, group)

    @func_arg_checker(SdlTypeError, 1, ns=str, channels_and_events=dict, data_map=dict)
    def set_and_publish(self, ns: str, channels_and_events: Dict[str, Union[str, List[str]]],
                        data_map: Dict[str, bytes]) -> None:
        self._validate_key_value_dict(data_map)
        self._validate_channels_events(channels_and_events)
        for channel, events in channels_and_events.items():
            channels_and_events[channel] = [events] if isinstance(events, str) else events
        self.__dbbackend.set_and_publish(ns, channels_and_events, data_map)

    @func_arg_checker(SdlTypeError,
                      1,
                      ns=str,
                      channels_and_events=dict,
                      key=str,
                      old_data=bytes,
                      new_data=bytes)
    def set_if_and_publish(self, ns: str, channels_and_events: Dict[str, Union[str, List[str]]],
                           key: str, old_data: bytes, new_data: bytes) -> bool:
        self._validate_channels_events(channels_and_events)
        for channel, events in channels_and_events.items():
            channels_and_events[channel] = [events] if isinstance(events, str) else events
        return self.__dbbackend.set_if_and_publish(ns, channels_and_events, key, old_data, new_data)

    @func_arg_checker(SdlTypeError, 1, ns=str, channels_and_events=dict, key=str, data=bytes)
    def set_if_not_exists_and_publish(self, ns: str,
                                      channels_and_events: Dict[str, Union[str, List[str]]],
                                      key: str, data: bytes) -> bool:
        self._validate_channels_events(channels_and_events)
        for channel, events in channels_and_events.items():
            channels_and_events[channel] = [events] if isinstance(events, str) else events
        return self.__dbbackend.set_if_not_exists_and_publish(ns, channels_and_events, key, data)

    @func_arg_checker(SdlTypeError, 1, ns=str, channels_and_events=dict, keys=(str, builtins.set))
    def remove_and_publish(self, ns: str, channels_and_events: Dict[str, Union[str, List[str]]],
                           keys: Union[str, Set[str]]) -> None:
        self._validate_channels_events(channels_and_events)
        for channel, events in channels_and_events.items():
            channels_and_events[channel] = [events] if isinstance(events, str) else events
        keys = [keys] if isinstance(keys, str) else list(keys)
        self.__dbbackend.remove_and_publish(ns, channels_and_events, keys)

    @func_arg_checker(SdlTypeError, 1, ns=str, channels_and_events=dict, key=str, data=bytes)
    def remove_if_and_publish(self, ns: str, channels_and_events: Dict[str, Union[str, List[str]]],
                              key: str, data: bytes) -> bool:
        self._validate_channels_events(channels_and_events)
        for channel, events in channels_and_events.items():
            channels_and_events[channel] = [events] if isinstance(events, str) else events
        return self.__dbbackend.remove_if_and_publish(ns, channels_and_events, key, data)

    @func_arg_checker(SdlTypeError, 1, ns=str, channels_and_events=dict)
    def remove_all_and_publish(self, ns: str,
                               channels_and_events: Dict[str, Union[str, List[str]]]) -> None:
        self._validate_channels_events(channels_and_events)
        for channel, events in channels_and_events.items():
            channels_and_events[channel] = [events] if isinstance(events, str) else events
        self.__dbbackend.remove_all_and_publish(ns, channels_and_events)

    @func_arg_checker(SdlTypeError, 1, ns=str, cb=Callable, channels=(str, builtins.set))
    def subscribe_channel(self, ns: str, cb: Callable[[str, List[str]], None],
                          channels: Union[str, Set[str]]) -> None:
        self._validate_callback(cb)
        channels = [channels] if isinstance(channels, str) else list(channels)
        self.__dbbackend.subscribe_channel(ns, cb, channels)

    @func_arg_checker(SdlTypeError, 1, ns=str, channels=(str, builtins.set))
    def unsubscribe_channel(self, ns: str, channels: Union[str, Set[str]]) -> None:
        channels = [channels] if isinstance(channels, str) else list(channels)
        self.__dbbackend.unsubscribe_channel(ns, channels)

    def start_event_listener(self) -> None:
        self.__dbbackend.start_event_listener()

    def handle_events(self) -> Optional[Tuple[str, List[str]]]:
        return self.__dbbackend.handle_events()

    @func_arg_checker(SdlTypeError, 1, ns=str, resource=str, expiration=(int, float))
    def get_lock_resource(self, ns: str, resource: str, expiration: Union[int, float]) -> SyncLock:
        return SyncLock(ns, resource, expiration, self)

    def get_backend(self) -> DbBackendAbc:
        """Return backend instance."""
        return self.__dbbackend

    def get_configuration(self) -> _Configuration:
        """Return configuration what was valid when the SDL instance was initiated."""
        return self.__configuration

    @classmethod
    def _validate_key_value_dict(cls, kv):
        for k, v in kv.items():
            if not isinstance(k, str):
                raise SdlTypeError(r"Wrong dict key type: {}={}. Must be: str".format(k, type(k)))
            if not isinstance(v, bytes):
                raise SdlTypeError(r"Wrong dict value type: {}={}. Must be: bytes".format(v, type(v)))

    def _validate_channels_events(self, channels_and_events: Dict[Any, Any]):
        for channel, events in channels_and_events.items():
            if not isinstance(channel, str):
                raise SdlTypeError(r"Wrong channel type: {}={}. Must be: str".format(
                    channel, type(channel)))
            if not isinstance(events, (list, str)):
                raise SdlTypeError(r"Wrong event type: {}={}. Must be: str".format(
                    events, type(events)))
            if isinstance(events, list):
                for event in events:
                    if not isinstance(event, str):
                        raise SdlTypeError(r"Wrong event type: {}={}. Must be: str".format(
                            events, type(events)))
                    if self.event_separator in event:
                        raise SdlTypeError(r"Events {} contains illegal substring (\"{}\")".format(
                            events, self.event_separator))
            else:
                if self.event_separator in events:
                    raise SdlTypeError(r"Events {} contains illegal substring (\"{}\")".format(
                        events, self.event_separator))

    @classmethod
    def _validate_callback(cls, cb):
        param_len = len(inspect.signature(cb).parameters)
        if param_len != 2:
            raise SdlTypeError(
                f"Callback function should take 2 positional argument but {param_len} were given")
