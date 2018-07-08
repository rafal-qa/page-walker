import json


class DatabaseValidator(object):
    def __init__(self, conn):
        self.conn = conn
        self.extracts_used = None

    def messages(self, html_type_id):
        c = self.conn.cursor()
        c.execute("""
            SELECT V.message_id, COUNT(*), M.is_error, M.description
            FROM pages_validator AS V
            JOIN validator_messages AS M
                ON V.message_id = M.id
            WHERE V.html_type = ?
            GROUP BY V.message_id
        """, (html_type_id,))
        result = c.fetchall()
        data_messages = []
        for row in result:
            message_id, occurrences, is_error, description = row
            message_data = {
                "message_id": message_id,
                "occurrences": occurrences,
                "is_error": is_error,
                "message": description
            }
            data_messages.append(message_data)
        return data_messages

    def top_extract_for_message(self, html_type_id):
        c = self.conn.cursor()
        c.execute("""
            SELECT COUNT(*), V.message_id, E.extract_json
            FROM pages_validator AS V
            JOIN validator_extracts AS E
                ON V.extract_id = E.id
            WHERE V.html_type = ?
            GROUP BY V.message_id, V.extract_id
            ORDER BY COUNT(*) DESC
        """, (html_type_id,))
        result = c.fetchall()
        data_extracts = {}
        for row in result:
            count, message_id, extract_json = row
            if message_id not in data_extracts:
                data_extracts[message_id] = extract_json
        return data_extracts

    def extracts_and_pages_for_message(self, html_type_id):
        c = self.conn.cursor()
        c.execute("""
            SELECT V.page_id, V.message_id, V.extract_id, V.line, E.extract_json
            FROM pages_validator AS V
            JOIN validator_extracts AS E
                ON V.extract_id = E.id
            WHERE V.html_type = ?
            ORDER BY V.page_id
        """, (html_type_id,))
        result = c.fetchall()
        data_messages = {}
        self.extracts_used = []
        for row in result:
            self._append_page_info_to_messages(data_messages, row)
        return data_messages

    def _append_page_info_to_messages(self, messages, row):
        page_id, message_id, extract_id, line, extract_json = row

        if self._extract_used(message_id, extract_id, page_id):
            return

        if message_id not in messages:
            messages[message_id] = {}

        current_extracts_in_message = len(messages[message_id])
        max_extracts_per_message = 5
        if current_extracts_in_message >= max_extracts_per_message:
            return

        if extract_id not in messages[message_id]:
            messages[message_id][extract_id] = {
                "pages": [],
                "extract": json.loads(extract_json)
            }

        current_pages_in_extract = len(messages[message_id][extract_id]["pages"])
        max_pages_per_extract = 5
        if current_pages_in_extract < max_pages_per_extract:
            messages[message_id][extract_id]["pages"].append([page_id, line])

    # don't allow duplicate pages per one code sample
    # but allow duplicate pages per message, same page in different code samples
    def _extract_used(self, message_id, extract_id, page_id):
        used_page = "-".join(map(str, [message_id, extract_id, page_id]))
        if used_page in self.extracts_used:
            return True
        else:
            self.extracts_used.append(used_page)
            return False
