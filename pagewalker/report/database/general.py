
class DatabaseGeneral(object):
    def __init__(self, conn):
        self.conn = conn

    def config_data(self):
        c = self.conn.cursor()
        c.execute(
            "SELECT option, value FROM config"
        )
        result = c.fetchall()
        data_config = {}
        for row in result:
            option, value = row
            data_config[option] = value
        return data_config

    def summary(self):
        c = self.conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM pages WHERE completion_status > 0"
        )
        data_summary = {
            "pages": c.fetchone()[0]
        }

        c.execute(
            "SELECT COUNT(*) FROM devtools_request"
        )
        data_summary["requests"] = c.fetchone()[0]

        c.execute(
            "SELECT SUM(data_received) FROM devtools_request"
        )
        data_summary["data_total"] = c.fetchone()[0]

        return data_summary
