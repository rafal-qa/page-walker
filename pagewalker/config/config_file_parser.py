import os
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
from . import config_validator
from pagewalker.utilities import error_utils
from pagewalker.config import config


class ConfigFileParser(object):
    def __init__(self):
        if not os.path.isfile(config.ini_file):
            error_utils.exit_with_message("Config file '%s' not found" % config.ini_file)
        parser = configparser.ConfigParser()
        parser.read(config.ini_file)
        self.parser = parser

    def apply(self):
        config_types = config_validator.ConfigValidator("config")
        validate = {
            "url": [
                "start_url"
            ],
            "positive_non_zero_integer": [
                "max_number_pages", "chrome_debugging_port", "chrome_timeout", "java_stack_size",
                "check_external_links_timeout"
            ],
            "positive_integer": [
                "wait_time_after_load"
            ],
            "boolean": [
                "scroll_after_load", "keep_previous_data", "chrome_headless", "chrome_close_on_finish",
                "chrome_ignore_cert", "validator_enabled", "validator_check_css", "validator_show_warnings",
                "pages_list_only", "check_external_links"
            ],
            "dimension": [
                "window_size"
            ]
        }
        for name, value in self._get_non_empty_values():
            if name in validate["url"]:
                setattr(config, name, config_types.url(value, name))
            elif name in validate["positive_non_zero_integer"]:
                setattr(config, name, config_types.positive_non_zero_integer(value, name))
            elif name in validate["positive_integer"]:
                setattr(config, name, config_types.positive_integer(value, name))
            elif name in validate["boolean"]:
                setattr(config, name, config_types.boolean(value, name))
            elif name in validate["dimension"]:
                setattr(config, name, config_types.dimension(value, name))
            else:
                setattr(config, name, value)

    def _get_non_empty_values(self):
        values = {}
        for name, value in self.parser.items("main"):
            if not value == '':
                values[name] = value
        return values.items()
