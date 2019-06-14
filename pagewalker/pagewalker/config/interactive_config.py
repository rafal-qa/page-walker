import sys
from . import config_validator, config


class InteractiveConfig(object):
    def __init__(self):
        self._config_types = config_validator.ConfigValidatorInteractive()

    def ask_for_config_if_interactive_mode(self):
        if self._is_interactive():
            self._start_url()
            self._max_number_pages()
            self._mobile_emulation_enabled()
            self._chrome_headless()

    def _start_url(self):
        config.start_url = self._config_types.url(
            self._read_input("Start URL to test", config.start_url)
        )

    def _max_number_pages(self):
        config.max_number_pages = self._config_types.positive_non_zero_integer(
            self._read_input("Number of pages to visit", config.max_number_pages)
        )

    def _mobile_emulation_enabled(self):
        mobile_emulation_default = "y" if config.mobile_emulation_enabled else "n"
        config.mobile_emulation_enabled = self._config_types.boolean(
            self._read_input("Mobile emulation (y/n)", mobile_emulation_default)
        )

    def _chrome_headless(self):
        headless_default = "y" if config.chrome_headless else "n"
        config.chrome_headless = self._config_types.boolean(
            self._read_input("Headless mode (y/n)", headless_default)
        )

    def _is_interactive(self):
        return True if len(sys.argv) == 1 else False

    def _read_input(self, text, default=None):
        if default:
            prompt = "%s [%s]: " % (text, default)
        else:
            prompt = "%s: " % text
        value = input(prompt)
        if not value and default:
            return str(default)
        return value
