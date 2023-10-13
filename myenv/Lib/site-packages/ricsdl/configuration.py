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


"""The module provides implementation of Shared Data Layer (SDL) configurability."""
import os
from enum import Enum
from collections import namedtuple


class DbBackendType(Enum):
    """Enumeration class of supported SDL database backend types."""
    REDIS = 1
    FAKE_DICT = 2


class _Configuration():
    """This class implements Shared Data Layer (SDL) configurability."""
    Params = namedtuple('Params', ['db_host', 'db_ports', 'db_sentinel_ports',
                                   'db_sentinel_master_names',
                                   'db_cluster_addrs', 'db_type'])

    def __init__(self, fake_db_backend):
        self.params = self._read_configuration(fake_db_backend)

    def __str__(self):
        return str(
            {
                "DB host": self.params.db_host,
                "DB ports": self.params.db_ports,
                "DB master sentinels": self.params.db_sentinel_master_names,
                "DB sentinel ports": self.params.db_sentinel_ports,
                "DB cluster addresses": self.params.db_cluster_addrs,
                "DB type": self.params.db_type.name,
            }
        )

    def get_params(self):
        """Return SDL configuration."""
        return self.params

    @classmethod
    def _read_configuration(cls, fake_db_backend):
        backend_type = DbBackendType.REDIS
        if fake_db_backend:
            if fake_db_backend.lower() != 'dict':
                msg = ("Configuration error: "
                       "SDL instance was initiated with wrong "
                       "'fake_db_backend' argument value: {}. "
                       "Value 'dict' is only supported.".
                       format(fake_db_backend))
                raise ValueError(msg)

            backend_type = DbBackendType.FAKE_DICT
        host = os.getenv('DBAAS_SERVICE_HOST', "")

        port_env = os.getenv('DBAAS_SERVICE_PORT')
        ports = port_env.split(",") if port_env is not None else list()

        sentinel_port_env = os.getenv('DBAAS_SERVICE_SENTINEL_PORT')
        sentinel_ports = sentinel_port_env.split(",") if sentinel_port_env is not None else list()

        sentinel_name_env = os.getenv('DBAAS_MASTER_NAME')
        sentinel_names = sentinel_name_env.split(",") if sentinel_name_env is not None else list()

        addr_env = os.getenv('DBAAS_CLUSTER_ADDR_LIST')
        addrs = addr_env.split(",") if addr_env is not None else list()

        if len(addrs) == 0 and len(host) > 0:
            addrs.append(host)

        addrs, ports, sentinel_ports, sentinel_names = cls._complete_configuration(
            addrs, ports, sentinel_ports, sentinel_names)

        return _Configuration.Params(db_host=host,
                                     db_ports=ports,
                                     db_sentinel_ports=sentinel_ports,
                                     db_sentinel_master_names=sentinel_names,
                                     db_cluster_addrs=addrs,
                                     db_type=backend_type)

    @classmethod
    def _complete_configuration(cls, addrs, ports, sentinel_ports, sentinel_names):
        if len(sentinel_ports) == 0:
            if len(addrs) > len(ports) and len(ports) > 0:
                for i in range(len(ports), len(addrs)):
                    ports.append(ports[i - 1])
        else:
            if len(addrs) > len(sentinel_ports):
                for i in range(len(sentinel_ports), len(addrs)):
                    sentinel_ports.append(sentinel_ports[i - 1])
            if len(addrs) > len(sentinel_names) and len(sentinel_names) > 0:
                for i in range(len(sentinel_names), len(addrs)):
                    sentinel_names.append(sentinel_names[i - 1])
        return addrs, ports, sentinel_ports, sentinel_names

    @classmethod
    def get_event_separator(cls):
        return "___"
