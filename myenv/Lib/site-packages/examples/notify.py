# Copyright (c) 2020 Samsung Electronics
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

"""Examples on how to use Shared Data Layer (SDL) notification feature.

Execution of  these examples requires:
 * Following Redis extension commands have been installed to runtime environment:
   - MSETPUB
   - SETIE
   - SETIEMPUB
   - SETNXMPUB
   - DELMPUB
   - DELIE
   - DELIEMPUB
   Redis v4.0 or greater is required. Older versions do not support extension modules.
   Implementation of above commands is produced by RIC DBaaS:
   https://gerrit.o-ran-sc.org/r/admin/repos/ric-plt/dbaas
   In official RIC deployments these commands are installed by `dbaas` service to Redis
   container(s).
   In development environment you may want install commands manually to pod/container, which is
   running Redis.
 * Following environment variables are needed to set to the pod/container where the application
   utilizing SDL is going to be run.
     DBAAS_SERVICE_HOST = [DB service address]
     DBAAS_SERVICE_PORT= [Comma separated list of DB service ports]. Only one port supported in
     RIC deployments, Nokia SEP deployments can have multiple ports.
     DBAAS_MASTER_NAME = [Comma separated list of DB names]. Needed to set only if Redis
     sentinel is used to provide high availability for Redis DB solution. Only one DB name
     supported in RIC deployments, Nokia SEP deployments can have multiple DB names.
     DBAAS_SERVICE_SENTINEL_PORT = [Comma separated list of Redis sentinel port number]. Needed
     to set only if Redis sentinel is in use. Only one port supported in RIC deployments, Nokia
     SEP deployments can have multiple ports.
     DBASS_CLUSTER_ADDR_LIST = [Comma separated list of DB service addresses]. Is set only if
     more than one Redis sentinel groups are in use. Only in use in Nokia SEP deployments.
   In official RIC deployments four first environment variables are defined in Helm configMaps
   of the DBaaS and these configurations can be loaded automatically as environment variables
   into application pods via `envFrom dbaas-appconfig` statement in an application Helm Charts.
   The last environment variable is not for time being in use in official RIC deployments, only
   in Nokia SEP deployments.
"""

import threading
import time

from ricsdl.syncstorage import SyncStorage
from ricsdl.exceptions import RejectedByBackend, NotConnected, BackendError
from typing import (Union, List)

# There are two available methods for applications to handle notifications:
#   - EVENT_LISTENER (true):
#     - User calls sdl.start_event_listener() which will create an SDL managed
#       event loop for handling messages.
#   - EVENT_LISTENER (false):
#     - User need to call sdl.handle_events() which will return the message
#
# Note: In both cases, the given callback function will be executed.
EVENT_LISTENER = True

# Constants used in the examples below.
MY_NS = 'my_ns'
MY_CHANNEL = "my_channel"
MY_LOCK = threading.Lock()


def _try_func_return(func):
    """
    Generic wrapper function to call SDL API function and handle exceptions if they are raised.
    """
    try:
        return func()
    except RejectedByBackend as exp:
        print(f'SDL function {func.__name__} failed: {str(exp)}')
        # Permanent failure, just forward the exception
        raise
    except (NotConnected, BackendError) as exp:
        print(f'SDL function {func.__name__} failed for a temporal error: {str(exp)}')
        # Here we could have a retry logic


def _try_func_callback_return(func):
    """Generic wrapper function for testing SDL APIs with callback functions.

    threading.Lock is unlocked in the callback function and threading.Lock is
    only used to demonstrate that the callback function was called.
    """
    global MY_LOCK
    MY_LOCK.acquire()
    ret = _try_func_return(func)
    while MY_LOCK.locked():
        time.sleep(0.01)
    return ret


# Creates SDL instance. The call creates connection to the SDL database backend.
mysdl = _try_func_return(SyncStorage)

# Stores the last received channel and message
last_cb_channel = ""
last_cb_message = ""

# Allows program to stop receive thread at the end of execution
stop_thread = False


def cb(channel: str, message: List[str]):
    """An example of function that will be called when an event list is received.

    This function sets last_cb_channel and last_cb_message as channel and
    message respectively. This also unlocks the global lock variable.

    Args:
        channel: Channel where the message was received
        message: Received message
    """
    global last_cb_channel, last_cb_message, MY_LOCK
    last_cb_channel = channel
    last_cb_message = message
    if MY_LOCK.locked():
        MY_LOCK.release()


def listen_thread():
    """An example of a listener thread that continuously calls sdl.handle_events()."""
    global mysdl
    global stop_thread
    while not stop_thread:
        message = mysdl.handle_events()
        if message:
            # You could process message here
            pass
        time.sleep(0.001)

# Subscribe to MY_CHANNEL. We expect that anytime we receive a message in the
# channel, cb function will be called.
_try_func_return(lambda: mysdl.subscribe_channel(MY_NS, cb, MY_CHANNEL))

# As mentioned above, there are two available methods for applications to
# handle notifications
if EVENT_LISTENER:
    _try_func_return(mysdl.start_event_listener)
else:
    thread = threading.Thread(target=listen_thread)
    thread.start()

# Sets a value 'my_value' for a key 'my_key' under given namespace. Note that value
# type must be bytes and multiple key values can be set in one set function call.
_try_func_callback_return(
    lambda: mysdl.set_and_publish(MY_NS, {MY_CHANNEL: "SET PUBLISH"}, {'my_key': b'my_value'}))
assert last_cb_channel == MY_CHANNEL and last_cb_message[0] == "SET PUBLISH"

# Sets a value 'my_value' for a key 'my_key' under given namespace. Note that value
# type must be bytes and multiple key values can be set in one set function call.
# Function publishes two events into one channel.
_try_func_callback_return(
    lambda: mysdl.set_and_publish(MY_NS, {MY_CHANNEL: ["SET PUBLISH1", "SET PUBLISH2"]}, {'my_key': b'my_value'}))
assert last_cb_channel == MY_CHANNEL and last_cb_message == ["SET PUBLISH1", "SET PUBLISH2"]

# Sets a value 'my_value2' for a key 'my_key' under given namespace only if the old value is
# 'my_value'.
was_set = _try_func_callback_return(lambda: mysdl.set_if_and_publish(
    MY_NS, {MY_CHANNEL: "SET IF PUBLISH"}, 'my_key', b'my_value', b'my_value2'))
assert was_set is True
assert last_cb_channel == MY_CHANNEL and last_cb_message[0] == "SET IF PUBLISH"
# Try again. This time value 'my_value2' won't be set, because the key has already 'my_value2'
# value. Callback function will not be called here.
was_set = _try_func_return(lambda: mysdl.set_if_and_publish(MY_NS, {MY_CHANNEL: "SET IF PUBLISH"},
                                                            'my_key', b'my_value', b'my_value2'))
assert was_set is False

# Sets a value 'my_value' for a key 'my_key2' under given namespace only if the key doesn't exist.
# Note that value types must be bytes.
was_set = _try_func_callback_return(lambda: mysdl.set_if_not_exists_and_publish(
    MY_NS, {MY_CHANNEL: "SET IF NOT PUBLISH"}, 'my_key2', b'my_value'))
assert was_set is True
assert last_cb_channel == MY_CHANNEL and last_cb_message[0] == "SET IF NOT PUBLISH"
# Try again. This time the key 'my_key2' already exists. Callback function will not be called here.
was_set = _try_func_return(lambda: mysdl.set_if_not_exists_and_publish(
    MY_NS, {MY_CHANNEL: "SET IF NOT PUBLISH"}, 'my_key2', b'my_value'))
assert was_set is False

# Removes a key 'my_key' under given namespace.
_try_func_callback_return(
    lambda: mysdl.remove_and_publish(MY_NS, {MY_CHANNEL: "REMOVE PUBLISH"}, 'my_key'))
my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, 'my_key'))
assert my_ret_dict == {}
assert last_cb_channel == MY_CHANNEL and last_cb_message[0] == "REMOVE PUBLISH"

# Removes a key 'my_key' under given namespace only if the old value is 'my_value'.
was_removed = _try_func_callback_return(lambda: mysdl.remove_if_and_publish(
    MY_NS, {MY_CHANNEL: "REMOVE IF PUBLISH"}, 'my_key2', b'my_value'))
assert was_removed is True
assert last_cb_channel == MY_CHANNEL and last_cb_message[0] == "REMOVE IF PUBLISH"
# Try again to remove not anymore existing key 'my_key'. Callback function will not be called here.
was_removed = _try_func_return(lambda: mysdl.remove_if_and_publish(
    MY_NS, {MY_CHANNEL: "REMOVE IF PUBLISH"}, 'my_key2', b'my_value'))
assert was_removed is False

# Removes all the keys under given namespace.
_try_func_return(lambda: mysdl.set(MY_NS, {'my_key': b'something'}))
my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {'my_key'}))
assert my_ret_dict != {}

_try_func_callback_return(
    lambda: mysdl.remove_all_and_publish(MY_NS, {MY_CHANNEL: "REMOVE ALL PUBLISH"}))
my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {'my_key'}))
assert my_ret_dict == {}
assert last_cb_channel == MY_CHANNEL and last_cb_message[0] == "REMOVE ALL PUBLISH"

stop_thread = True
mysdl.close()
