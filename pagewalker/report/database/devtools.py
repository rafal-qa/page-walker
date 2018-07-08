
class DatabaseDevtools(object):
    def __init__(self, conn):
        self.conn = conn

    def log_list(self):
        c = self.conn.cursor()
        c.execute("""
            SELECT P.log_id, COUNT(*), L.level_id, L.source_id, L.description
            FROM pages_devtools_logs AS P
            JOIN devtools_logs AS L
                ON P.log_id = L.id
            GROUP BY P.log_id
        """)
        result = c.fetchall()
        data_logs = []
        for row in result:
            log_id, occurrences, level_id, source_id, description = row
            log_data = {
                "id": log_id,
                "occurrences": occurrences,
                "level_id": level_id,
                "source_id": source_id,
                "description": description
            }
            data_logs.append(log_data)
        return data_logs

    def pages_for_log(self):
        max_occurrences = 10
        c = self.conn.cursor()
        c.execute(
            "SELECT DISTINCT page_id, log_id FROM pages_devtools_logs ORDER BY page_id"
        )
        result = c.fetchall()
        data_logs = {}
        for row in result:
            page_id, log_id = row
            if log_id not in data_logs:
                data_logs[log_id] = []
            if len(data_logs[log_id]) < max_occurrences:
                data_logs[log_id].append(page_id)
        return data_logs
