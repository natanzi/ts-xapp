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


"""
Examples how to use synchronous API functions of the Shared Data Layer (SDL).
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
from ricsdl.syncstorage import SyncStorage
from ricsdl.exceptions import RejectedByBackend, NotConnected, BackendError


# Constants used in the examples below.
MY_NS = 'my_ns'
MY_GRP_NS = 'my_group_ns'
MY_LOCK_NS = 'my_group_ns'


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


# Creates SDL instance. The call creates connection to the SDL database backend.
mysdl = _try_func_return(SyncStorage)

# Creates SDL instance what utilizes a fake database backend. Fake database is meant to
# be used only at development phase of SDL clients. It does not provide more advanced
# database services.
# mysdl = _try_func_return(lambda: SyncStorage(fake_db_backend='dict'))

# Checks if SDL is operational. Note that it is not necessary to call `is_active()` after each
# SDL instance creation. Below example is here just to show how to call it spontaneously
# when SDL healthiness is needed to check.
is_active = mysdl.is_active()
assert is_active is True

# Sets a value 'my_value' for a key 'my_key' under given namespace. Note that value
# type must be bytes and multiple key values can be set in one set function call.
_try_func_return(lambda: mysdl.set(MY_NS, {'my_key': b'my_value'}))


# Gets the value of 'my_value' under given namespace.
# Note that the type of returned value is bytes.
my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {'my_key', 'someting not existing'}))
for key, val in my_ret_dict.items():
    assert val.decode("utf-8") == u'my_value'


# Sets a value 'my_value2' for a key 'my_key' under given namespace only if the old value is
# 'my_value'.
# Note that value types must be bytes.
was_set = _try_func_return(lambda: mysdl.set_if(MY_NS, 'my_key', b'my_value', b'my_value2'))
assert was_set is True
# Try again. This time value 'my_value2' won't be set, because the key has already 'my_value2'
# value.
was_set = _try_func_return(lambda: mysdl.set_if(MY_NS, 'my_key', b'my_value', b'my_value2'))
assert was_set is False


# Sets a value 'my_value' for a key 'my_key2' under given namespace only if the key doesn't exist.
# Note that value types must be bytes.
was_set = _try_func_return(lambda: mysdl.set_if_not_exists(MY_NS, 'my_key2', b'my_value'))
assert was_set is True
# Try again. This time the key 'my_key2' already exists.
was_set = _try_func_return(lambda: mysdl.set_if_not_exists(MY_NS, 'my_key2', b'my_value'))
assert was_set is False


# Removes a key 'my_key' under given namespace.
_try_func_return(lambda: mysdl.remove(MY_NS, 'my_key'))
my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, 'my_key'))
assert my_ret_dict == {}


# Removes a key 'my_key' under given namespace only if the old value is 'my_value'.
was_removed = _try_func_return(lambda: mysdl.remove_if(MY_NS, 'my_key2', b'my_value'))
assert was_removed is True
# Try again to remove not anymore existing key 'my_key'.
was_removed = _try_func_return(lambda: mysdl.remove_if(MY_NS, 'my_key2', b'my_value'))
assert was_removed is False


# Removes all the keys under given namespace.
_try_func_return(lambda: mysdl.set(MY_NS, {'my_key': b'something'}))
my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {'my_key'}))
assert my_ret_dict != {}

_try_func_return(lambda: mysdl.remove_all(MY_NS))
my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {'my_key'}))
assert my_ret_dict == {}


# Finds keys under given namespace that are matching to given key prefix 'my_k'.
_try_func_return(lambda: mysdl.set(MY_NS, {'my_key': b'my_value'}))
ret_keys = _try_func_return(lambda: mysdl.find_keys(MY_NS, 'my_k*'))
assert ret_keys == ['my_key']


# Finds keys and their values under given namespace that are matching to given key search
# pattern 'my_k*'.
# Note that the type of returned value is bytes.
ret_key_values = _try_func_return(lambda: mysdl.find_and_get(MY_NS, 'my_k*'))
assert ret_key_values == {'my_key': b'my_value'}

_try_func_return(lambda: mysdl.remove_all(MY_NS))


# Adds a member 'a' to a group 'my_group' under given namespace. A group is a unique collection of
# members.
# Note that member type must be bytes and multiple members can be set in one set function call.
_try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'my_group', {b'a'}))
# Try again to add a member 'a'. This time 'a' won't be added, because 'a' belongs already to
# the group.
_try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'my_group', {b'a'}))


# Gets group 'my_group' members under given namespace.
# Note that the type of returned member is bytes.
ret_members = _try_func_return(lambda: mysdl.get_members(MY_GRP_NS, 'my_group'))
assert ret_members == {b'a'}


# Checks if 'a' is a member of the group 'my_group' under given namespace.
was_member = _try_func_return(lambda: mysdl.is_member(MY_GRP_NS, 'my_group', b'a'))
assert was_member is True
was_member = _try_func_return(lambda: mysdl.is_member(MY_GRP_NS, 'my_group', b'not a member'))
assert was_member is False


# Returns the count of members of a group 'my_group' under given namespace.
ret_count = _try_func_return(lambda: mysdl.group_size(MY_GRP_NS, 'my_group'))
assert ret_count == 1


# Removes the member 'a' of the group 'my_group' under given namespace.
_try_func_return(lambda: mysdl.remove_member(MY_GRP_NS, 'my_group', {b'a', b'not exists'}))
ret_count = _try_func_return(lambda: mysdl.group_size(MY_GRP_NS, 'my_group'))
assert ret_count == 0


# Removes the group 'my_group' under given namespace.
_try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'my_group', {b'a', b'b', b'c'}))
ret_count = _try_func_return(lambda: mysdl.group_size(MY_GRP_NS, 'my_group'))
assert ret_count == 3

_try_func_return(lambda: mysdl.remove_group(MY_GRP_NS, 'my_group'))
ret_count = _try_func_return(lambda: mysdl.group_size(MY_GRP_NS, 'my_group'))
ret_members = _try_func_return(lambda: mysdl.get_members(MY_GRP_NS, 'my_group'))
assert ret_count == 0
assert ret_members == set()


# Gets a lock 'my_lock' resource under given namespace.
# Note that this function does not take a lock, you need to call 'acquire' function to take
# the lock to yourself.
my_lock = _try_func_return(lambda: mysdl.get_lock_resource(MY_LOCK_NS, "my_lock", expiration=5.5))
assert my_lock is not None


# Acquires a lock from the lock resource. Return True if lock was taken within given retry limits.
was_acquired = _try_func_return(lambda: my_lock.acquire(retry_interval=0.5, retry_timeout=2))
assert was_acquired is True
# Try again. This time a lock won't be acquired successfully, because we have a lock already.
was_acquired = _try_func_return(lambda: my_lock.acquire(retry_interval=0.1, retry_timeout=0.2))
assert was_acquired is False


# Refreshs the remaining validity time of the existing lock back to the initial value.
_try_func_return(my_lock.refresh)


# Gets the remaining validity time of the lock.
ret_time = _try_func_return(my_lock.get_validity_time)
assert ret_time != 0


# Releases the lock.
_try_func_return(my_lock.release)


# Locking example what utilizes python 'with' statement with SDL lock.
# The lock is released automatically when we are out of the scope of
# 'the with my_lock' statement.
my_lock = _try_func_return(lambda: mysdl.get_lock_resource(MY_LOCK_NS, "my_lock", 2.5))
with my_lock:
    # Just an example how to use lock API
    time_left = _try_func_return(my_lock.get_validity_time)

    # Add here operations what needs to be done under a lock, for example some
    # operations with a shared resources what needs to be done in a mutually
    # exclusive way.

# Lock is not anymore hold here


# Closes the SDL connection.
mysdl.close()
