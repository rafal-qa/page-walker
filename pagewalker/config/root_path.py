import sys
import os
from os.path import dirname


def get():
    is_compiled = getattr(sys, 'frozen', False)
    return _get_from_compiled() if is_compiled else _get_from_source_code()


def _get_from_source_code():
    file_path = os.path.abspath(__file__)
    root_path = dirname(dirname(dirname(file_path)))
    return root_path


def _get_from_compiled():
    return sys._MEIPASS
