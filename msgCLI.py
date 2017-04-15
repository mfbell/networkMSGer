"""MSG App CLI Module.



Written by {0}
Version {1}
Status: {2}
Licensed under {3}
URL: {4}

"""

AUTHOR = "mtech0 | https://github.com/mtech0"
LICENSE = "GNU-GPLv3 | https://www.gnu.org/licenses/gpl.txt"
VERSION = "0.4.0"
STATUS = "Development"
URL = ""
__doc__ = __doc__.format(AUTHOR, VERSION, STATUS, LICENSE, URL)

import threading
import queue
from tools import debug_msg, Thread_tools, main

class Printer(threading.Thread, Thread_tools):
    """Print Class."""

    def __init__(self, print_queue, kill, debug=True, run=True, timeout=5.0):
        threading.Thread.__init__(self)
        self.print_queue = print_queue
        self.kill = kill
        self.debug = debug
        self.is_autorun = run
        self.timeout = timeout
        Thread_tools.__init__(self)

    def run(self):
        while not self.kill.is_set():
            try:
                msg = self.print_queue.get(True, 5.0)
                print(msg)
            except queue.Empty:
                pass

class Interface(threading.Thread, Thread_tools):
    """Interface class."""

    def __init__(self, input_queue, kill, debug=True, run=True, timeout=5.0):
        threading.Thread.__init__(self)
        self.input_queue = input_queue
        self.kill = kill
        self.debug = debug
        self.is_autorun = run
        self.timeout = timeout
        Thread_tools.__init__(self)

    def run(self):
        while not self.kill.is_set():
            msg = input(">")
            if msg == "!kill":
                self.kill.set()
                continue
            self.input_queue.put(msg)
            #time.sleep(0.05)

if __name__ == '__main__':
    main(__doc__)
