"""General Tools for networkMSGer.



Written by {0}
Version {1}
Status: {2}
Licensed under {3}
URL: {4}

"""

AUTHOR = "mtech0 | https://github.com/mtech0"
LICENSE = "GNU-GPLv3 | https://www.gnu.org/licenses/gpl.txt"
VERSION = "0.6.0"
STATUS = "Development"
URL = ""
__doc__ = __doc__.format(AUTHOR, VERSION, STATUS, LICENSE, URL)

# import errors

def debug_msg(debug, msg):
    """Debug message printer. if True.

    debug - Test | boolean or object to retrieve self.debug from
    msg - Msg to print | string
    """
    if isinstance(debug, (bool, int)):
        pass
    else:
        try:
            debug = debug.debug
        except NameError:
            raise NameError("Could not find self.debug in {0}".format(debug))
        except AttributeError:
            raise TypeError("Invalid Argument Type for 'debug': {0} ({1})".format(debug, type(debug)))
    if debug:
        print(msg)

class Tools():
    """General Tool class."""
    def __init__(self):
        """Initialization."""
        self.debug_msg(__doc__.splitlines[0][:-1], "initialized.")

    def debug_msg(self, msg):
        """Class rapper for debug_msg."""
        return debug_msg(self, msg)


class Thread_tools(Tools):
    """A set of thread class tools."""
    def __init__(self):
        """Initialization."""
        self.autorun()

    def autorun(self):
        """Autorun thread if self.is_autorun is True."""
        if self.is_autorun:
            self.start()

def main(doc=None, itu=None):
    """Module run as main function.

    doc - Either docstring or info to print | string
            / Defaults to 'README.md' file contents.
    itu - If to print "Import to use." at the end | boolean
            / Defaults to None
            / Behaviour:
                If doc=None and itu=None: itu=None
                If doc=None and itu=False: itu=False
                If doc=None and itu=True: itu=True
            --> If doc=True and itu=None: itu=True
                If doc=True and itu=False: itu=False
                If doc=True and itu=True: itu=True

    """
    if doc and itu == None:
        itu = True
    if not doc:
        doc = open("README.md", "r").read()
    print("\n" + doc)
    if itu:
        print("Import to use.")
    print()

if __name__ == '__main__':
    main(__doc__)
