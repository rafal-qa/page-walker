import time
from os import path
from subprocess import Popen
from pagewalker.utilities import filesystem_utils, error_utils
from pagewalker.config import config
from .browser_abstract import BrowserAbstract


class ChromeDesktop(BrowserAbstract):
    _log_file_name = "chrome_run.log"
    _subdir = "port_%s" % config.chrome_debugging_port
    _profile_dir = path.join(config.chrome_data_dir, _subdir)

    def _start_browser(self):
        self._check_chrome_binary_set()
        filesystem_utils.clean_directory(self._profile_dir)
        self._exec_command()

    def _check_chrome_binary_set(self):
        if not config.chrome_binary:
            self._chrome_not_found()

    def _exec_command(self):
        command_parts = self._build_command()
        log_file = path.join(config.current_data_dir, self._log_file_name)
        chrome_log = open(log_file, "w")
        try:
            Popen(command_parts, stdout=chrome_log, stderr=chrome_log)
        except OSError:
            self._chrome_not_found()

    def _build_command(self):
        window_size_command = config.window_size.replace("x", ",")
        command_parts = [
            config.chrome_binary,
            "--remote-debugging-port=%s" % config.chrome_debugging_port,
            "--window-size=%s" % window_size_command,
            "--no-first-run",
            "--user-data-dir=%s" % self._profile_dir
        ]
        if config.chrome_headless:
            command_parts.append("--headless")
            command_parts.append("--disable-gpu")
        if config.chrome_ignore_cert:
            command_parts.append("--ignore-certificate-errors")
        return command_parts

    def _chrome_not_found(self):
        if config.chrome_binary:
            message = "Chrome was not found at location: %s" % config.chrome_binary
        else:
            message = "Chrome was not found in your system"
        message += "\nFind location of Chrome/Chromium in your system and configure it in one of the ways:"
        message += "\n* file: %s (option 'chrome_binary')" % config.ini_file
        message += "\n* command line parameter: --chrome-binary"
        error_utils.exit_with_message(message)

    def _print_start_message(self):
        print("[INFO] Running Chrome Desktop, saving output to %s" % self._log_file_name)

    def close(self):
        self._devtools_protocol.send_browser_close()

    def close_previously_unclosed(self):
        msg = "Chrome Desktop instance is already running on port %s" % config.chrome_debugging_port
        msg += "\nClosing it now..."
        error_utils.show_warning(msg)
        self.close()
        time.sleep(5)
