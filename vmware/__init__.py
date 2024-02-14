import logging
import ssl
from enum import Enum
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

class NetworkCard():
    def __init__(self, network_card_object):
        self.network_card_object = network_card_object
        self.key = network_card_object.key
        self.mac = network_card_object.macAddress
        self.connected = network_card_object.connectable.connected
        self.label = network_card_object.deviceInfo.label
        self.summary = network_card_object.deviceInfo.summary

    def print(self):
        print(f"Key:\t\t{self.key}")
        print(f"Label:\t\t{self.label}")
        print(f"MAC:\t\t{self.mac}")

class SerialPortType(Enum):
    PIPE = 1
    NETWORK = 2

class SerialPort:
    def __init__(self, port_object):
        self.port_object = port_object
        self.key = port_object.key
        self.label = port_object.deviceInfo.label
        self.summary = port_object.deviceInfo.summary
        self.connected = port_object.connectable.connected
        self.auto_connect = port_object.connectable.startConnected
        self.linux_device = f"/dev/ttyS{self.key - 9000}"

        if isinstance(port_object.backing, vim.vm.device.VirtualSerialPort.PipeBackingInfo):
            self.type = SerialPortType.PIPE
            self.pipe_name = port_object.backing.pipeName
            self.pipe_endpoint =  port_object.backing.endpoint

        elif isinstance(port_object.backing, vim.vm.device.VirtualSerialPort.URIBackingInfo):
            self.type = SerialPortType.NETWORK
            logging.warning("TODO: implement support for network serial ports, requires paid ESX license")

        else:
            logging.warning("Found non network or pipe serial port, unsupported serial access")

    def print(self):
        print(f"Key:\t\t{self.key}")
        print(f"Type:\t\t{self.type}")
        print(f"Label:\t\t{self.label}")
        print(f"Device:\t\t{self.linux_device}")
        if self.type == SerialPortType.PIPE:
            print(f"PIPE Name:\t{self.pipe_name}")
            print(f"PIPE Endpoint:\t{self.pipe_endpoint}")


class Snapshot:
    def __init__(self, snapshot_object, parent=None, connection=None):
        if connection:
            self.connection = connection
        self.parent = parent
        self.snapshot_object = snapshot_object
        self.id = snapshot_object.id
        self.name = snapshot_object.name
        self.description = snapshot_object.description
        self.timestamp = snapshot_object.createTime
        self.powerstate = snapshot_object.state
        self.quiesces = snapshot_object.quiesced
        self.child = snapshot_object.childSnapshotList
        self.vm = snapshot_object.vm

    def getChild(self):
        if self.child:
            return self.child
        else:
            return None

    def print(self):
        if self.parent:
            print(f"Parent:\t{self.parent.name}")
        print(f"Name:\t\t{self.name}")
        print(f"Description:\t{self.description}")
        print(f"Timestamp:\t{self.timestamp}")
        print(f"VM:\t\t{self.vm}")

    def delete(self):
        return self.snapshot_object.RemoveSnapshot_Task(True)

    def revert(self):
        return self.snapshot_object.RevertToSnapshot_Task()

    def rename(self,name):
        logging.error("Snapshot rename not implemented")
        return False


class Machine:
    def __init__(self, vmware_object, connection=None, adapter=None):
        if connection:
            self.connection = connection
        if adapter:
            self.adapter = adapter
        self.vmware_object = vmware_object
        self.moid = vmware_object._moId
        summary = vmware_object.summary
        self.name = summary.config.name
        self.template = summary.config.template
        self.path = summary.config.vmPathName
        self.guest = summary.config.guestFullName
        self.uuid = summary.config.instanceUuid
        self.annotation = summary.config.annotation
        self.powerstate = summary.runtime.powerState
        self.ip = summary.guest.ipAddress
        self.tools = summary.guest.toolsStatus

        # list of tuples in the form, (Popen obj, vnc port)
        self.vnc_instances = []

    def print(self):
        print(f"Id:\t\t{self.moid}")
        print(f"Label:\t\t{self.name}")
        print(f"PowerState:\t{self.powerstate}")

    def getPowerState(self):
        if self.powerstate == vim.VirtualMachinePowerState.poweredOn:
            return True
        else:
            return False

    def getCurrentSnapshot(self):
        if self.vmware_object.snapshot is not None:
            return

    def _recurseSnapshots(self, tree, parent=None):
        snapshots = []
        for snapshot_object in tree:
            snapshot = Snapshot(snapshot_object, parent)
            snapshots.append(snapshot)
            if snapshot.getChild():
                snapshots = snapshots + self._recurseSnapshots(snapshot.getChild(), parent=snapshot)
        return snapshots

    def listSnapshots(self):
        if self.vmware_object.snapshot is not None:
            return self._recurseSnapshots(self.vmware_object.snapshot.rootSnapshotList)

    def takeSnapshot(self, name, description="", withram=False, quiesce=False):
        logging.info(f"Attempting to take snapshot {name}")
        return self.vmware_object.CreateSnapshot(name, description, withram, quiesce)

    def revertSnapshot(self, name):
        snapshots = self.listSnapshots()
        for snapshot in snapshots:
            if name == snapshot.name:
                return snapshot.revert()
        logging.info(f"Snapshot {name} not found")        
        return False

    def deleteSnapshot(self, name):
        snapshots = self.listSnapshots()
        for snapshot in snapshots:
            if name == snapshot.name:
                return snapshot.delete()
        logging.info(f"Snapshot {name} not found")
        return

    # TODO: ensure that the machine is on before acquiring the websocket ticket
    def getMKS(self):
        return self.vmware_object.AcquireTicket("webmks").ticket

    def getVNC(self, port=None, local=True):
        logging.info("VNC is not natively available, using websocket ticket + websocket forwarder")
        ticket = self.getMKS()
        url = f"wss://{self.adapter.host}/ticket/{ticket}"
        if local:
            ip = "127.0.0.1"
        else:
            ip = "0.0.0.0"
        if self.adapter.verify:
            verify = ""
        else:
            verify = "-k"
        from shutil import which
        if not which("websocat"):
            logging.error("websocat not found in PATH")
            return False

        # silly hack to quickly find a free port
        if not port:
            from socket import socket
            with socket() as s:
                s.bind(('',0))
                port = s.getsockname()[1]

        from subprocess import Popen
        #from os import system
        logging.info("Running websocat on {ip}:{port} target {url}, verify = {verify}")
        proc = Popen(["websocat", "-b", f"tcp-listen:{ip}:{port}", url, verify, "--protocol", "binary, vmware-vvc"])
        #exec = system(f"websocat -b tcp-listen:{ip}:{port} {url} {verify} --protocol 'binary, vmware-vvc'")
        self.vnc_instances.append((proc, port))
        return port

    def killVNC(self, ports=[]):
        # TODO: find if kill() is better suioted than terminate()
        for instance in self.vnc_instances:
            # if ports is none, kill all
            if len(ports) == 0:
                instance[0].terminate()
            else:
                for port in ports:
                    if instance[1] == port:
                        instance[0].terminate()

    def getVMRC(self):
        if self.connection:
            content = self.connection.RetrieveContent()
            session_manager = content.sessionManager
            session = session_manager.AcquireCloneTicket()
        else:
            logging.warning("Connection object not provided when instantiating VM object")

        return f"vmrc://clone:{session}@host:port/?moid={self.moid}"

    # Just return the info about serialports
    def listSerialPorts(self):
        serial_ports = []
        for device in self.vmware_object.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualSerialPort):
                serial_ports.append(SerialPort(device))
        return serial_ports

    def listNetworkCards(self):
        logging.info("listNetworkCards() lists only VMXNET3 type cards!")
        network_cards = []
        for device in self.vmware_object.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualVmxnet3):
                network_cards.append(NetworkCard(device))
        return network_cards

    # we shall support 2 options here
    # if ESX is licensed, then we can have network serial ports and everything is easier, and this node can be remote
    # if esx is unlicensed, then serial ports and only be named pipes, and the far end is this local machine
    # which needs to be in the hypervisor as the testing vms
    def getSerialPort(self, localvm=None):
        # we refer to target as the vm where the test have to be run
        # and to local as the machine where this script is running
        target_serial_ports = self.listSerialPorts()
        # attempt searching for the local vm in the vmware node based on mac address
        # otherwise provide the label in "localvm"

        # if a network port is available, we choose the first one in the list
        for target_serial_port in target_serial_ports:
            if target_serial_port.type == SerialPortType.NETWORK:
                logging.error("Network serial port found but support not complete")
                return False

        if not self.adapter:
            logging.error("An adapter object has to be passed to automatically find a pipe serial port")
            return False
        if localvm:
            # if a label is provided use that
            local = self.adapter.getMachineByName(localvm)
        else:
            # otherwise search by mac address the local machine
            from uuid import getnode
            mac = hex(getnode())[2:]
            local = self.adapter.getMachineByMAC(mac)
        if not local:
            logging.error("Unable to find the test machine on the vmware server")
            return False
        
        local_serial_ports = local.listSerialPorts()

        # lol this is ugly but here we are
        for target_serial_port in target_serial_ports:
            if target_serial_port.type == SerialPortType.PIPE:
                for local_serial_port in local_serial_ports:
                    if (local_serial_port.type == SerialPortType.PIPE and
                        local_serial_port.pipe_name == target_serial_port.pipe_name and
                        local_serial_port.pipe_endpoint == "client" and
                        target_serial_port.pipe_endpoint == "server"):
                            logging.info(f"Local port should be {local_serial_port.linux_device}, target port should be {target_serial_port.linux_device}")
                            return local_serial_port.linux_device
                            # we have a match!


    def getScreenshot(self):
        # call getVNC
        # get local websocket
        # take screenshot
        return

    def powerOff(self):
        return self.vmware_object.PowerOff()

    def powerOn(self):
        return self.vmware_object.PowerOn()

class vmwareAdapter:
    def __init__(self, username, password, host, vmname="", headers={}, verify=True):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)

        if not verify:
            ssl_context.verify_mode = ssl.CERT_NONE

        try:
            self.connection = SmartConnect(user=username, pwd=password, host=host, sslContext=ssl_context, customHeaders=headers)
            self.host = host
            self.verify = verify
            self.vmname = vmname

        except Exception as e:
            logging.error(f"Failed to connect to ESX at host {host}:\n{e}")
            self.connection = None
            self.host = None    

    def getInfo(self):
        return

    # Helper func
    def createMachineObject(self, virtual_machine):
        machine_object = Machine(virtual_machine, self.connection, adapter=self)
        return machine_object

    # Returns a list of "Machine" objects. Machine is a custom made class, but it also contains the original
    # pyvmomi object which remains accessible
    def listMachines(self):
        content = self.connection.RetrieveContent()

        container = content.rootFolder
        view_type = [vim.VirtualMachine]
        recursive = True 
        container_view = content.viewManager.CreateContainerView(container, view_type, recursive)
        children = container_view.view

        machines = []
        for virtual_machine in children:
            machines.append(self.createMachineObject(virtual_machine))
        return machines

    # Scans true the VMs on the ESX host looking for one including the name and powered off
    def getFreeMachine(self, name=""):
        for machine in self.listMachines():
            if name.lower() in machine.name.lower() and machine.powerstate == vim.VirtualMachinePowerState.poweredOff:
                return machine
        return False

    # Lookup a VM by name, case insensitive
    def getMachineByName(self, name):
        for machine in self.listMachines():
            if name.lower() in machine.name.lower():
                return machine
        return False

    def getMachineByMoid(self, moid):
        for machine in self.listMachines():
            if moid in machine.moid:
                return machine
        return False
            
    def getMachineByMAC(self, mac):
        for machine in self.listMachines():
            for network_card in machine.listNetworkCards():
                if mac.lower() in network_card.mac.lower() or mac in network_card.mac.lower().replace(":", "").lstrip("0"):
                    return machine
        return False

    # We do not want a loose match here, so we expect the name to match erfectly
    def killMachineByName(self, name):
        for machine in self.listMachines():
            if name == machine.name:
                return machine.powerOff()
        return False
