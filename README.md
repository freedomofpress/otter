# otter
Infrastructure framework for Qubes-OS based testing on VMWare

The idea is to develop our own set of tools to automate as much as possible any SDW-related testing, while keeping the ability for interactive debugging sessions, results artifacts, GUI testing and so on.

The backend hypervisor is vmware ESX 7, that is so far the one that works best for nesting Qubes, but the project is structured in classes that would allow seamlessy plugging in another backend.

# Classes
## VMWare
The WMWareAdapter class provides more abstract methods for easy interaction with the ESX server building on top of [pyvmomi](https://github.com/vmware/pyvmomi).

#### vmwareAdapter
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

#### Machine
