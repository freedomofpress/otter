import vmware
import logging
from otter import Otter

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

adapter = vmware.vmwareAdapter("root", "pass", "ip", vmname="Router", headers={}, verify=False)


vm = adapter.getFreeMachine("name*")
otter = Otter(vm, adapter, testfile=None, screenrecord=None, outputfolder="/tmp/test1")
otter.exit()
