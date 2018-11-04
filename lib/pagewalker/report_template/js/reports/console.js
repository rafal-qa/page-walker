
/* global data_console_head, data_console_main, data_console_stat */

class ConsoleReport extends Report {

    constructor() {
        super();
        this.console_logs = new DataParser(data_console_head, data_console_main);
        this.table = $('.table-wrapper.report-console table');
        this.table_loaded = {
            "console": false
        };
        this.table_order = {
            "console": [[2, "desc"], [1, "desc"]]
        };

        this.log_levels = {
            1: "verbose",
            2: "info",
            3: "warning",
            4: "error"
        };
        this.log_levels_color = {
            1: "blue",
            2: "blue",
            3: "yellow",
            4: "red"
        };
        this.log_sources = {
            1: "xml",
            2: "javascript",
            3: "network",
            4: "storage",
            5: "appcache",
            6: "rendering",
            7: "security",
            8: "deprecation",
            9: "worker",
            10: "violation",
            11: "intervention",
            12: "recommendation",
            13: "other"
        };
    }

    addStats() {
        var stats = $('#stats-main');
        for (name in data_console_stat) {
            var value = data_console_stat[name],
                class_name = '.stats-' + name;
            $(class_name + ' .value', stats).text(value);
            if (name === 'error') {
                var color = value > 0 ? 'red' : 'green';
                $(class_name, stats).addClass(color);
            } else if (name === 'warning') {
                var color = value > 0 ? 'yellow' : 'green';
                $(class_name, stats).addClass(color);
            }
        }
    }

    insertDataToTable() {
        var html = "";

        if (!this.console_logs.hasData()) {
            return false;
        }
        this.console_logs.reset();
        do {
            var log_id = this.console_logs.get("id"),
                description = this.console_logs.get("description"),
                occurrences = this.console_logs.get("occurrences"),
                level_id = this.console_logs.get("level_id"),
                level = level_id + '_' + this.log_levels[level_id],
                source_id = this.console_logs.get("source_id"),
                source = this.log_sources[source_id],
                occurrences_color = this.log_levels_color[level_id];

            html += '<tr data-log-id="' + log_id + '">'
                    + '<td>' + breakLine(escapeHtml(description)) + '</td>'
                    + '<td><a class="ui ' + occurrences_color + ' label details">' + occurrences + '</a></td>'
                    + '<td>' + level + '</td>'
                    + '<td>' + source + '</td>'
                  + '</tr>';
        }
        while (this.console_logs.forward());

        $("tbody", this.table).html(html);
    }

    insertDataToModal(clicked_element) {
        var log_id = clicked_element.closest("tr").attr("data-log-id");
        this.console_logs.setIndexById(log_id);

        var modal = $('#details-modal'),
            description = this.console_logs.get("description"),
            level_id = this.console_logs.get("level_id"),
            color = this.log_levels_color[level_id];

        description = escapeHtml(description);
        description = breakLine(description);

        $('.ui.message', modal).removeClass('blue yellow red').addClass(color);
        $('.console-message', modal).html(description);

        var content = this._modalContent();
        $('table tbody', modal).html(content);
    }

    _modalContent() {
        var pages_with_log = this.console_logs.get("pages_with_log"),
            html = "";
        for (var i = 0; i < pages_with_log.length; i++) {
            var page_id = pages_with_log[i];
            this.pages.setIndexById(page_id);
            var append_row = '<tr>'
                             + '<td>' + this.pages.getAsLink("url") + '</td>'
                           + '</tr>';
            html += append_row;
        }
        return html;
    }

}