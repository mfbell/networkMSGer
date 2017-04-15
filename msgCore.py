"""MSG App Core.



Written by {0}
Version {1}
Status: {2}
Licensed under {3}
URL: {4}

"""

AUTHOR = "mtech0 | https://github.com/mtech0"
LICENSE = "GNU-GPLv3 | https://www.gnu.org/licenses/gpl.txt"
VERSION = "0.9.5"
STATUS = "Development"
URL = ""
__doc__ = __doc__.format(AUTHOR, VERSION, STATUS, LICENSE, URL)

import threading
import queue
from tools import debug_msg, Thread_tools, main

class Core(threading.Thread, Thread_tools):
    """The Core of msgCore.py."""

    def __init__(self, qu_inputs, qu_outbound, qu_inbound, qu_interface, kill, debug=True, run=True, timeout=5.0):
        """Initialization.

        qu_inputs - User input queue object | object
        qu_outbound - Outbound data queue object | object
        qu_inbound - Inbound data queue object | object
        qu_interface - User interface display queue object | object
        kill - Event object to kill thread | object
        debug - Print debug info | boolean
                / Defaults to True
        run - Autorun thread | boolean
                / Defaults to True
        timeout - Time to wait on blocking functions so able to check kill | float
                / Defaults to 5.0

        """
        threading.Thread.__init__(self)
        #self.interface = interface # What is this? The interface object or a queue to send cmds down???
        self.qu_inputs = qu_inputs
        self.qu_outbound = qu_outbound
        self.qu_inbound = qu_inbound
        self.qu_interface = qu_interface
        self.kill = kill
        self.debug = debug
        self.is_autorun = run
        self.timeout = timeout
        self.cmd_handler("--setup", "--bypass-arg-aliases")
        Thread_tools.__init__(self)

    def run(self):
        """Core Thread."""
        self.debug_msg("Running Core Thread.")
        self.incoming = Incoming(self.qu_inputs, self.qu_outbound, self.qu_inbound, self.qu_interface, self.kill, self.debug, self.is_autorun, self.timeout)
        self.outgoing = Outgoing(self.qu_inputs, self.qu_outbound, self.qu_inbound, self.qu_interface, self.kill, self.debug, self.is_autorun, self.timeout)
        self.incoming.join()
        self.outgoing.join()

    def cmd_handler(self, *args):
        """Command Handler.

        *args - Arguments:
                "--setup" - Setup commands.
                "--help" [cmd-alias] - return help [on cmd]

        """
        if not "--bypass-arg-aliases" in args:
            try:
                args = self.correct_aliases(*args)
            except NameError:
                self.cmd_handler("--setup", "--bypass-arg-aliases")
                args = self.correct_aliases(*args)
        if "--setup" in args:
            """
            Setup.
            """
            # System commands
            # {Name: [Command, Function, [Args], Discription], ...}
            self.sys_cmds = {"kill": ["£!:kill", self.kill_connnection, [], "Kill the connection."],
                             "print": ["£+:", self.relay_print, ["msg"], "Print a msg."], # Also send
                             "echo": ["£!:echo:", self.echo, ["msg"], "Echo a msg back to sender."]
                             }
            # User commands
            # {Name: [[cmd-aliases], Function, [Args], Discription], ...}
            self.usr_cmds = {"kill": [["kill"], self.kill_connnection, ["--send"], "Kill the connection."],
                             "help": [["help", "h"], self.cmd_help, ["msg"], "Show help."],
                             "echo": [["echo", "e"], self.echo, ["msg"], "Send an echo."],
                             "commands": [["commands"], self.show_commands, ["msg"], "Show all commands."],
                             }
            # User command prefix
            self.prefix = "-" # Need to change to a function for runtime updating accross threads.
            # Command arg aliases
            # {arg: [aliases], ...}
            self.cmd_args = {"--setup": None,
                            "--help": None,
                            "--bypass-arg-aliases": None,
                            "--send": ["-s"],
                            }
            # Inverting command arg aliases.
            self.cmd_args_alias = {}
            for arg in self.cmd_args:
                if self.cmd_args[arg]:
                    for alias in self.cmd_args[arg]:
                        self.cmd_args_alias[alias] = arg

        if "--help" in args:
            amount_of_args = len(args)
            pos = args.index("--help") + 1
            self.debug_msg("in cmd_handler\ngiven {0}".format(args))
            if pos + 1 <= amount_of_args:
                self.debug_msg("pos + 1 <= amount_of_args: True")
                cmd = args[pos]
                if cmd.startswith(self.prefix):
                    cmd = cmd[len(self.prefix):]
                self.debug_msg("cmd: {0}".format(cmd))
                found = False
                for cmd_ in self.usr_cmds:
                    self.debug_msg("Is cmd: {0}?".format(cmd_))
                    for alias in self.usr_cmds[cmd_][0]:
                        self.debug_msg("Is alias: {0}?".format(alias))
                        if cmd == alias:
                            found = True
                            return self.usr_cmds[cmd_][1]("--help")
                if not found:
                    self.debug_msg("not found: {0}".format(cmd))
                    return "Unknown command. Try '{0}commands' to get a list of commands.".format(self.prefix)
            else:
                self.debug_msg("just --help")
                return "To get help on a command: '{0}help <command>'.\nFor a list of commands: '{0}commands'".format(self.prefix)

    # Commands
    def show_commands(self, *args):
        """Display all the commands.

        msg - Full command string | string
        *args/msg: Arguments:
                "--help" return help

        """
        args = self.correct_aliases(*args)
        if "--help" in args:
            return "Command '{0}commands' displays all aviable commands.".format(self.prefix)
        discp = "short"
        if args:
            msg = args[0]
            parts = msg.split()
            if True in [parts[0] == self.prefix + alias for alias in self.usr_cmds["commands"][0]]:
                if len(parts) >= 2:
                    discp = parts[1]
            else:
                discp = parts[0]
        to_show = ["Name: Aliases | Info"]
        for cmd in self.usr_cmds:
            if discp == "full":
                info = self.cmd_handler("--help", self.usr_cmds[cmd][0][0])
            else:
                info = self.usr_cmds[cmd][3]
            to_show.append("{0}: {1} | {2}".format(cmd, self.usr_cmds[cmd][0], info))
        self.relay_print("\n".join(to_show))

    def kill_connnection(self, *args):
        """Kill the connection.

        *args: Arguments:
                "--help" return help
        """
        args = self.correct_aliases(*args)
        if "--help" in args:
            return "Command '{0}kill' kills the current connection.".format(self.prefix)
        if "--send" in args:
            self.send_msg(self.add_cmd_prefix("", "kill"))
        self.debug_msg("Killing the connection.")
        # @ the moment well kill all the threads :)
        self.kill.set()

    def relay_print(self, msg, *args):
        """Process and relay msg to print_queue.

        msg - The whole msg | string
        *args/msg: Arguments:
                "--help" return help

        """
        args = self.correct_aliases(msg, *args)
        if "--help" in args:
            return "System command, idk how you got this to show in the interface.\nSend a msg to interface queue."
        self.debug_msg("Process and relay msg for print.")
        if msg.startswith(self.sys_cmds["print"][0]):
            msg = msg[len(self.sys_cmds["print"][0]):]
        self.qu_interface.put(msg)

    def send_msg(self, msg, *args):
        """Send msg to outbound queue.

        msg - String to send to outbound queue | string
        *args/msg: Arguments:
                "--help" return help

        """
        args = self.correct_aliases(msg, *args)
        if "--help" in args:
            return "System command, idk how you got this to show in the interface.\nSend a msg to outbound queue."
        self.debug_msg("Adding msg to outbound queue")
        self.qu_outbound.put(msg)

    def cmd_help(self, *args):
        """Displays user command help.

        msg - A command to get help on | string
                / If not given, will show general help.
                / Can pass full command.
        *args/msg: Arguments:
                "--help" return help

        """
        args = self.correct_aliases(*args)
        if "--help" in args:
            return self.cmd_handler("--help")
        if args:
            self.debug_msg("cmd_help has been give args")
            msg = args[0]
            if True in [msg.startswith(self.prefix + alias) for alias in self.usr_cmds["help"][0]]:
                self.debug_msg("msg begins with -help")
                cmd = msg.split()
                if len(cmd) >= 2:
                    self.debug_msg("is more than -help: {0}".format(cmd))
                    info = self.cmd_handler("--help", cmd[1])
                else:
                    self.debug_msg("only -help")
                    info = self.cmd_handler("--help")
            else:
                self.debug_msg("Passed a command: {0}".format(msg))
                info = self.cmd_handler("--help", msg)
        else:
            self.debug_msg("no args passed.")
            info = self.cmd_handler("--help")
        self.relay_print(info)

    def echo(self, msg, *args):
        """Echo a message.

        msg - Full command string | string
        *args/msg: Arguments:
                "--help" return help

        """
        args = self.correct_aliases(msg, *args)
        if "--help" in args:
            return "Command '{0}echo <msg>' echos msg.".format(self.prefix)
        if msg.startswith(self.sys_cmds["echo"][0]):
            msg = self.remove_cmd_prefix(msg, "echo")
            self.qu_interface.put("Connection echoed '{0}'".format(msg))
            self.send_msg(self.add_cmd_prefix(msg, "print"))
        else:
            pos = msg.find(" ") + 1
            msg = msg[pos:]
            self.send_msg(self.add_cmd_prefix(msg, "echo"))

    # Tools
    def remove_cmd_prefix(self, msg, cmd):
        """Remove the cmd prefix from msg.

        msg - The msg to remove the prefix from cmd from | string
        cmd - The command name of the prefix to remove from self.sys_cmds | string

        """
        self.debug_msg("Remove prefix function called.")
        return msg[len(self.sys_cmds[cmd][0]):]

    def add_cmd_prefix(self, msg, cmd):
        """Add the cmd prefix to msg.

        msg - The msg to add the prefix from cmd to | string
        cmd - The command name of the prefix to add from self.sys_cmds | string

        """
        return self.sys_cmds[cmd][0] + msg

    def correct_aliases(self, *args):
        """Turn aliases into full arg.

        *args - Any amount of aliases and/or args | Strings

        """
        re = []
        for arg in args:
            if arg in self.cmd_args_alias:
                re.append(self.cmd_args_alias[arg])
            else:
                re.append(arg)
        return re

class Incoming(Core):
    """Incoming data handler.

    Requires the same arguments as Core.

    """

    def run(self):
        """Handler thread."""
        self.debug_msg("Running Incoming Data Handler.")
        while not self.kill.is_set():
            try:
                msg = self.qu_inbound.get(True, self.timeout)
                # Check for commands
                for cmd in self.sys_cmds:
                    if msg.startswith(self.sys_cmds[cmd][0]):
                        args = []
                        # Check for args needed
                        if self.sys_cmds[cmd][2]:
                            # go through args
                            for arg in self.sys_cmds[cmd][2]:
                                # possible args
                                if arg == "msg":
                                    args.append(msg)
                                # Insert others before here.
                                # Passing flags
                                elif isinstance(arg, str):
                                    args.append(arg)
                        self.sys_cmds[cmd][1](*args)
                        break
            except queue.Empty:
                pass


class Outgoing(Core):
    """User input and outgoing data handler.

    Requires the same arguments as Core.

    """

    def run(self):
        """Handler thread."""
        self.debug_msg("Outgoing data handler running.")
        while not self.kill.is_set():
            try:
                msg = self.qu_inputs.get(True, self.timeout)
                # is user cmd?
                self.debug_msg("Revieved: {0}".format(msg))
                if msg.startswith(self.prefix):
                    self.debug_msg("Is command.")
                    # display help = not found
                    found = False
                    # check for cmd
                    for cmd in self.usr_cmds:
                        self.debug_msg("Is command {0}?".format(cmd))
                        for alias in self.usr_cmds[cmd][0]:
                            self.debug_msg("Alias: {0}?".format(alias))
                            if msg == self.prefix + alias or msg.startswith(self.prefix + alias + " "):
                                self.debug_msg("Alias matched command.")
                                found = True
                                args = []
                                # go through args
                                if self.usr_cmds[cmd][2]:
                                    for arg in self.usr_cmds[cmd][2]:
                                        # possible args
                                        if arg == "msg":
                                            args.append(msg)
                                        # Insert others before here.
                                        # Passing flags
                                        elif isinstance(arg, str):
                                            args.append(arg)
                                self.usr_cmds[cmd][1](*args)
                                break
                        if found:
                            break
                    # usr cmd help
                    if not found:
                        self.cmd_help(msg)
                # just msg
                else:
                    self.send_msg(self.add_cmd_prefix(msg, "print"))
            except queue.Empty:
                pass


if __name__ == '__main__':
    main(__doc__)
