
class DatabaseResource(object):
    def __init__(self, conn):
        self.conn = conn

    def resource_list_only(self):
        c = self.conn.cursor()
        c.execute("""
            SELECT DISTINCT RS.id, RS.url, RS.is_truncated, RS.is_external
            FROM devtools_request AS RQ
            JOIN devtools_resource AS RS
                ON RQ.resource_id = RS.id
            WHERE RQ.is_main = 0
        """)
        result = c.fetchall()
        data_resources = []
        for row in result:
            resource_id, url, is_truncated, is_external = row
            resource_data = {
                "id": resource_id,
                "url": url,
                "is_truncated": is_truncated,
                "is_external": is_external
            }
            data_resources.append(resource_data)
        return data_resources

    # Only finished: requests.http_status is not null
    # - exclude requests that didn't receive Network.loadingFinished or Network.loadingFailed event
    # - unfinished requests are not included in stats, because we don't know if this is an error
    def request_stat_for_resources(self):
        data_resources = self._all_finished_requests()
        self._append_non_cached_requests(data_resources)
        self._append_unfinished_requests(data_resources)
        return data_resources

    def _append_non_cached_requests(self, data):
        for resource_id, non_cached in self._non_cached_finished_requests().items():
            if resource_id not in data:
                data[resource_id] = {}
            data[resource_id]["avg_size"] = non_cached["avg_size"]
            data[resource_id]["avg_load_time"] = non_cached["avg_load_time"]

    def _append_unfinished_requests(self, data):
        for resource_id, unfinished in self._unfinished_requests().items():
            if resource_id not in data:
                data[resource_id] = {}
            data[resource_id]["requests_unfinished"] = unfinished

    def _all_finished_requests(self):
        c = self.conn.cursor()
        c.execute("""
             SELECT resource_id, COUNT(*), SUM(from_cache)
             FROM devtools_request
             WHERE is_main = 0 AND http_status IS NOT NULL
             GROUP BY resource_id
         """)
        result = c.fetchall()
        resources = {}
        for row in result:
            resource_id, requests_finished, from_cache = row
            resources[resource_id] = {
                "requests_finished": requests_finished,
                "from_cache": from_cache
            }
        return resources

    # avg_load_time (only non-cached requests)
    # avg_size (this is resource size, so cached requests are not included)
    def _non_cached_finished_requests(self):
        c = self.conn.cursor()
        c.execute("""
             SELECT resource_id, AVG(data_received), AVG(time_load)
             FROM devtools_request
             WHERE is_main = 0 AND http_status IS NOT NULL AND from_cache = 0
             GROUP BY resource_id
         """)
        result = c.fetchall()
        resources = {}
        for row in result:
            resource_id, avg_size, avg_load_time = row
            resources[resource_id] = {
                "avg_size": avg_size,
                "avg_load_time": avg_load_time
            }
        return resources

    def _unfinished_requests(self):
        c = self.conn.cursor()
        c.execute("""
             SELECT resource_id, COUNT(*)
             FROM devtools_request
             WHERE is_main = 0 AND http_status IS NULL
             GROUP BY resource_id
         """)
        result = c.fetchall()
        resources = {}
        for row in result:
            resource_id, requests_unfinished = row
            resources[resource_id] = requests_unfinished
        return resources

    def request_error_for_resources(self):
        c = self.conn.cursor()
        c.execute("""
             SELECT R.page_id, R.resource_id, R.http_status, E.name
             FROM devtools_request AS R
             LEFT JOIN devtools_request_error AS E
                ON E.id = R.error_id
             WHERE R.is_main = 0 AND (R.http_status >= 400 OR R.http_status = 0)
         """)
        result = c.fetchall()
        resources = {}
        for row in result:
            self._append_error_info_to_resources(resources, row)
        return resources

    # top 10 occurrences for every failed request
    def _append_error_info_to_resources(self, resources, row):
        page_id, resource_id, http_status, error_name = row
        if resource_id not in resources:
            resources[resource_id] = {
                "requests_errors": 0,
                "pages_with_error": []
            }
        resources[resource_id]["requests_errors"] += 1
        page_occurrences = len(resources[resource_id]["pages_with_error"])
        max_occurrences = 10
        error_data = [page_id, http_status, error_name]
        if page_occurrences < max_occurrences and error_data not in resources[resource_id]["pages_with_error"]:
            resources[resource_id]["pages_with_error"].append(error_data)
