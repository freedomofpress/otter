import logging
from time import sleep

# gui operations calculated on screen 1280*1024
# for installations it's always 800x600 unless bot parameters are changed

def login_serial(otter, username="user", password="password"):
    # wair for dom0 serial login
    logging.info("Waiting for the serial login prompt")
    otter.wait_serial("dom0 login: ")
    # log in
    logging.info("Typing serial username")
    otter.write_serial(f"{username}\n")
    logging.info("Typing serial password")
    otter.write_serial(f"{password}\n")
    logging.info("Reading serial login result")
    otter.read_serial()

    logging.info(otter.serial_output.decode("utf-8"))

    assert(f"{username}@dom0" in otter.serial_output.decode('utf-8'))

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

def launch_terminal_dom0(otter):
    logging.info("Starting xfce4-terminal in dom0")
    otter.write_serial("export DISPLAY=:0\n")
    otter.write_serial("xfce4-terminal\n")
    sleep(3)
    otter.read_serial()

    logging.info(otter.serial_output.decode("utf-8"))
    assert(otter.wait_screen("Terminal", (0, 30, 300, 100)))

def run_command_in_qube_serial_and_wait(otter, qube, command, string):
    cmd = f"qvm-run --pass-io '{qube}' '{command}'\n"
    otter.write_serial(cmd)
    assert(otter.wait_serial(string))

def run_command_in_qube_screen_and_wait(otter, command, waitstring, coordinates=()):
    # we could hack this and open the terminal via serial
    # but let's see if we find a mouse fix first
    pass

def qubes_install():
    # this can be done entirely mouse free, and deterministically via key press
    pass

def qubes_first_boot():
    # same as the previous one
    pass
