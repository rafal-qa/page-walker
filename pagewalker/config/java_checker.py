from subprocess import Popen, PIPE
from . import config_validator
from pagewalker.utilities import console_utils, error_utils


class JavaChecker(object):
    def __init__(self, java_binary):
        self.java_binary = java_binary
        self.continue_with_no_java = False
        self._check()

    def _check(self):
        command_parts = [self.java_binary, "-version"]
        try:
            Popen(command_parts, stdout=PIPE, stderr=PIPE)
        except OSError:
            self._not_found()

    def _not_found(self):
        msg = "Java not found, program '%s' failed" % self.java_binary
        msg += "\nInstall Java or disable HTML Validator"
        if console_utils.interactive_mode:
            config_types = config_validator.ConfigValidator("interactive")
            error_utils.show_warning(msg)
            self.continue_with_no_java = config_types.boolean(
                console_utils.read_input("Continue with disabled HTML Validator? (y/n)", "y")
            )
            if not self.continue_with_no_java:
                console_utils.finish(True)
        else:
            error_utils.exit_with_message(msg)
