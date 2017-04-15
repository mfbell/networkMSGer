"""MSG App Core.



Written by {0}
Version {1}
Status: {2}
Licensed under {3}
URL: {4}

"""

AUTHOR = "mtech0 | https://github.com/mtech0"
LICENSE = "GNU-GPLv3 | https://www.gnu.org/licenses/gpl.txt"
VERSION = "0.0.0"
STATUS = "Development"
URL = ""
__doc__ = __doc__.format(AUTHOR, VERSION, STATUS, LICENSE, URL)

import threading
import queue
#import sys # geting system args also with msvcrt
#import traceback # dev
#import msvcrt # need work
#import time # need work
#import networkTesting # does this belong here?
from tools import debug_msg, Tools, Thread_tools, main, sys_args
import errors

class Core(threading.Thread, Thread_tools):
    """The Core of msgCore.py."""

    def __init__(self, interface, qu_inputs, qu_to_connection, qu_from_connection, qu_to_interface, kill, debug=True, run=True, timeout=5.0):
        """Initialization.

        """
        threading.Thread.__init__(self)
        self.interface = interface # What is this? The interface object or a queue to send cmds down???
        self.qu_inputs = qu_inputs
        self.qu_to_interface = qu_to_interface
        self.qu_from_connection = qu_from_connection
        self.qu_to_interface = self.qu_to_interface
        self.kill = kill
        self.debug = debug
        self.is_autorun = run
        self.timeout = timeout
        self.cmds = self.get_cmds()
        Thread_tools.__init__(self)

    def get_cmds(self):
        """Return Commands - IDK why I did it this way, I just did.

        Could have passed it through as arg but that is boring.
        Layout:
            { Name: [Command, Function, [Args], Discription], }
        """
        return {"kill": ["£!:kill", self.kill_connnection, None, "Kill the program."],
                "print": ["£+:", self.relay_print, ["msg"], "Print a msg."],
                }

    def run(self):
        """Core Thread."""
        self.debug_msg("Running Core Thread.")
        self.incoming = Incoming() # Args
        self.outgoing = Outgoing() # Args
        self.incoming.join()
        self.outgoing.join()

    # Inherited methods - Both halves use them.
    def kill_connnection():
        """Kill the connection."""
        self.debug_msg("Killing the connection.")
        # @ the moment well kill all the threads :)
        self.kill.set()

    def remove_prefix(self, msg, cmd):
        """Remove the cmd prefix from msg.

        msg - The msg to remove the prefix from cmd from | string
        cmd - The command name of the prefix to remove from self.cmds | string

        """
        # May only be used by incoming?
        self.debug_msg("Remove prefix function called.")
        return msg[len(self.cmds[cmd][0]):]


class Incoming(Core):
    """Incoming data handler."""

    def __init__(self, in_queue, print_queue, kill, debug=True, run=True, timeout=5.0):
        """Initialization.

        in_queue - Incoming data queue object | object
        print_queue - Queue object for msgs to be show to user | object
        kill - Event object to kill thread | object
        debug - Print debug info | boolean
                / Defaults to True
        run - Autorun thread | boolean
                / Defaults to True
        timeout - Time to wait on blocking functions so able to check kill | float
                / Defaults to 5.0

        """
        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.print_queue = print_queue
        self.kill = kill
        self.debug = debug
        self.is_autorun = run
        self.timeout = timeout
        self.cmds = self.get_cmds()
        Thread_tools.__init__(self)

    def run(self):
        """Handler thread."""
        self.debug_msg("Running Incoming Data Handler.")
        while not self.kill.is_set():
            try:
                msg = self.in_queue.get(True, 5.0)
                # Check for commands
                for cmd in self.cmds:
                    if msg.startswith(self.cmds[cmd][0]):
                        args = []
                        # Check for args needed
                        if self.cmds[cmd][2]:
                            # go through args
                            for arg in self.cmds[cmd][2]:
                                # possible args
                                if arg == "msg":
                                    args.append(msg)
                        self.cmds[cmd][1](*args)
                        break
            except queue.Empty:
                pass

    def relay_print(self, msg):
        """Process and relay msg to print_queue.

        msg - The whole msg | string

        """
        self.debug_msg("Process and relay msg for print.")
        self.print_queue.put(self.remove_prefix(msg, "print"))

# We are here in clean up
class Interface(threading.Thread):
    """Interface class."""
    def __init__(self, msg_queue, kill, run=True):
        threading.Thread.__init__(self)
        self.msg_queue = msg_queue
        self.kill = kill
        if run:
            self.start()

    def run(self):
        while not self.kill.is_set():
            msg = input(">", 5.0)
            if msg == "-exit":
                self.msg_queue.put("$%KILL$%")
                self.kill.set()
            else:
                self.msg_queue.put(msg)
                time.sleep(0.05)

class Main():
    """Main functions as a class so threads could be shutdown."""
    def __init__(self):
        print("Loaded")

    def run(self):
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue()
        self.sockets = queue.Queue()
        self.kill = threading.Event()
        if True in args("-s", "--server"):
            self.server = networkTesting.Server(self.sockets, self.kill)
            self.socket = self.sockets.get()
        elif True in args("-c", "--client"):
            self.socket = networkTesting.connect()
        else:
            print("No args give. Terminating.")
            self.kill.set()
            exit()
        self.client = networkTesting.Client(self.socket, self.out_queue, self.in_queue, self.kill)
        self.interface = Interface(self.out_queue, self.kill)
        self.printer = Printer(self.in_queue, self.kill)



class TimeoutExpired(Exception):
    pass

_input = input
def input(prompt, timeout=None, timer=time.monotonic):
    if not timeout:
        return _input(prompt)
    else:
        sys.stdout.write(prompt)
        sys.stdout.flush()
        endtime = timer() + timeout
        result = []
        while timer() < endtime:
            if msvcrt.kbhit():
                result.append(msvcrt.getwche()) #XXX can it block on multibyte characters?
                if result[-1] == '\n':   #XXX check what Windows returns here
                    return ''.join(result[:-1])
                    time.sleep(0.04) # just to yield to other processes/threads
        raise TimeoutExpired

if __name__ == '__main__':
    main = Main()
    try:
        main.run()
    except Exception as e:
        main.kill.set()
        try:
            raise Exception
        except:
            pass
        print("=====================")
        print("---ERROR---")
        print(e)
        print(traceback.print_tb(e.__traceback__))
        print("=====================")
        exit()
