from os import path
from pagewalker.utilities import filesystem_utils, time_utils


class PrepareDirectories(object):
    def __init__(self, output_data, keep_previous):
        self.output_data = output_data
        self.keep_previous = keep_previous
        self.current_subdir = time_utils.current_date_time_safe_precise()
        self.current = path.join(output_data, self.current_subdir)

    def create(self):
        if not self.keep_previous:
            filesystem_utils.clean_directory(self.output_data)
        filesystem_utils.try_make_dir(self.current)

    def get_current_dir(self):
        return self.current

    def get_current_subdir(self):
        return self.current_subdir
