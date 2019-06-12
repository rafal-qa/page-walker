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
    exit(1)


def show_warning(message):
    print("")
    print(SEPARATOR)
    print("WARNING".center(50))
    print(message)
    print(SEPARATOR)
    print("")
