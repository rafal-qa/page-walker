import re
from argparse import ArgumentTypeError
from pagewalker.utilities import url_utils, error_utils


class ConfigValidator(object):
    def __init__(self, validation_mode):
        self.validation_mode = validation_mode

    def boolean(self, value, name=None):
        if value.lower() in ("y", "yes", "true", "1"):
            return True
        elif value.lower() in ("n", "no", "false", "0"):
            return False
        else:
            self._error("'%s' is not boolean value" % value, name)

    def positive_integer(self, value, name=None):
        if value.isdigit():
            return int(value)
        else:
            self._error("'%s' is not positive integer" % value, name)

    def positive_non_zero_integer(self, value, name=None):
        if value.isdigit() and value != "0":
            return int(value)
        else:
            self._error("'%s' is not positive non-zero integer" % value, name)

    def url(self, value, name=None):
        if not value:
            self._error("Start URL is required", name)
        if url_utils.has_valid_scheme(value, ["http", "https"]):
            return value
        else:
            self._error("'%s' is not valid URL" % value, name)

    def dimension(self, value, name=None):
        if re.match(r"^\d+x\d+$", value):
            return value
        else:
            self._error("'%s' is not in the format [width]x[height]" % value, name)

    def _error(self, message, name):
        if self.validation_mode == "argparse":
            raise ArgumentTypeError(message)
        elif self.validation_mode == "config":
            error_utils.exit_with_message("Invalid '%s' value in config file: %s " % (name, message))
        elif self.validation_mode == "interactive":
            error_utils.exit_with_message(message)
