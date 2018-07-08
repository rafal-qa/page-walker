import sqlite3
from . import general, javascript, devtools, page, validator, resource


class DatabaseReader(object):
    def __init__(self, db_file):
        conn = sqlite3.connect(db_file)
        self.conn = conn
        self.general_data = general.DatabaseGeneral(conn)
        self.page_data = page.DatabasePage(conn)
        self.resource_data = resource.DatabaseResource(conn)
        self.javascript_data = javascript.DatabaseJavascript(conn)
        self.devtools_data = devtools.DatabaseDevtools(conn)
        self.validator_data = validator.DatabaseValidator(conn)

    def close(self):
        self.conn.close()
