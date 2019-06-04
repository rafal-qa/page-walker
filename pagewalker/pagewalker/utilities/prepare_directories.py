from os import path
from pagewalker.utilities import filesystem_utils, time_utils
from pagewalker.config import config


class PrepareDirectories(object):
    def __init__(self):
        self.current_subdir = time_utils.current_date_time_safe_precise()
        self.current = path.join(config.output_data, self.current_subdir)

    def create(self):
        filesystem_utils.try_make_dir(self.current)
        config.current_data_dir = self.current
        config.current_data_subdir = self.current_subdir
