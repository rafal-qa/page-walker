import sys
from pagewalker.config import config
from . import console_utils

SEPARATOR = "=" * 50


def exit_with_message(message):
    print("")
    print(SEPARATOR)
    print("ERROR".center(50))
    print(message)
    print(SEPARATOR)
    print("")
    if console_utils.keep_open_console:
        console_utils.wait_confirm("Press 'Enter' to close.")
    sys.exit(1)


def socket_lost_connection():
    exit_with_message("Lost connection to Chrome remote debugger")


def chrome_not_found(location=None):
    if location:
        message = "Chrome was not found at location: %s" % location
    else:
        message = "Chrome was not found in your system"
    message += "\nFind location of Chrome/Chromium in your system and configure it in one of the ways:"
    message += "\n* file: %s (option 'chrome_binary')" % config.ini_file
    message += "\n* command line parameter: --chrome-binary"
    exit_with_message(message)


def show_warning(message):
    print("")
    print(SEPARATOR)
    print("WARNING".center(50))
    print(message)
    print(SEPARATOR)
    print("")
