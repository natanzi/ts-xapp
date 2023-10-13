# Copyright (c) 2019 AT&T Intellectual Property.
# Copyright (c) 2018-2019 Nokia.
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


"""The module provides Shared Data Layer (SDL) database backend interface."""

from typing import (Callable, Dict, Set, List, Optional, Tuple, Union)
from abc import ABC, abstractmethod


class DbBackendAbc(ABC):
    """An abstract Shared Data Layer (SDL) class providing database backend interface."""

    @abstractmethod
    def is_connected(self):
        """Test database backend connection."""
        pass

    @abstractmethod
    def close(self):
        """Close database backend connection."""
        pass

    @abstractmethod
    def set(self, ns: str, data_map: Dict[str, bytes]) -> None:
        """Write key value data mapping to database under a namespace."""
        pass

    @abstractmethod
    def set_if(self, ns: str, key: str, old_data: bytes, new_data: bytes) -> bool:
        """"Write key value to database under a namespace if the old value is expected one."""
        pass

    @abstractmethod
    def set_if_not_exists(self, ns: str, key: str, data: bytes) -> bool:
        """"Write key value to database under a namespace if key doesn't exist."""
        pass

    @abstractmethod
    def get(self, ns: str, keys: List[str]) -> Dict[str, bytes]:
        """"Return values of the keys under a namespace."""
        pass

    @abstractmethod
    def find_keys(self, ns: str, key_pattern: str) -> List[str]:
        """"Return all the keys matching search pattern under a namespace in database."""
        pass

    @abstractmethod
    def find_and_get(self, ns: str, key_pattern: str) -> Dict[str, bytes]:
        """
        Return all the keys with their values matching search pattern under a namespace in
        database.
        """
        pass

    @abstractmethod
    def remove(self, ns: str, keys: List[str]) -> None:
        """Remove keys and their data from database."""
        pass

    @abstractmethod
    def remove_if(self, ns: str, key: str, data: bytes) -> bool:
        """
           Remove key and its data from database if if the current data value is expected
           one.
        """
        pass

    @abstractmethod
    def add_member(self, ns: str, group: str, members: Set[bytes]) -> None:
        """Add new members to a group under a namespace in database."""
        pass

    @abstractmethod
    def remove_member(self, ns: str, group: str, members: Set[bytes]) -> None:
        """Remove members from a group under a namespace in database."""
        pass

    @abstractmethod
    def remove_group(self, ns: str, group: str) -> None:
        """Remove a group under a namespace in database along with it's members."""
        pass

    @abstractmethod
    def get_members(self, ns: str, group: str) -> Set[bytes]:
        """Get all the members of a group under a namespace in database."""
        pass

    @abstractmethod
    def is_member(self, ns: str, group: str, member: bytes) -> bool:
        """Validate if a given member is in the group under a namespace in database."""
        pass

    @abstractmethod
    def group_size(self, ns: str, group: str) -> int:
        """Return the number of members in a group under a namespace in database."""
        pass

    @abstractmethod
    def set_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]],
                        data_map: Dict[str, bytes]) -> None:
        """Publish event to channel after writing data."""
        pass

    @abstractmethod
    def set_if_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]], key: str,
                           old_data: bytes, new_data: bytes) -> bool:
        """
        Publish event to channel after writing key value to database under a namespace
        if the old value is expected one.
        """
        pass

    @abstractmethod
    def set_if_not_exists_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]],
                                      key: str, data: bytes) -> bool:
        """"
        Publish event to channel after writing key value to database under a namespace if
        key doesn't exist.
        """
        pass

    @abstractmethod
    def remove_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]],
                           keys: List[str]) -> None:
        """Publish event to channel after removing data."""
        pass

    @abstractmethod
    def remove_if_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]], key: str,
                              data: bytes) -> bool:
        """
        Publish event to channel after removing key and its data from database if the
        current data value is expected one.
        """
        pass

    @abstractmethod
    def remove_all_and_publish(self, ns: str, channels_and_events: Dict[str, List[str]]) -> None:
        """
        Publish event to channel after removing all keys in namespace.
        """
        pass

    @abstractmethod
    def subscribe_channel(self, ns: str, cb: Callable[[str, List[str]], None],
                          channels: List[str]) -> None:
        """
        This takes a callback function and one or many channels to be subscribed.
        When an event is received for the given channel, the given callback function
        shall be called with channel and notification(s) as parameter.
        """
        pass

    @abstractmethod
    def unsubscribe_channel(self, ns: str, channels: List[str]) -> None:
        """Unsubscribes from channel and removes set callback function."""
        pass

    @abstractmethod
    def start_event_listener(self) -> None:
        """
        start_event_listener creates an event loop in a separate thread for handling
        notifications from subscriptions.
        """
        pass

    @abstractmethod
    def handle_events(self) -> Optional[Tuple[str, List[str]]]:
        """
        handle_events is a non-blocking function that returns a tuple containing channel
        name and message(s) received from notification.
        """
        pass


class DbBackendLockAbc(ABC):
    """
    An abstract Shared Data Layer (SDL) class providing database backend lock interface.
    Args:
        ns (str): Namespace under which this lock is targeted.
        name (str): Lock name, identifies the lock key in a database backend.
    """
    def __init__(self, ns: str, name: str) -> None:
        self._ns = ns
        self._lock_name = name
        super().__init__()

    @abstractmethod
    def acquire(self, retry_interval: Union[int, float] = 0.1,
                retry_timeout: Union[int, float] = 10) -> bool:
        """Acquire a database lock."""
        pass

    @abstractmethod
    def release(self) -> None:
        """Release a database lock."""
        pass

    @abstractmethod
    def refresh(self) -> None:
        """Refresh the remaining validity time of the database lock back to a initial value."""
        pass

    @abstractmethod
    def get_validity_time(self) -> Union[int, float]:
        """Return remaining validity time of the lock in seconds."""
        pass
