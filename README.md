# otter
Infrastructure framework for Qubes-OS based testing on VMWare

The idea is to develop our own set of tools to automate as much as possible any SDW-related testing, while keeping the ability for interactive debugging sessions, results artifacts, GUI testing and so on.

The backend hypervisor is vmware ESX 7, that is so far the one that works best for nesting Qubes, but the project is structured in classes that would allow seamlessy plugging in another backend.

## Config
In the Otter root, set the config in `otter.ini`.
```
[esx]
server = <host>
username = <username>
password = <password>
vms = <vm namespace>
```

## Examples
The `helpers` folder cointains basic helper functions for Qubes.

```
def login_gui(otter, username="user", password="password"):
    # we expect 800x600 screen at login
    logging.info("Waiting for Qubes login screen")
    assert(otter.wait_screen("Log", (250, 200, 300, 200)))
    # we do not support switching from the selected username for now, we can do it if needed
    # sends credentials
    logging.info("Typing password and logging in")
    for char in password:
        otter.vnc_client.keyPress(char)
    otter.vnc_client.keyPress("enter")

    logging.info("Waiting for the desktop")
    sleep(5)

    assert(otter.wait_screen("user", (1200, 0, 80, 30)))
```

`example.py` contains an example usage of the helper and how tests can be built on top of them.

# Classes
## otter
Otter is the main automation helper.
```
class Otter:
    def __init__(self, machine, adapter, testfile, outputfolder="", screenrecord=False, start_snapshot="kickstart", baudrate=115200):
```
 * *machine*: is a `Machine` object. A powered off free machine has to be picked before, using for instance `vmware.getFreeMachine(name)`.
 * *adapter*: the `vmwareAdapter` object.
 * *testfile*: currently not in use.
 * *outputfolder*: the folder where to store the resulting artifacts (screenshots and logs). If empty is a new temporary dir. If it does not exists creation is attempted.
 * *screenrecord*: whether to screen record the whole VNC session. Currently not implemented, we need to choose the software to do so.
 * *start_snapshot*: the name of the _snapshot_ to reset at each run.
 * *baudrate*: serial baudrate, vmware defaults at 115200.

What the initialization function will do then is:
 1. Test the output dire, create it or get a temporary one
 2. Restore the `start_snapshotz snapshot and wait for completion
 3. Power on the VM
 4. Find the Linux device for the shared serial port
 5. Open the serial port and check for basic errors
 6. Get a local VNC socket
 7. Open the VNC socket and test for basic errors
 8. Initialize easyOCR

If initialized succesfully, it the offers a few helpers for test automation. Any screenshot is saved with an incremental number for debugging purposes. The whole serial communication is kept in memory and logged at `Otter.exit()`.

##### capture_screen_wrapper(self, coordinates=())
Save a screenshot, or a portion of the screen if coordinates are provided. Returns the `filename`.

 * *coordinates*: tuple of (start x, start y, width, height).

##### get_screen_text(filename)
Will return a joined list of all the OCRed text on a given screenshot.
 * *filename*: the screenshot full path.

##### wait_screen(self, string, coordinates=(), timeout=360):
Stay in a blocking loop until `string` is found on the OCRed text, or until `timeout` seconds have passed.

##### wait_serial(self, string, timeout=360):
Stay in a blocking loop until `string` is found on the serial console, or until `timeout` seconds have passed.

##### read_serial(self)
Returns raw bytes from the serial console.

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

##### listNetworkCards()
Returns a python list of `NetworkCard` objects. Used internally.

#### getSerialPort(localvm)
While the name might seem misleading, what this function does is looking for a _local_ serial port (where local is the test orchestrator, which is the machine which is running this code) that is piped to the target machine (the VM represented by the Machine object). If `localvm` is specified, the the current machine is looked up on the ESX server by the name supplied. If not, the machine tries to find itself by looking for which VM has the local MAC address on the cluster (the autodetection works quite well). Then, it enumerates the serial port on the orchestrating machine and the serial ports of the target machine, and iteratively looks for a "named pipe" type serial port that is shared between the two. The target machine should be set as "server" and have a unique name. The test machine should be "client" and share the same unique name. Then the function tries to match that to a local port in Linux style, `/dev/ttySx` and returns that as a string.

