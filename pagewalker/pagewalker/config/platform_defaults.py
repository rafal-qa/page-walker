from abc import ABCMeta, abstractmethod
import platform


class SystemAbstract(metaclass=ABCMeta):
    @property
    @abstractmethod
    def java_binary(self):
        pass

    @property
    @abstractmethod
    def chrome_binary(self):
        pass

    @property
    @abstractmethod
    def adb_binary_file(self):
        pass


class Windows(SystemAbstract):
    @property
    def java_binary(self):
        return "Java"

    @property
    def chrome_binary(self):
        from pagewalker.utilities import windows_registry
        registry = windows_registry.WindowsRegistry()
        return registry.chrome_exe_path()

    @property
    def adb_binary_file(self):
        return "adb.exe"


class MacOS(SystemAbstract):
    @property
    def java_binary(self):
        return "java"

    @property
    def chrome_binary(self):
        return "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    @property
    def adb_binary_file(self):
        return "adb"


class Linux(SystemAbstract):
    @property
    def java_binary(self):
        return "java"

    @property
    def chrome_binary(self):
        return "google-chrome"

    @property
    def adb_binary_file(self):
        return "adb"


os_type = platform.system()
if os_type == "Windows":
    defaults = Windows()
elif os_type == "Darwin":
    defaults = MacOS()
else:
    defaults = Linux()

java_binary = defaults.java_binary
chrome_binary = defaults.chrome_binary
adb_binary_file = defaults.adb_binary_file
