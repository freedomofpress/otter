import logging
import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

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
    def __init__(self, vmware_object, connection=None):
        if connection:
            self.connection = connection
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

    def print(self):
        print(f"Id:\t\t{self.moid}")
        print(f"Name:\t\t{self.name}")
        print(f"PowerState:\t{self.powerstate}")

    def updateInfo(self):
        return

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

    def getMKS(self):
        if self.powerstate == vim.VirtualMachinePowerState.poweredOn:
            return self.vmware_object.AcquireTicket("webmks").ticket
        else:
            logging.warning(f"Machine {self.name} is powered off, so no websocket available")
            return False

    def getVNC(self, port):
        assert(port > 1024 and port <= 65535)
        logging.info("VNC is not natively available, using websocket ticket + websocket forwarder")
        ticket = self.getMKS()
        url = f"wss://host/ticket/{ticket}"
        return

    def getVMRC(self):
        if self.connection:
            content = self.connection.RetrieveContent()
            session_manager = content.sessionManager
            session = session_manager.AcquireCloneTicket()
        else:
            logging.warning("Connection object not provided when instantiating VM object")

        return f"vmrc://clone:{session}@127.0.0.1:8443/?moid={self.moid}"

    def getSerialPorts(self):
        return

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
    def __init__(self, username, password, host, headers={}, verify=True):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)

        if not verify:
            ssl_context.verify_mode = ssl.CERT_NONE

        try:
            self.connection = SmartConnect(user=username, pwd=password, host=host, sslContext=ssl_context, customHeaders=headers)
            self.host = host

        except Exception as e:
            logging.error(f"Failed to connect to ESX at host {host}:\n{e}")
            self.connection = None
            self.host = None    

    def getInfo(self):
        return

    def createMachineObject(self, virtual_machine):
        machine_object = Machine(virtual_machine, self.connection)
        return machine_object

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

    def getFreeMachine(self):
        return

    def getMachineByName(self, name):
        for machine in self.listMachines():
            if name == machine.name:
                return machine
        return False

    def killMachineByName(self, name):
        for machine in self.listMachines():
            if name == machine.name:
                return machine.powerOff()
        return False
