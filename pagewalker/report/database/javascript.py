
class DatabaseJavascript(object):
    def __init__(self, conn):
        self.conn = conn

    def exception_list(self):
        c = self.conn.cursor()
        c.execute("""
            SELECT P.exception_id, COUNT(*), E.description
            FROM pages_js_exceptions AS P
            JOIN js_exceptions AS E
                ON P.exception_id = E.id
            GROUP BY P.exception_id
        """)
        result = c.fetchall()
        data_list = []
        for row in result:
            log_id, occurrences, description = row
            append_row = {
                "id": log_id,
                "occurrences": occurrences,
                "description": description
            }
            data_list.append(append_row)
        return data_list

    def pages_for_exception(self):
        max_occurrences = 10
        c = self.conn.cursor()
        c.execute(
            "SELECT DISTINCT page_id, exception_id FROM pages_js_exceptions"
        )
        result = c.fetchall()
        data_dict = {}
        for row in result:
            page_id, exception_id = row
            if exception_id not in data_dict:
                data_dict[exception_id] = []
            if len(data_dict[exception_id]) < max_occurrences:
                data_dict[exception_id].append(page_id)
        return data_dict
