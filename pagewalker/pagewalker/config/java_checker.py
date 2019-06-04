from subprocess import Popen, PIPE
from pagewalker.utilities import error_utils
from pagewalker.config import config


class JavaChecker(object):
    def disable_validator_if_no_java(self):
        if not self._is_installed():
            config.validator_enabled = False

    def _is_installed(self):
        command_parts = [config.java_binary, "-version"]
        try:
            Popen(command_parts, stdout=PIPE, stderr=PIPE)
            return True
        except OSError:
            self._print_warning()
            return False

    def _print_warning(self):
        msg = "Java not found at location: %s" % config.java_binary
        msg += "\nHTML Validation will be omitted."
        msg += "\nInstall Java to use HTML Validator or disable it to not show this message."
        msg += "\nYou can provide custom Java location in file: %s (option 'java_binary')" % config.ini_file
        error_utils.show_warning(msg)
