
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
            "SELECT COUNT(*) FROM pages WHERE status > 0"
        )
        data_summary = {
            "pages": c.fetchone()[0]
        }

        c.execute(
            "SELECT COUNT(*) FROM requests"
        )
        data_summary["requests"] = c.fetchone()[0]

        c.execute(
            "SELECT SUM(data_received) FROM requests"
        )
        data_summary["data_total"] = c.fetchone()[0]

        return data_summary
