from configparser import ConfigParser
import vmware
import logging
from otter import Otter
from helpers import qubes

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

config = ConfigParser()
config.read('otter.ini')
host = config.get('esx', 'server')
username = config.get('esx', 'username')
password = config.get('esx', 'password')
vms = config.get('esx', 'vms')

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
