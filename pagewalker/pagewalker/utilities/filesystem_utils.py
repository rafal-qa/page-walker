from os import path, makedirs
import shutil


def clean_directory(directory):
    if path.exists(directory):
        shutil.rmtree(directory)
    makedirs(directory)


def make_dir_if_not_exists(directory):
    if not path.exists(directory):
        makedirs(directory)


def try_make_dir(directory):
    makedirs(directory)


def get_full_directory_name(file_path):
    return path.dirname(path.realpath(file_path))
