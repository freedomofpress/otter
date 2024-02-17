from tempfile import TemporaryDirectory
from PIL import Image
from vncdotool import api
import logging
import serial
import socket
import os
import easyocr

from time import sleep, time

class Otter:
    def __init__(self, machine, adapter, testfile, outputfolder="", screenrecord=False, start_snapshot="kickstart", baudrate=115200):
        self.machine = machine
        self.adapter = adapter
        self.testfile = testfile
        self.outputfolder = outputfolder

        self.serial_output = b""
        self.screen_count = 0

        if len(outputfolder) == 0:
            # generate dir in tmp
            outputfolder = TemporaryDirectory().name
            logging.info(f"Temp output folder is {outputfolder}")
        
        if not os.path.exists(outputfolder):
            try:
                os.makedirs(outputfolder)
            except:
                logging.error(f"Impossible to create dir {outputfolder}")

        self.outputfolder = outputfolder

        logging.info(f"Starting Otter, outdir: {outputfolder}, vm: {self.machine.name}")

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

        self.easyocr = easyocr.Reader(['en'])

        logging.info(f"Attempting serial connect to {self.serial}")
        try:
            # would be nice if vmware supports rtscts so we can read non-blocking, let's try
            self.serial_client = serial.Serial(self.serial, baudrate, timeout=1, rtscts=1)
            assert(self.serial_client.is_open)
            logging.info(f"Succesfully connected to {self.serial}")
        except Exception as e:
            logging.error(f"Failed to connect to serial port {self.serial}")
            logging.debug(e)

        self.reader = easyocr.Reader(['en'])


    def capture_screen_wrapper(self, coordinates=()):
        filename = f"{self.outputfolder}/{self.screen_count}.png"
        try:
            if len(coordinates) == 4:
                logging.info(f"Using capture region with x={coordinates[0]}, y={coordinates[1]}, w={coordinates[2]}, h={coordinates[3]}")
                self.vnc_client.captureRegion(filename, coordinates[0], coordinates[1], coordinates[2], coordinates[3])
            else:
                logging.info("Capturing full screen")
                self.vnc_client.captureScreen(filename)
            logging.info(f"Screen captures as {filename}")
            self.screen_count += 1
        except Exception as e:
            logging.info(f"Capture {filename} failed, maybe no updates available")
            logging.debug(e)

        return filename

    def get_screen_text(self, filename):
        text = self.reader.readtext(filename, detail=0)
        logging.info(f"Read text '{text}' from {filename}")
        # TODO: quick hack for easier matching, having separate items might help
        return " ".join(text)

    def wait_screen(self, string, coordinates=(), timeout=360):
        start = int(time())
        filename = self.capture_screen_wrapper(coordinates)
        screen_out = self.get_screen_text(filename)
        while string not in screen_out:
            print(screen_out)
            sleep(1)
            filename = self.capture_screen_wrapper(coordinates)
            screen_out = self.get_screen_text(filename)
            if timeout > 0 and (int(time()) - start) >= timeout:
                logging.error(f"Wait for {string} timeout out after {timeout} seconds")
                return False
        logging.info(f"Waited {int(time())-start} seconds for the string")
        return True

    def wait_serial(self, string, timeout=360):
        start = int(time())
        serial_out = self.read_serial()
        while string.encode("utf-8") not in serial_out:
            logging.debug(serial_out)
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
            sleep(0.2)
            return True
        except Exception as e:
            logging.error(e)
            return False

    def read_serial(self):
        full_read = self.serial_client.read(1024)
        data = full_read
        while len(data) == 1024:
            logging.debug(data)
            data = self.serial_client.read(1024)
            full_read += data
        self.serial_output += full_read
        return full_read

    def screen(self):
        self.vnc_client.framebufferUpdateRequest(False)
        return self.vnc_client.screen

    def exit(self):
        # TODO: maybe if something went wrong we can snapshot here like
        #if self.fail:
        #    self.machine.take_snapshot(blabla)
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
        # saving the serial log
        logging.info(f"Saving the serial output to {self.outputfolder}/serial.log")
        with open(f"{self.outputfolder}/serial.log", "wb") as f:
            f.write(self.serial_output)

