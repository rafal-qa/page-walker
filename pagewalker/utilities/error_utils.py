import sys
from . import console_utils


def exit_with_message(message):
    print("")
    print("=" * 50)
    print("ERROR: %s" % message)
    print("=" * 50)
    print("")
    if console_utils.keep_open_console:
        console_utils.wait_confirm("Press 'Enter' to close.")
    sys.exit(1)


def socket_lost_connection():
    exit_with_message("Lost connection to Chrome remote debugger")


def show_warning(message):
    print("")
    print("-" * 50)
    print("WARNING: %s" % message)
    print("-" * 50)
    print("")
