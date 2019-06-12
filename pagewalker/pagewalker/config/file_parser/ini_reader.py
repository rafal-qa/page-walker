import configparser


class INIReader(object):
    def __init__(self, file_ini):
        parser = configparser.RawConfigParser()
        parser.read(file_ini)
        self.parser = parser

    def _get_sections(self):
        return self.parser.sections()

    def _get_non_empty_values(self, section):
        values = {}
        for name, value in self.parser.items(section):
            if not value == '':
                values[name] = value
        return values
