"""Network Connections Core.

A module handling network connections.

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
URL = "None"
__doc__ = __doc__.format(AUTHOR, VERSION, STATUS, LICENSE, URL)


import socket
import threading
import queue
from tools import debug_msg, Tools, Thread_tools, main
import errors

class Incoming_connections_handler(threading.Thread, Thread_tools):
    """Incoming connections handler server."""

    def __init__(self, sockets, kill, host="", port=3110, max_connections=1, debug=True, run=True, timeout=5.0):
        """Initialization.

        sockets - Queue object | object
        kill - Event object to kill thread | object
        host - Hostname | string
                / Defaults to ""/Any interface.
        port - Port number | integer
                / Defaults to 3110
        max_connections - Maximim connections to handler | integer
                / Defaults to 1
        debug - Print debug info | boolean
                / Defaults to True
        run - Autorun thread | boolean
                / Defaults to True
        timeout - Time to wait on blocking functions so able to check kill | float
                / Defaults to 5.0

        """
        threading.Thread.__init__(self)
        self.sockets = sockets
        self.kill = kill
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.debug = debug
        self.timeout = timeout
        self.is_autorun = run
        Thread_tools.__init__(self)

    def run(self):
        """Run the server."""
        self.debug_msg("Incoming Connections Handler Server running.")
        s = socket.socket()
        s.bind((self.host, self.port))
        s.listen(self.max_connections)
        count = 0
        s.settimeout(self.timeout)
        while count < self.max_connections and not self.kill.is_set():
            try:
                conn, addr = s.accept()
                count += 1
                self.debug_msg("Connection from {0}, port {1}".format(*addr))
                self.sockets.put(conn)
            except socket.timeout:
                pass
        s.close()

def connect(host="localhost", port=3110, debug=True):
        """Connection Handler."""
        soc = socket.socket()
        soc.connect((host, port))
        debug_msg("Connected to {0}, port {1}".format(host, port))
        return soc

class Client(threading.Thread, Thread_tools):
    """Socket Client handler.

    Runs a full duplex socket automatically once started.

    """

    def __init__(self, socket, outgoing, incoming, kill, debug=True, run=True, timeout=5.0):
        """Initialization.

        socket - Socket object | object
        outoging - Queue for msgs to be sent | object
        incoming - Queue for msgs recieved | object
        kill - Event object to kill thread | object
        debug - Print debug info | boolean
                / Defaults to True
        run - Autorun thread | boolean
                / Defaults to True
        timeout - Time to wait on blocking functions so able to check kill | float
                / Defaults to 5.0

        """
        threading.Thread.__init__(self)
        self.soc = socket # Socket
        self.out = outgoing # Queue
        self.inc = incoming # Queue
        self.kill = kill # Event
        self.debug = debug
        self.is_run = run
        self.timeout = timeout
        self.soc.settimeout(self.timeout)
        self.header_st = "%N$T£H%"
        self.header_le = "%"
        self.header = self.header_st + "{0}" + self.header_le
        Thread_tools.__init__(self)

    def run(self):
        """Run the socket."""
        outgoing = Outgoing(self.soc, self.out, self.inc, self.kill, self.debug, True, self.timeout)
        incoming = Incoming(self.soc, self.out, self.inc, self.kill, self.debug, True, self.timeout)
        outgoing.join()
        incoming.join()
        self.soc.close()

class Outgoing(Client):
    """Outgoing Traffic Handler.

    Requires same arguments as Client.

    Can be run on its own to act as a half-duplex socket, however you may want
    to change that properly with the socket.

    """

    def run(self):
        """Run outgoing msgs on the socket."""
        while not self.kill.is_set():
            try:
                msg = self.out.get(True, self.timeout)
                data = self.header.format(len(msg)) + msg
                data_sent = 0
                while data_sent < len(data):
                    data_sent = self.soc.send(data[data_sent:].encode("utf-8"))
                self.out.task_done()
            except queue.Empty:
                pass

class Incoming(Client):
    """Incoming Traffic Handler.

    Requires same arguments as Client.

    Can be run on its own to act as a half-duplex socket, however you may want
    to change that properly with the socket.

    """

    def run(self):
        len_header_st = len(self.header_st)
        len_header_le = len(self.header_le)
        len_min_header = len_header_st + 1 + len_header_le
        data = ""
        while not self.kill.is_set():
            try:
                in_data = self.soc.recv(1028).decode("utf-8")
                if in_data:
                    data += in_data
                    if not data.startswith(self.header_st):
                        if len(data) > 20:
                            data_start = data[:20]
                        else:
                            data_start = data
                        raise errors.IncomingDataError("Incoming data error, data begins with '{0}', not {1}".format(data_start, self.header_st))
                    elif len(data) >= len_min_header:
                        pos = data[len_header_st:].find(self.header_le) + len_header_st
                        if pos == 0:
                            raise error.IncomingDataError("Incoming data error, data contains no length: {0}".format(data))
                        elif not pos == -1:
                            msg_length = int(data[len_header_st:pos])
                            len_attual_header = len_header_st + len(str(msg_length)) + len_header_le
                            len_total_msg = len_attual_header + msg_length
                            if len(data) >= len_total_msg:
                                msg = data[len_attual_header:len_total_msg]
                                data = data[len_total_msg:]
                                self.inc.put(msg)
            except socket.timeout:
                pass

if __name__ == '__main__':
    main(__doc__)
