import sys
import platform


interactive_mode = True if len(sys.argv) == 1 else False
is_compiled = getattr(sys, 'frozen', False)
keep_open_console = interactive_mode and platform.system() == "Windows" and is_compiled


def read_input(text, default=None):
    if default:
        prompt = "%s [%s]: " % (text, default)
    else:
        prompt = "%s: " % text
    if sys.version_info[0] > 2:
        value = input(prompt)
    else:
        value = raw_input(prompt)
    if not value and default:
        return str(default)
    return value


def wait_confirm(text):
    if sys.version_info[0] > 2:
        input(text)
    else:
        raw_input(text)


def finish(terminate=False):
    if keep_open_console:
        print("")
        wait_confirm("Press 'Enter' to close.")
    if terminate:
        sys.exit()
