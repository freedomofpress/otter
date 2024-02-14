from logging import logging
from time import sleep
from PIL import Image
import serial
import os

START_SNAPSHOT = "kickstart"
BAUDRATE = 115200

class Otter:
    def __init__(self, machine, adapter, testfile, outputfolder, screenrecord=False):
        self.machine = machine
        self.adapter = adapter
        self.testfile = testfile
        self.outputfolder = outputfolder

        if not os.path.exists(outputfolder):
            try:
                os.makedirs(outputfolder)
            except:
                logging.error("Impossible to create dir {outputfolder}")
                return False

        self.outputfolder = outputfolder

        # restore snapshot
        snapshots = self.machine.listSnapshots()
        for snapshot in snapshots:
            if snapshot.name == START_SNAPSHOT:
                snapshot.revert()
                # TODO: check the task status instead of waiting
                sleep(5)

        # power on machine and get the consoles
        logging.info("Powering on machine {self.machine.name} id: {self.machine.vmoid}")
        machine.powerOn()
        while not adapter.getMachineByMoid(machine.moid).getPowerState():
            logging.info("Waiting for the machine to power on")

        # get machine connection details
        self.serial = machine.getSerialPort()

        try:
            self.serial_obj = serial.Serial(self.serial, BAUDRATE)
        except Exception as e:
            logging.error("Failed to open serial port")
            self.machine.powerOff()
        
        self.vnc = machine.getVNC()
        self.vnc_obj = VNC()

        if screenrecord:
            # get extra VNC socket just for the recorder
            # and pick a library/method for recording
            # TODO
            pass
