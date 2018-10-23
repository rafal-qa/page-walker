import platform
import struct


version_info = (1, 0, 1)
version = '.'.join(str(c) for c in version_info)


def get_versions():
    return {
        "app": version,
        "python": platform.python_version(),
        "arch": struct.calcsize("P") * 8
    }
