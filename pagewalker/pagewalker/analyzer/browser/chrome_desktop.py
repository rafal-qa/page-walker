from os import path
from subprocess import Popen
from pagewalker.utilities import filesystem_utils, error_utils
from pagewalker.config import config
from .browser import Browser


class ChromeDesktop(Browser):
    def __init__(self):
        self.log_file_name = "chrome_run.log"
        subdir = "port_%s" % config.chrome_debugging_port
        self.profile_dir = path.join(config.chrome_data_dir, subdir)

    def run(self):
        self._check_chrome_binary_set()
        filesystem_utils.clean_directory(self.profile_dir)
        self._exec_command()
        self._print_start_message()

    def _check_chrome_binary_set(self):
        if not config.chrome_binary:
            self._chrome_not_found()

    def _exec_command(self):
        command_parts = self._build_command()
        log_file = path.join(config.current_data_dir, self.log_file_name)
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
            "--user-data-dir=%s" % self.profile_dir
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
        print("[INFO] Running Chrome Desktop, saving output to %s" % self.log_file_name)
