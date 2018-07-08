
/* global data_resources_head, data_resources_main, data_resources_stat */

class ResourcesReport extends Report {

    constructor() {
        super();
        this.resources = new DataParser(data_resources_head, data_resources_main);
        this.table_internal = $('.table-wrapper.report-internal table');
        this.table_external = $('.table-wrapper.report-external table');
        this.table_loaded = {
            "internal": false,
            "external": false
        };
        this.table_order = {
            "internal": [[2, "desc"], [ 1, "desc" ]],
            "external": [[2, "desc"], [ 1, "desc" ]]
        };
    }

    addStats() {
        var stats = $('#stats-main');
        for (name in data_resources_stat) {
            var value = data_resources_stat[name],
                class_name = '.stats-' + name;
            $(class_name + ' .value', stats).text(value);
            if (name === 'error_internal' || name === 'error_external') {
                var color = value > 0 ? 'red' : 'green';
                $(class_name, stats).addClass(color);
            }
        }
    }

    insertDataToTable() {
        var html_internal = "",
            html_external = "";

        if (!this.resources.hasData()) {
            return false;
        }
        this.resources.reset();
        do {
            var resource_id = this.resources.get("id"),
                url = this.resources.getAsLink("url", this.resources.get("is_truncated")),
                requests = this.resources.get("requests_all"),
                errors = this.resources.get("requests_errors"),
                requests_cached = this.resources.get("requests_cached_percent"),
                unfinished = this.resources.get("requests_unfinished_percent"),
                avg_size = this.resources.get("avg_size"),
                avg_time = this.resources.get("avg_load_time"),
                pages_with_error = this.resources.get("pages_with_error");

            var append_row = '<tr data-resource-id="' + resource_id + '">'
                             + '<td>' + url + '</td>'
                             + '<td>' + requests + '</td>'
                             + '<td>' + this._errorsHTML(errors, pages_with_error) + '</td>'
                             + '<td>' + requests_cached + '%</td>'
                             + '<td>' + avg_size + '</td>'
                             + '<td>' + avg_time + '</td>'
                             + '<td>' + this._unfinishedHTML(unfinished) + '</td>'
                           + '</tr>';

            if (this.resources.get("is_external")) {
                html_external += append_row;
            } else {
                html_internal += append_row;
            }
        }
        while (this.resources.forward());

        $("tbody", this.table_internal).html(html_internal);
        $("tbody", this.table_external).html(html_external);
    }

    _errorsHTML(errors, pages_with_error) {
        if (errors > 0) {
            var status_code = pages_with_error[0][1],
                error_name = pages_with_error[0][2];
            return '<a class="ui red label details" data-tooltip="' + this._errorStatusName(status_code, error_name)
                    + '" data-position="right center">' + errors + '</a>';
        } else {
            return '<span class="ui green basic label">0</span>';
        }
    }

    _unfinishedHTML(unfinished) {
        if (unfinished > 0) {
            return '<span class="ui yellow basic label">' + unfinished + '%</span>';
        } else {
            return '<span class="ui green basic label">0</span>';
        }
    }

    insertDataToModal(clicked_element) {
        var resource_id = clicked_element.closest("tr").attr("data-resource-id");
        this.resources.setIndexById(resource_id);
        
        var modal = $('#details-modal'),
            resource_url = this.resources.getAsLink("url", this.resources.get("is_truncated"));
        $('.resource-url', modal).html(resource_url);

        var content = this._modalContent();
        $('table tbody', modal).html(content);
    }

    _modalContent() {
        var pages_with_error = this.resources.get("pages_with_error"),
            html = "";
        for (var i = 0; i < pages_with_error.length; i++) {
            var page_id = pages_with_error[i][0],
                status_code = pages_with_error[i][1],
                error_name = pages_with_error[i][2];
            this.pages.setIndexById(page_id);
            var append_row = '<tr>'
                             + '<td>' + this.pages.getAsLink("url") + '</td>'
                             + '<td>' + this._errorStatusName(status_code, error_name) + '</td>'
                           + '</tr>';
            html += append_row;
        }
        return html;
    }

    _errorStatusName(status_code, error_name) {
        var status_name = "Unknown";
        if (status_code) {
            status_name = httpStatusInfo(status_code);
        } else {
            if (error_name !== null) {
                status_name = error_name;
            }
        }
        return status_name;
    }

}