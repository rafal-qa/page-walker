from os import path
import shutil
import json
from pagewalker.utilities import filesystem_utils
from pagewalker.config import config


class HtmlExporterFiles(object):
    def __init__(self):
        self.report_dir = path.join(config.current_data_dir, "report")
        self.data_dir = path.join(self.report_dir, "data")

    def prepare_directory(self):
        self._copy_layout()
        filesystem_utils.make_dir_if_not_exists(self.data_dir)

    def _copy_layout(self):
        if path.exists(self.report_dir):
            shutil.rmtree(self.report_dir)
        template_dir = path.join(config.root, "pagewalker", "resources", "report_template")
        shutil.copytree(template_dir, self.report_dir)

    def save_json(self, db_data, data_name):
        javascript_data = []
        for key in db_data.keys():
            append = "var data_%s_%s = %s;" % (data_name, key, json.dumps(db_data[key]))
            javascript_data.append(append)

        file_name = "%s.js" % data_name
        file_path = path.join(self.data_dir, file_name)
        with open(file_path, "w") as f:
            f.write("\n".join(javascript_data))
