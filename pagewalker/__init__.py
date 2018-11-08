import platform
import struct
from pagewalker.utilities import console_utils


version_info = (1, 0, 1)
version = '.'.join(str(c) for c in version_info)


def print_version():
    arch = struct.calcsize("P") * 8
    print("Page Walker: %s" % version)
    print("Python: %s (%s-bit)" % (platform.python_version(), arch))
    console_utils.finish(True)
