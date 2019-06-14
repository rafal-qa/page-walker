import sys

SEPARATOR = "=" * 50


def exit_with_message(message):
    print("")
    print(SEPARATOR)
    print("ERROR".center(50))
    print(message)
    print(SEPARATOR)
    print("")
    sys.exit(1)


def show_warning(message):
    print("")
    print(SEPARATOR)
    print("WARNING".center(50))
    print(message)
    print(SEPARATOR)
    print("")
