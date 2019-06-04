from os import path
from .ini_reader import INIReader
from .. import config_validator
from pagewalker.utilities import error_utils
from pagewalker.config import config


class MainConfigParser(INIReader):
    def __init__(self):
        self._check_ini_file_exists()
        super(MainConfigParser, self).__init__(config.ini_file)

    def _check_ini_file_exists(self):
        if not path.exists(config.ini_file):
            error_utils.exit_with_message("File '%s' not found" % config.ini_file)

    def apply(self):
        config_types = config_validator.ConfigValidatorFile()
        validate_options = {
            "url": [
                "start_url", "initial_actions_url", "domain_blacklist_url"
            ],
            "positive_non_zero_integer": [
                "max_number_pages", "chrome_debugging_port", "chrome_timeout", "java_stack_size",
                "check_external_links_timeout", "check_external_links_threads"
            ],
            "positive_integer": [
                "wait_time_after_load", "domain_blacklist_cache_expiry"
            ],
            "boolean": [
                "scroll_after_load", "chrome_headless", "chrome_close_on_finish",
                "chrome_ignore_cert", "validator_enabled", "validator_check_css", "validator_show_warnings",
                "pages_list_only", "check_external_links", "domain_blacklist_enabled", "domain_blacklist_auto_update"
            ],
            "dimension": [
                "window_size"
            ],
            "file": [
                "pages_list_file", "custom_cookies_file", "initial_actions_file"
            ],
            "any": [
                "chrome_binary", "http_basic_auth_data", "validator_vnu_jar", "java_binary"
            ]
        }
        for name, value in self._get_non_empty_values("main").items():
            if name in validate_options["url"]:
                setattr(config, name, config_types.url(value, name))
            elif name in validate_options["positive_non_zero_integer"]:
                setattr(config, name, config_types.positive_non_zero_integer(value, name))
            elif name in validate_options["positive_integer"]:
                setattr(config, name, config_types.positive_integer(value, name))
            elif name in validate_options["boolean"]:
                setattr(config, name, config_types.boolean(value, name))
            elif name in validate_options["dimension"]:
                setattr(config, name, config_types.dimension(value, name))
            elif name in validate_options["file"]:
                setattr(config, name, config_types.file(value, name))
            elif name in validate_options["any"]:
                setattr(config, name, value)
            else:
                error_utils.exit_with_message("Unknown option '%s' in config file '%s'" % (name, config.ini_file))
