# otter
Infrastructure framework for Qubes-OS based testing on VMWare

The idea is to develop our own set of tools to automate as much as possible any SDW-related testing, while keeping the ability for interactive debugging sessions, results artifacts, GUI testing and so on.

The backend hypervisor is vmware ESX 7, that is so far the one that works best for nesting Qubes, but the project is structured in classes that would allow seamlessy plugging in another backend.

# Classes
## vmware
The `vmwareAdapter` class provides more abstract methods for easy interaction with the ESX server building on top of [pyvmomi](https://github.com/vmware/pyvmomi).

### vmwareAdapter
```
class vmwareAdapter:
    def __init__(self, username, password, host, vmname="", headers={}, verify=True):
```
 * *username*: ESX username
 * *password*: ESX password
 * *host*: ESX host
 * *vmname*: not required, is autodetected later in the code, should be the VM name in ESX of the vm where the code is being invoked
 * *headers*: passed to pyvmomi *customerHeaders*
 * *verify*: check SSL (has cascading effect, ie: on the VNC connections)

##### listMachines()
Returns a list of *Machine* objects corresponding to all the VMs ion the server.

##### getFreeMachine(name=""):
Returns the first _powered off_ result as Machine object.
 * *name*: loosely matched (lowercase, contained in) search for a VM

##### getMachineByName(name)
Return the first Machine that match.
 * *name*: case insensitive, loosely matched

##### getMachineByMoid(moid)
Return the Machine that match.
 * *moid*: virtual machine _moid_

##### getMachineByMAC(mac)
Returns a Machine that has the MAC Address assigned to any interface.
 * *mac*: case insensitive, with or without the semicolon with leading 0s stripped

Used for auto detecting the *vmname* where the code is currently running.

##### killMachineByName(name)
Force power off of the machine which name is supplied as parameter.
 * *name*: exactly matched, the machine to be killed.

##### listDatastores()
Returns a list of datastore objects.

### Machine
Machine are abstract objects that represent a VM. A few higher level methods and variables are available for programming convenience, but everything in background is still managed by `pyvmomi`. The `pvmomi` original object is always kept available as Machine.vmware_object. Note that objects are not dynamically update, so the power state might change and that change might not be reflected in the object for example.

It can be initialized just by passing `vmware_object` which is the raw `pyvmomi` object. For some internal functionalitis, `adapter` and `connection` might be well needed. (TODO: probably connection is droppable).
```
class Machine:
    def __init__(self, vmware_object, connection=None, adapter=None):
```

##### getPowerState()
False if the machine is Off, True if the machine is On. This is the state _at the object creation and not dynamically updated_.

##### powerOn()
Synchronous blocking call, returns when the operation has been completed.

##### powerOff()
Synchronous blocking call, returns when the operation has been completed.

##### listSnapshots()
Returns a list of Snapshot objects, exhaustive for the Machine object.

##### revertSnapshot(name)
Revert to the selected snapshot. Internally, it calls `revert()` on a Snapshot object, and uses `pyvmomi WaitForTask` to wait for the operation complete. The call it is thus blocking synchronous: we expect that when the function call returns, the revert operation has completed in the backend.
 * *name*: target snapshot to revert to.

##### deleteSnapshot(name)
Delete the snapshot by name. The action is irrecoverable, and is asynchronous non blocking, the function will return immediately regardless of the deletion progress.
 * *name*: target snapshot to delete.

##### takeSnapshot(self, name, description, withram, quiesce):
Take a snapshot (TODO research internals, see if it's blocking or what).

 * *name*: mandatory snapshot label.
 * *description*: optional additional dewcription text.
 * *withram*: required if the machine is powered on, then a restore will be to the same state.
 * *quisce*: vmware disk stuff.

##### getMKS()
Returns a ticket (string) for the VNC websocket. The tickets are always one time use, meaning that when something connects, it works only until that connection is alive. Parallel connections to the same machine can be done, but each must use a different ticket. The ticket returned is a string, and the actual websocket has to be constructed as `url = f"wss://{self.adapter.host}/ticket/{ticket}"`

##### getVNC(self, port, local)
No parameters required, by default will listen on localhost and on a randomly selected free port. Requires [websocat](https://github.com/vi/websocat) to be available in path in order to forward the VNC over websocket to a no authentication, unencrypted TCP VNC socket. The random free port is selected using python built in `socket` module. The `websocat` process is spawned with `Popen` and references to it are being kept in order to be able to shut it down when an operation has completed. `websocat` inherits the `verify` flag from `vmwareAdapter` when choosing if to ignore SSL errors when connecting to the websocket. Can be called an unlimited number of times, will return different ports and all will be valid.

Returns a `(host, port)` tuple to which VNC is available.

 * *port*: optional, port on which websocat should forward.
 * *local*: default True, if False than the listen address is `0.0.0.0`

##### killVNC()
Kills all the `websocat` processes that have been started, effectively ending all VNC sessions.

##### getVMRC()
Returns a single use VMRC url token for VMRC connections. It requires ESX to be reachable both on port 443 and 903 (and maybe more). Barely tested.

##### listSerialPorts()
Returns a python list of `SerialPort` objects. Used internally.

#### listNetworkCards()
Returns a python list of `NetworkCard` objects. Used internally.


