from subprocess import Popen, PIPE
from pagewalker.utilities import error_utils


class JavaChecker(object):
    def __init__(self, java_binary):
        self.java_binary = java_binary

    def is_installed(self):
        command_parts = [self.java_binary, "-version"]
        try:
            Popen(command_parts, stdout=PIPE, stderr=PIPE)
            return True
        except OSError:
            self._print_warning()
            return False

    def _print_warning(self):
        msg = "Java not found at location: %s" % self.java_binary
        msg += "\nDisabling HTML Validator."
        msg += "\nInstall/configure Java in your system to use HTML Validator."
        error_utils.show_warning(msg)
