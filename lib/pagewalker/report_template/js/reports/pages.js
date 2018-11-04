
/* global data_pages_stat, data_summary_config */

class PagesReport extends Report {

    constructor() {
        super();
        this.table_pages = $('.table-wrapper.report-pages table');
        this.table_files = $('.table-wrapper.report-files table');
        this.table_loaded = {
            "pages": false,
            "files": false
        };
        this.table_order = {
            "pages": [[2, "desc"], [0, "asc"]],
            "files": []
        };
    }

    addStats() {
        var stats = $('#stats-main');
        for (name in data_pages_stat) {
            var value = data_pages_stat[name],
                class_name = '.stats-' + name;
            $(class_name + ' .value', stats).text(value);
            if (name === 'failed') {
                var color = value > 0 ? 'red' : 'green';
                $(class_name, stats).addClass(color);
            }
        }
    }

    insertDataToTable() {
        var html_pages = "",
            html_files = "";

        if (!this.pages.hasData()) {
            return false;
        }
        this.pages.reset();
        do {
            var page_id = this.pages.get("id"),
                url = this.pages.getAsLink("url"),
                file_type = this.pages.get("file_content_type"),
                file_size = this.pages.get("file_content_length"),
                http_status_code = this.pages.get("http_status"),
                http_exception_name = this.pages.get("exception_name"),
                requests_all = this.pages.get("requests_count"),
                requests_cached = this.pages.get("requests_cached_percent"),
                data_received = this.pages.get("data_received_sum"),
                time_load = this.pages.get("time_load"),
                backlink_html = this._backlinkHTML(this.pages.get("backlink"));

            if (requests_cached === null) {
                var requests_cached_text = "";
            } else {
                var requests_cached_text = requests_cached + "%";
            }

            if (file_type) {
                html_files += '<tr data-page-id="' + page_id + '">'
                                + '<td>' + page_id + '</td>'
                                + '<td>' + url + '</td>'
                                + '<td>' + nullToString(file_type) + '</td>'
                                + '<td>' + nullToString(file_size) + '</td>'
                                + '<td>' + backlink_html + '</td>'
                            + '</tr>';
            } else {
                var status_name = "Loading failed",
                    status_css = "error";
                if (http_status_code === null) {
                    if (http_exception_name !== null) {
                        status_name = http_exception_name;
                    }
                } else {
                    status_name = httpStatusInfo(http_status_code);
                    status_css = this._statusCSS(http_status_code);
                }
                html_pages += '<tr data-page-id="' + page_id + '">'
                                + '<td>' + page_id + '</td>'
                                + '<td>' + url + '</td>'
                                + '<td class="' + status_css + '">' + status_name + '</td>'
                                + '<td>' + nullToString(requests_all) + '</td>'
                                + '<td>' + requests_cached_text + '</td>'
                                + '<td>' + nullToString(data_received) + '</td>'
                                + '<td>' + nullToString(time_load) + '</td>'
                                + '<td>' + backlink_html + '</td>'
                            + '</tr>';
            }
        }
        while (this.pages.forward());

        $("tbody", this.table_pages).html(html_pages);
        $("tbody", this.table_files).html(html_files);
    }

    _backlinkHTML(backlink_id) {
        if (backlink_id === 0) {
            return '';
        }
        var relative_url = this.pages.getByIdValue(backlink_id, "url"),
            full_url = data_summary_config["page_host"] + relative_url;
        if (relative_url === "" || relative_url === "/") {
            var backlink_title = "(home)";
        } else {
            var backlink_title = relative_url;
        }
        return '<a href="' + full_url + '" title="'
                + backlink_title + '"><i class="external alternate icon"></i></a>';
    }

    _statusCSS(status_code) {
        var status_type = status_code.toString().charAt(0);
        if (status_type === "1" || status_type === "2") {
            return "positive";
        } else if (status_type === "3") {
            return "warning";
        } else {
            return "error";
        }
    }

}