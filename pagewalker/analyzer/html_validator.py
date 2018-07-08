import json
import re
import os
from subprocess import Popen, PIPE
from pagewalker.utilities import filesystem_utils, error_utils


class HtmlValidator(object):
    def __init__(self, enabled, jar, html_dir, check_css, show_warnings, java_binary, java_stack):
        self.enabled = enabled
        self.jar = jar
        self.html_dir = html_dir
        self.java = java_binary
        self.db_conn = None
        self.queue_current_size = 0
        self.queue_max_size = 40
        self.vnu_version = ""

        if not self.enabled:
            return

        self.vnu_version = self._check_vnu()

        stack_size = "-Xss%sk" % java_stack
        command_parts = [self.java, stack_size, "-jar", self.jar, "--format", "json", "--exit-zero-always"]
        if check_css:
            command_parts.append("--also-check-css")
        if not show_warnings:
            command_parts.append("--errors-only")
        command_parts.append(self.html_dir)
        self.vnu_command_parts = command_parts

        filesystem_utils.clean_directory(self.html_dir)

    def _check_vnu(self):
        command_parts = [self.java, "-jar", self.jar, "--version"]
        p = Popen(command_parts, stdout=PIPE, stderr=PIPE)
        (out, err) = p.communicate()
        if p.returncode == 0:
            return self._popen_decode(out)
        else:
            error_utils.exit_with_message("v.Nu failed | %s" % self._popen_decode(err))

    def set_db_connection(self, db_connection):
        self.db_conn = db_connection

    def add_to_queue(self, page_id, html_raw, html_dom):
        if not self.enabled:
            return
        self._save_html_to_file(page_id, "raw", html_raw)
        self._save_html_to_file(page_id, "dom", html_dom)
        self.queue_current_size += 2

    def validate_if_full_queue(self):
        if self.queue_current_size >= self.queue_max_size:
            self.validate()

    def validate(self):
        if not self.enabled:
            return
        logs = self._execute_vnu()
        self._save_result_to_database(logs)

    def _execute_vnu(self):
        if self.queue_current_size == 0:
            return []
        print("[INFO] Running HTML validator on %s files" % self.queue_current_size)
        parsed = json.loads(self._get_vnu_json_result())
        logs = []
        for msg in parsed["messages"]:
            logs.append(self._parse_output_message(msg))
        filesystem_utils.clean_directory(self.html_dir)
        self.queue_current_size = 0
        return logs

    # option "exit-zero-always" was used, but still need to read from "stderr" not "stdout" (this is how v.Nu works)
    def _get_vnu_json_result(self):
        p = Popen(self.vnu_command_parts, stdout=PIPE, stderr=PIPE)
        (out, err) = p.communicate()
        if p.returncode == 0:
            return self._popen_decode(err)
        else:
            msg = "v.Nu failed\n%s %s" % (self._popen_decode(out), self._popen_decode(err))
            error_utils.exit_with_message(msg)

    def _save_result_to_database(self, logs):
        c = self.db_conn.cursor()
        for log in logs:
            message_id = self._get_message_id(log["is_error"], log["description"])
            extract_id = self._get_extract_id(log["extract_json"])
            c.execute(
                "INSERT INTO pages_validator (page_id, message_id, extract_id, line, html_type) VALUES (?,?,?,?,?)",
                (log["page_id"], message_id, extract_id, log["line"], log["html_type_id"])
            )
        self.db_conn.commit()

    def _get_message_id(self, is_error, description):
        c = self.db_conn.cursor()
        c.execute(
            "SELECT id FROM validator_messages WHERE is_error = ? AND description = ?", (is_error, description)
        )
        result = c.fetchone()
        if result:
            message_id = result[0]
        else:
            c.execute(
                "INSERT INTO validator_messages (is_error, description) VALUES (?, ?)", (is_error, description)
            )
            message_id = c.lastrowid
        return message_id

    def _get_extract_id(self, extract_json):
        c = self.db_conn.cursor()
        c.execute(
            "SELECT id FROM validator_extracts WHERE extract_json = ?", (extract_json,)
        )
        result = c.fetchone()
        if result:
            extract_id = result[0]
        else:
            c.execute(
                "INSERT INTO validator_extracts (extract_json) VALUES (?)", (extract_json,)
            )
            extract_id = c.lastrowid
        return extract_id

    def _save_html_to_file(self, page_id, html_type, html):
        file_name = "code_%s_%s.html" % (page_id, html_type)
        file_path = os.path.join(self.html_dir, file_name)
        html = html.encode('utf-8')
        with open(file_path, "wb") as f:
            f.write(html)

    def _parse_output_message(self, msg):
        match = re.findall("code_(\d+)_(raw|dom).html", msg["url"])
        page_id = int(match[0][0])
        html_type_name = match[0][1]
        extract_parts = self._split_extract(msg)
        html_types = {
            "raw": 1,
            "dom": 2
        }
        return {
            "is_error": 1 if msg["type"] == "error" else 0,
            "line": msg["lastLine"] if "lastLine" in msg else 0,
            "extract_json": json.dumps(extract_parts),
            "description": self._replace_unicode_quotes(msg["message"]),
            "page_id": page_id,
            "html_type_id": html_types[html_type_name]
        }

    def _replace_unicode_quotes(self, text):
        open_quote = u'\u201c'
        close_quote = u'\u201d'
        return text.replace(open_quote, '{').replace(close_quote, '}')

    def _split_extract(self, msg):
        extract = msg["extract"] if "extract" in msg else ""
        start = msg["hiliteStart"] if "hiliteStart" in msg else 0
        end = start + msg["hiliteLength"] if "hiliteLength" in msg else 0
        part_before = extract[:start]
        part_hilite = extract[start:end]
        part_after = extract[end:]
        extract_parts = [part_before, part_hilite, part_after]
        return extract_parts

    def get_vnu_version(self):
        return self.vnu_version

    def _popen_decode(self, output):
        return output.decode('utf-8', 'ignore').strip()
