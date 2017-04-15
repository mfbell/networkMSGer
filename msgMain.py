"""MSG App Main Module.



Written by {0}
Version {1}
Status: {2}
Licensed under {3}
URL: {4}

"""

AUTHOR = "mtech0 | https://github.com/mtech0"
LICENSE = "GNU-GPLv3 | https://www.gnu.org/licenses/gpl.txt"
VERSION = "0.1.9"
STATUS = "Development"
URL = ""
__doc__ = __doc__.format(AUTHOR, VERSION, STATUS, LICENSE, URL)

#import threading
from queue import Queue
from threading import Event
import traceback # Error catching/debugging.
from tools import debug_msg, Tools, sys_args
import msgCore
import networkCore
if sys_args("-gui"):
    print("unsupported at the moment.")
    exit()
    #import msgGUI as ui
else:
    import msgCLI as ui

class Run(Tools):
    """Run the app."""

    def __init__(self):
        """Initialization."""
        self.argv_setup()
        Tools.__init__(self)

    def argv_setup(self):
        argv = sys_args()
        self.debug = True in sys_args("--debug", "-d")
        if sys_args("--timeout"):
            index = argv.index("--timeout") + 1
            self.timeout = float(argv[index])
        elif sys_args("-t"):
            index = argv.index("-t") + 1
            self.timeout = float(argv[index])
        else:
            self.timeout = 5.0
        self.server = True in sys_args("--server", "-s")
        # Interface modules import at import section. ui.
        self.is_autorun = True # Even though not used.
        if sys_args("--host"):
            index = argv.index("--host") + 1
            self.host = argv[index]
        elif sys_args("-h"):
            index = argv.index("-h") + 1
            self.host = argv[index]
        else:
            self.host = "localhost"
        if sys_args("--port"):
            index = argv.index("--port") + 1
            self.port = float(argv[index])
        elif sys_args("-p"):
            index = argv.index("-p") + 1
            self.port = float(argv[index])
        else:
            self.port = 3110

    def run(self):
        self.qu_interface = Queue()
        self.qu_inbound = Queue()
        self.qu_inputs = Queue()
        self.qu_outbound = Queue()
        self.sockets = Queue()
        self.kill = Event()
        if self.server:
            self.server = networkCore.Incoming_connections_handler(self.sockets, self.kill, port=self.port, debug=self.debug, timeout=self.timeout)
            self.socket = self.sockets.get()
        else:
            self.socket = networkCore.connect(self.host, self.port, self.debug)
        self.client = networkCore.Client(self.socket, self.qu_outbound, self.qu_inbound, self.kill, self.debug, timeout=self.timeout)
        self.core = msgCore.Core(self.qu_inputs, self.qu_outbound, self.qu_inbound, self.qu_interface, self.kill, self.debug, timeout=self.timeout)
        self.printer = ui.Printer(self.qu_interface, self.kill, self.debug, timeout=self.timeout)
        self.interface = ui.Interface(self.qu_inputs, self.kill, self.debug, timeout=self.timeout)
        self.client.join()
        self.printer.join()
        self.interface.join()
        print("Terminated")
        exit()


def main():
    if True in sys_args("--help", "-h"):
        print("""Usage: python .\msgMain [options]

Options:
    - Connection mode:
        Server or Client:
        Defaults to client, to run as server --server or -s
    - Interface:
        CLI or GUI:
        Defaults to CLI, -gui for GUI (not supported yet.)
    - Debug text:
        Defaults to false, to enable --debug or -d
    - Timeout/Thread kill responsiveness:
        Defaults to 5.0, to change --timeout <seconds> or -t <seconds>
    - Hostname to connect to:
        Defaults to localhost, to change --host <name> or -h <name>
    - Port to connect to or run listening server on:
        Defaults to 3110, to change --port <number> or -p <number>
Note: Only -d, -s and -c have been test and even they may have lot of bugs :)
If you find a bug please submit it to https://github.com/mtech0/networkMSGer/issues thanks.
""")
        exit()
    app = Run()
    try:
        app.run()
    except Exception as err:
        app.kill.set()
        try:
            raise Exception()
        except:
            pass
        traceback.print_tb(err.__traceback__)
        print(err)

if __name__ == '__main__':
    main()
