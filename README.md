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

## Sample run
Here is an example run of this code:
```
adapter = vmware.vmwareAdapter(username, password, host, headers={}, verify=False)

# Look for a free machine with "Qubes 42 Otter" name prefix
vm = adapter.getFreeMachine(vms)
# Initialize otter, will spawn VNC + serial
otter = Otter(vm, adapter, testfile=None, screenrecord=None)
# Serial console login example, with success checking
qubes.login_serial(otter)
# VNC login example, with success checking
qubes.login_gui(otter)
# Run a command on any qube via serial
qubes.run_command_in_qube_serial_and_wait(otter, "sys-net", "id", "groups")
# Example of starting a GUI app via serial
qubes.launch_terminal_dom0(otter)
# Save logs and poweroff
otter.exit()
```


```
INFO:root:Temp output folder is /tmp/tmp0y32jrfw
INFO:root:Starting Otter, outdir: /tmp/tmp0y32jrfw, vm: Qubes 42 Otter 1
INFO:root:Reverting to snapshot kickstart
INFO:root:Powering on machine Qubes 42 Otter 1 id: 16
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:listNetworkCards() lists only VMXNET3 type cards!
INFO:root:Local port should be /dev/ttyS3, target port should be /dev/ttyS0
INFO:root:VNC is not natively available, using websocket ticket + websocket forwarder
INFO:root:Running websocat on 127.0.0.1:55881 target wss://192.168.1.200/ticket/330f6b3158480009, verify = -k
websocat: Unfortunately, serving multiple clients without --exit-on-eof (-E) or with -U option is prone to socket leak in this websocat version
INFO:root:Attempting VNC connect
INFO:twisted:Starting factory <vncdotool.client.VNCDoToolFactory object at 0x7fe4812c9b90>
INFO:twisted:Using protocol version 3.8
INFO:twisted:Offered <AuthTypes.NONE: 1>
INFO:twisted:Native PixelFormat(bpp=32, depth=24, bigendian=False, truecolor=True, redmax=255, greenmax=255, bluemax=255, redshift=16, greenshift=8, blueshift=0) bytes=4
INFO:twisted:Offering <Encoding.RAW: 0>
INFO:twisted:Offering <Encoding.PSEUDO_DESKTOP_SIZE: -223>
INFO:twisted:Offering <Encoding.PSEUDO_LAST_RECT: -224>
INFO:twisted:Offering <Encoding.PSEUDO_QEMU_EXTENDED_KEY_EVENT: -258>
INFO:twisted:x=0 y=0 w=512 h=400 <Encoding.RAW: 0>
INFO:twisted:x=512 y=0 w=208 h=400 <Encoding.RAW: 0>
DEBUG:root:<PIL.Image.Image image mode=RGB size=720x400 at 0x7FE4812BCA50>
INFO:root:Attempting serial connect to /dev/ttyS3
INFO:root:Succesfully connected to /dev/ttyS3
WARNING:easyocr.easyocr:Neither CUDA nor MPS are available - defaulting to CPU. Note: This module is much faster with a GPU.
INFO:root:Waiting for the serial login prompt
INFO:root:Waited 33 seconds for the string
INFO:root:Typing serial username
INFO:root:Typing serial password
INFO:root:Reading serial login result
INFO:root:
Qubes release 4.2.0 (R4.2)
Kernel 6.1.75-1.qubes.fc37.x86_64 on an x86_64 (ttyS0)

dom0 login: user
Password: 
Last login: Tue Feb 13 16:59:41 on :0
[user@dom0 ~]$ 
INFO:root:Waiting for Qubes login screen
INFO:root:Using capture region with x=250, y=200, w=300, h=200
DEBUG:vncdotool.client:captureRegion /tmp/tmp0y32jrfw/0.png
INFO:twisted:x=0 y=0 w=800 h=600 <Encoding.PSEUDO_DESKTOP_SIZE: -223>
DEBUG:vncdotool.client:captureSave /tmp/tmp0y32jrfw/0.png
INFO:root:Screen captures as /tmp/tmp0y32jrfw/0.png
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 1652
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 1652
DEBUG:PIL.Image:Error closing: Operation on closed image
INFO:root:Read text '['select', 'which entry', 'highlight', 'selected', '0S', 'to', 'edit', 'the', 'col', 'for', 'COMMand-line', 'executed', 'autoMatically', 'Ss']' from /tmp/tmp0y32jrfw/0.png
select which entry highlight selected 0S to edit the col for COMMand-line executed autoMatically Ss
INFO:root:Using capture region with x=250, y=200, w=300, h=200
DEBUG:vncdotool.client:captureRegion /tmp/tmp0y32jrfw/1.png
INFO:twisted:x=0 y=0 w=512 h=512 <Encoding.RAW: 0>
INFO:twisted:x=512 y=0 w=288 h=512 <Encoding.RAW: 0>
INFO:twisted:x=0 y=512 w=512 h=88 <Encoding.RAW: 0>
INFO:twisted:x=512 y=512 w=288 h=88 <Encoding.RAW: 0>
DEBUG:vncdotool.client:captureSave /tmp/tmp0y32jrfw/1.png
INFO:root:Screen captures as /tmp/tmp0y32jrfw/1.png
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 5410
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 5410
DEBUG:PIL.Image:Error closing: Operation on closed image
INFO:root:Read text '['user', 'Log -']' from /tmp/tmp0y32jrfw/1.png
INFO:root:Waited 2 seconds for the string
INFO:root:Typing password and logging in
DEBUG:vncdotool.client:keyPress p
DEBUG:vncdotool.client:keyDown p
DEBUG:vncdotool.client:keyUp p
DEBUG:vncdotool.client:keyPress a
DEBUG:vncdotool.client:keyDown a
DEBUG:vncdotool.client:keyUp a
DEBUG:vncdotool.client:keyPress s
DEBUG:vncdotool.client:keyDown s
DEBUG:vncdotool.client:keyUp s
DEBUG:vncdotool.client:keyPress s
DEBUG:vncdotool.client:keyDown s
DEBUG:vncdotool.client:keyUp s
DEBUG:vncdotool.client:keyPress w
DEBUG:vncdotool.client:keyDown w
DEBUG:vncdotool.client:keyUp w
DEBUG:vncdotool.client:keyPress o
DEBUG:vncdotool.client:keyDown o
DEBUG:vncdotool.client:keyUp o
DEBUG:vncdotool.client:keyPress r
DEBUG:vncdotool.client:keyDown r
DEBUG:vncdotool.client:keyUp r
DEBUG:vncdotool.client:keyPress d
DEBUG:vncdotool.client:keyDown d
DEBUG:vncdotool.client:keyUp d
DEBUG:vncdotool.client:keyPress enter
DEBUG:vncdotool.client:keyDown enter
DEBUG:vncdotool.client:keyUp enter
INFO:root:Waiting for the desktop
INFO:root:Using capture region with x=1200, y=0, w=80, h=30
DEBUG:vncdotool.client:captureRegion /tmp/tmp0y32jrfw/2.png
INFO:twisted:x=0 y=0 w=1280 h=1024 <Encoding.PSEUDO_DESKTOP_SIZE: -223>
DEBUG:vncdotool.client:captureSave /tmp/tmp0y32jrfw/2.png
INFO:root:Screen captures as /tmp/tmp0y32jrfw/2.png
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 28
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 28
DEBUG:PIL.Image:Error closing: Operation on closed image
INFO:root:Read text '[]' from /tmp/tmp0y32jrfw/2.png

INFO:root:Using capture region with x=1200, y=0, w=80, h=30
DEBUG:vncdotool.client:captureRegion /tmp/tmp0y32jrfw/3.png
INFO:twisted:x=0 y=0 w=512 h=512 <Encoding.RAW: 0>
INFO:twisted:x=512 y=0 w=512 h=512 <Encoding.RAW: 0>
INFO:twisted:x=1024 y=0 w=256 h=512 <Encoding.RAW: 0>
INFO:twisted:x=0 y=512 w=512 h=128 <Encoding.RAW: 0>
INFO:twisted:x=512 y=512 w=512 h=128 <Encoding.RAW: 0>
INFO:twisted:x=1024 y=512 w=256 h=128 <Encoding.RAW: 0>
INFO:twisted:x=0 y=640 w=512 h=384 <Encoding.RAW: 0>
INFO:twisted:x=512 y=640 w=512 h=384 <Encoding.RAW: 0>
INFO:twisted:x=1024 y=640 w=256 h=384 <Encoding.RAW: 0>
DEBUG:vncdotool.client:captureSave /tmp/tmp0y32jrfw/3.png
INFO:root:Screen captures as /tmp/tmp0y32jrfw/3.png
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 1375
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 1375
DEBUG:PIL.Image:Error closing: Operation on closed image
INFO:root:Read text '['user']' from /tmp/tmp0y32jrfw/3.png
INFO:root:Waited 1 seconds for the string
INFO:root:Waited 1 seconds for the string
INFO:root:Starting xfce4-terminal in dom0
INFO:root:
Qubes release 4.2.0 (R4.2)
Kernel 6.1.75-1.qubes.fc37.x86_64 on an x86_64 (ttyS0)

dom0 login: user
Password: 
Last login: Tue Feb 13 16:59:41 on :0
[user@dom0 ~]$ qvm-run --pass-io 'sys-net' 'id'
uid=1000(user) gid=1000(user) groups=1000(user),98(qubes) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
[user@dom0 ~]$ export DISPLAY=:0
[user@dom0 ~]$ xfce4-terminal
Failed to connect to session manager: Failed to connect to the session manager: SESSION_MANAGER environment variable not defined

INFO:root:Using capture region with x=0, y=30, w=300, h=100
DEBUG:vncdotool.client:captureRegion /tmp/tmp0y32jrfw/4.png
INFO:twisted:x=32 y=0 w=224 h=512 <Encoding.RAW: 0>
INFO:twisted:x=32 y=512 w=224 h=48 <Encoding.RAW: 0>
INFO:twisted:x=800 y=0 w=48 h=512 <Encoding.RAW: 0>
INFO:twisted:x=800 y=512 w=48 h=48 <Encoding.RAW: 0>
INFO:twisted:x=0 y=16 w=32 h=512 <Encoding.RAW: 0>
INFO:twisted:x=0 y=528 w=32 h=32 <Encoding.RAW: 0>
INFO:twisted:x=256 y=16 w=512 h=512 <Encoding.RAW: 0>
INFO:twisted:x=768 y=16 w=32 h=512 <Encoding.RAW: 0>
INFO:twisted:x=256 y=528 w=512 h=32 <Encoding.RAW: 0>
INFO:twisted:x=768 y=528 w=32 h=32 <Encoding.RAW: 0>
INFO:twisted:x=1056 y=32 w=208 h=96 <Encoding.RAW: 0>
INFO:twisted:x=128 y=560 w=112 h=16 <Encoding.RAW: 0>
DEBUG:vncdotool.client:captureSave /tmp/tmp0y32jrfw/4.png
INFO:root:Screen captures as /tmp/tmp0y32jrfw/4.png
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 5530
DEBUG:PIL.PngImagePlugin:STREAM b'IHDR' 16 13
DEBUG:PIL.PngImagePlugin:STREAM b'IDAT' 41 5530
DEBUG:PIL.Image:Error closing: Operation on closed image
INFO:root:Read text '['File', 'Edit', 'View', 'Terminal', 'Tabs', 'Help', '[userddomo ~]s']' from /tmp/tmp0y32jrfw/4.png
INFO:root:Waited 0 seconds for the string
INFO:root:Dsconnecting from VNC
INFO:twisted:Stopping factory <vncdotool.client.VNCDoToolFactory object at 0x7fe4812c9b90>
INFO:twisted:Main loop terminated.
INFO:root:Killing any websocat forwarder
INFO:root:Powering off the vm Qubes 42 Otter 1
INFO:root:Saving the serial output to /tmp/tmp0y32jrfw/serial.log
```

With the following serial output:
```
Qubes release 4.2.0 (R4.2)
Kernel 6.1.75-1.qubes.fc37.x86_64 on an x86_64 (ttyS0)

dom0 login: user
Password: 
Last login: Tue Feb 13 16:59:41 on :0
[user@dom0 ~]$ qvm-run --pass-io 'sys-net' 'id'
uid=1000(user) gid=1000(user) groups=1000(user),98(qubes) context=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
[user@dom0 ~]$ export DISPLAY=:0
[user@dom0 ~]$ xfce4-terminal
Failed to connect to session manager: Failed to connect to the session manager: SESSION_MANAGER environment variable not defined

```

And the following screen captures:
 * Waiting for login prompt

![image](https://github.com/freedomofpress/otter/assets/66009328/934331f4-2688-4519-b6b7-4bdd3fd99e5b)

 * Login prompt found

![image](https://github.com/freedomofpress/otter/assets/66009328/771c0b9e-31a3-491a-8420-f621b1d1c328)

 * Waiting for desktop session

![image](https://github.com/freedomofpress/otter/assets/66009328/d6526a7c-e022-41bd-9098-ff24f0e75450)

 * Successful login verified

![image](https://github.com/freedomofpress/otter/assets/66009328/d0dfeda5-b69c-4973-a7c9-64dbb04d38d6)

 * dom0 fce4-terminal start success

![image](https://github.com/freedomofpress/otter/assets/66009328/ea7b5e84-9fa0-431b-95bf-bfff99bb5ecd)

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

