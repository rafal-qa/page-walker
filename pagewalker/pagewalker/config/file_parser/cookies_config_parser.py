from .ini_reader import INIReader
from .. import config_validator
from pagewalker.utilities import error_utils
from pagewalker.config import config


class CookiesConfigParser(INIReader):
    def __init__(self):
        super(CookiesConfigParser, self).__init__(config.custom_cookies_file)
        self.config_types = config_validator.ConfigValidatorCustomCookie()

    def apply(self):
        cookies_data = []
        for section in self._get_sections():
            cookies_data.append(self._single_cookie(section))
        if cookies_data:
            config.custom_cookies_data = cookies_data

    def _single_cookie(self, section):
        print("[INFO] Custom cookie: %s" % section)
        cookie = {}
        for name, value in self._get_non_empty_values(section).items():
            self._validate_allowed_option(name)
            if name in ["secure", "httponly"]:
                cookie[name] = self.config_types.boolean(value, name)
            else:
                cookie[name] = value
        self._validate_required_options(cookie, section)
        return cookie

    def _validate_allowed_option(self, option_name):
        allowed_options = ["name", "value", "domain", "path", "secure", "httponly"]
        if option_name not in allowed_options:
            msg = "Unknown option '%s' in config file '%s'" % (option_name, config.custom_cookies_file)
            error_utils.exit_with_message(msg)

    def _validate_required_options(self, cookie, section):
        required_options = ["name", "value"]
        for option in required_options:
            if option not in cookie:
                msg = "Missing '%s' option in [%s] cookie in config file '%s'" \
                      % (option, section, config.custom_cookies_file)
                error_utils.exit_with_message(msg)
