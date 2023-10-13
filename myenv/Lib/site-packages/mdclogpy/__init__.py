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
"""Structured logging library with Mapped Diagnostic Context

Outputs the log entries to standard out in structured format, json currently.
Severity based filtering.
Supports Mapped Diagnostic Context (MDC).

Set MDC pairs are automatically added to log entries by the library.
"""

from .Logger import Logger
from .Logger import Level
from .Logger import Value


_root_logger = Logger()


def log(level: Level, message: str):
    """Log a message."""
    _root_logger.log(level, message)


def mdclog_format_init(configmap_monitor=False):
    _root_logger.mdclog_format_init(configmap_monitor)    


def error(message: str):
    """Log an error message. Equals to log(ERROR, msg)."""
    _root_logger.log(Level.ERROR, message)


def warning(message: str):
    """Log a warning message. Equals to log(WARNING, msg)."""
    _root_logger.log(Level.WARNING, message)


def info(message: str):
    """Log an info message. Equals to log(INFO, msg)."""
    _root_logger.log(Level.INFO, message)


def debug(message: str):
    """Log a debug message. Equals to log(DEBUG, msg)."""
    _root_logger.log(Level.DEBUG, message)


def set_level(level: Level):
    """Set current logging level."""
    _root_logger.set_level(level)


def get_level() -> Level:
    """Return the current logging level."""
    return _root_logger.get_level()


def add_mdc(key: str, value: Value):
    """Add an MDC to the root logger."""
    _root_logger.add_mdc(key, value)


def get_mdc(key: str) -> Value:
    """Return root logger's MDC with the given key or None."""
    return _root_logger.get_mdc(key)


def remove_mdc(key: str):
    """Remove root logger's MDC with the given key."""
    _root_logger.remove_mdc(key)


def clean_mdc():
    """Remove all MDCs from the root logger."""
    _root_logger.clean_mdc()
