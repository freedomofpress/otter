from PIL import Image
from vncdotool import api
import logging
import serial
import socket
import os

from time import sleep, time

class Otter:
    def __init__(self, machine, adapter, testfile, outputfolder, screenrecord=False, start_snapshot="kickstart", baudrate=115200):
        self.machine = machine
        self.adapter = adapter
        self.testfile = testfile
        self.outputfolder = outputfolder

        self.serial_output = b""

        if not os.path.exists(outputfolder):
            try:
                os.makedirs(outputfolder)
            except:
                logging.error("Impossible to create dir {outputfolder}")

        self.outputfolder = outputfolder

        # restore snapshot
        logging.info(f"Reverting to snapshot {start_snapshot}")
        self.machine.revertSnapshot(start_snapshot)

        # power on machine and get the consoles
        logging.info(f"Powering on machine {self.machine.name} id: {self.machine.moid}")
        machine.powerOn()

        # get machine connection details
        self.serial = machine.getSerialPort()

        try:
            self.serial_obj = serial.Serial(self.serial, baudrate)
        except Exception as e:
            logging.error("Failed to open serial port")
            self.machine.powerOff()
        
        self.vnc = machine.getVNC()

        if screenrecord:
            # get extra VNC socket just for the recorder
            self.screenrecord_vnc = machine.getVNC()
            # and pick a library/method for recording
            # TODO
            pass

        # TODO: find a better way not to race websocat startup
        # for instance, we can't test like this or we will use the single use VNC ticket!
        #while socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect_ex(self.vnc):
        #    print("Waiting")

        logging.info("Attempting VNC connect")
        try:
            self.vnc_client = api.connect(server=f"{self.vnc[0]}::{self.vnc[1]}", timeout=5)
            # screen is the raw pixel, capture saves the screenshot
            self.vnc_client.refreshScreen(False)
            # test capture
            logging.debug(self.vnc_client.screen)
        except Exception as e:
            logging.error(f"Failed to establish a VNC connection to {self.vnc}")    
            logging.debug(e)    

        logging.info(f"Attempting serial connect to {self.serial}")
        try:
            # would be nice if vmware supports rtscts so we can read non-blocking, let's try
            self.serial_client = serial.Serial(self.serial, baudrate, timeout=1, rtscts=1)
            assert(self.serial_client.is_open)
            logging.info(f"Succesfully connected to {self.serial}")
        except Exception as e:
            logging.error(f"Failed to connect to serial port {self.serial}")
            logging.debug(e)
        
        ### TODO: move this to qubes specific helpers
        # wair for dom0 serial login
        self.wait_serial("dom0 login: ")
        # gui should also be loaded, screen it for checking        
        self.vnc_client.captureScreen("login.png")
        # log in
        self.write_serial("user\n")
        sleep(0.3)
        self.write_serial("password\n")
        sleep(0.3)
        # check for ir
        self.read_serial()
        logging.info(self.serial_output.decode("utf-8"))

        


    def wait_serial(self, string, timeout=0):
        start = int(time())
        serial_out = self.read_serial()
        while string.encode("utf-8") not in serial_out:
            #print(serial_out)
            sleep(1)
            serial_out = self.read_serial()
            if timeout > 0 and (int(time()) - start) >= timeout:
                logging.error(f"Wait for {string} timeout out after {timeout} seconds")
                return False
        logging.info(f"Waited {int(time())-start} seconds for the string")
        return True

    def write_serial(self, string):
        # TODO: charset decision? let's go for utf-8 for now
        string = string.encode("utf-8")
        try:
            self.serial_client.write(string)
            return True
        except Exception as e:
            logging.error(e)
            return False

    def read_serial(self):
        full_read = self.serial_client.read(1024)
        data = full_read
        while len(data) == 1024:
            #print(data)
            data = self.serial_client.read(1024)
            full_read += data
        self.serial_output += full_read
        return full_read

    def screnshot(self, name):
        self.vnc_client.captureScreen(f"{self.outputfolder}/{name}.png")

    def wait_for_screen_text(self, text, timeout):
        pass

    def exit(self):
        # exit the vnc session
        logging.info("Dsconnecting from VNC")
        self.vnc_client.disconnect()
        api.shutdown()
        # kill the websocat processes
        logging.info("Killing any websocat forwarder")
        self.machine.killVNC()
        # poweroff the machine
        logging.info(f"Powering off the vm {self.machine.name}")
        self.machine.powerOff()

