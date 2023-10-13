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


"""Shared Data Layer (SDL) database backend module."""

from importlib import import_module
from ricsdl.configuration import DbBackendType


def get_backend_instance(configuration):
    """
    Select database backend solution and return and instance of it.
    """
    if configuration.get_params().db_type == DbBackendType.FAKE_DICT:
        backend_name = 'FakeDictBackend'
        backend_module_name = 'fake_dict_db'
    else:
        backend_name = 'RedisBackend'
        backend_module_name = 'redis'

    package = __package__ or __name__
    backend_module = import_module('.' + backend_module_name, package=package)
    backend_class = getattr(backend_module, backend_name)
    instance = backend_class(configuration)
    return instance


def get_backend_lock_instance(configuration, ns, name, expiration, backend):
    """
    Select database backend lock solution and return and instance of it.
    """
    if configuration.get_params().db_type == DbBackendType.FAKE_DICT:
        backend_lock_name = 'FakeDictBackendLock'
        backend_module_name = 'fake_dict_db'
    else:
        backend_lock_name = 'RedisBackendLock'
        backend_module_name = 'redis'

    package = __package__ or __name__
    backend_module = import_module('.' + backend_module_name, package=package)
    backend_lock_class = getattr(backend_module, backend_lock_name)
    instance = backend_lock_class(ns, name, expiration, backend)
    return instance
