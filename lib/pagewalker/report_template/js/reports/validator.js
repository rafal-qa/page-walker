
/* global data_validator_head, data_validator_main, data_validator_stat */

class ValidatorReport extends Report {

    constructor() {
        super();
        this.validator = new DataParser(data_validator_head, data_validator_main);
        this.table_raw = $('.table-wrapper.report-raw table');
        this.table_dom = $('.table-wrapper.report-dom table');
        this.table_loaded = {
            "raw": false,
            "dom": false
        };
        this.table_order = {
            "raw": [[3, "asc"], [2, "desc"]],
            "dom": [[3, "asc"], [2, "desc"]]
        };
    }

    addStats() {
        var stats = $('#stats-main');
        for (name in data_validator_stat) {
            var value = data_validator_stat[name],
                class_name = '.stats-' + name;
            $(class_name + ' .value', stats).text(value);
            if (name === 'errors_raw' || name === 'errors_dom') {
                var color = value > 0 ? 'red' : 'green';
                $(class_name, stats).addClass(color);
            }
        }
    }

    insertDataToTable() {
        var html_raw = "",
            html_dom = "";

        if (!this.validator.hasData()) {
            return false;
        }
        this.validator.reset();
        do {
            var message_id = this.validator.get("id"),
                message = this._messageColors(this.validator.get("message")),
                extract = this._generateExtract(this.validator.get("extract")),
                occurrences = this.validator.get("occurrences");

            if (this.validator.get("is_error")) {
                var occurrences_color = 'red',
                    event_type = 'error';
            } else {
                var occurrences_color = 'yellow',
                    event_type = 'warning';
            }

            var append_row = '<tr data-message-id="' + message_id + '">'
                             + '<td>' + message + '</td>'
                             + '<td><code class="ellipsis">' + extract + '</code></td>'
                             + '<td><a class="ui ' + occurrences_color + ' label details">' + occurrences + '</a></td>'
                             + '<td>' + event_type + '</td>'
                           + '</tr>';

            if (this.validator.get("html_type") === 1) {
                html_raw += append_row;
            } else {
                html_dom += append_row;
            }
        }
        while (this.validator.forward());

        $("tbody", this.table_raw).html(html_raw);
        $("tbody", this.table_dom).html(html_dom);
    }

    insertDataToModal(clicked_element) {
        var message_id = clicked_element.closest("tr").attr("data-message-id");
        this.validator.setIndexById(message_id);

        var modal = $('#details-modal'),
            message = this._messageColors(this.validator.get("message")),
            details = this.validator.get("details"),
            color = this.validator.get("is_error") ? 'red' : 'yellow';

        $('.ui.message', modal).removeClass('red yellow').addClass(color);
        $('.validator-message', modal).html(message);

        var content = this._modalContent(this, details);
        $('table tbody', modal).html(content);
    }

    _modalContent(validator_obj, details) {
        var html = "";
        Object.keys(details).forEach(function(extract_id) {
            var data = details[extract_id],
                pages_list = data["pages"],
                extract = validator_obj._generateExtract(data["extract"]),
                pages_list_html = "";

            for (var i = 0; i < pages_list.length; i++) {
                var page_id = pages_list[i][0],
                    code_line = pages_list[i][1];
                validator_obj.pages.setIndexById(page_id);
                pages_list_html += '<li>' + validator_obj.pages.getAsLink("url") + ' [' + code_line +']</li>';
            }

            var append_row = '<tr>'
                             + '<td><code class="ellipsis">' + extract + '</code></td>'
                             + '<td><ul class="ui list">' + pages_list_html + '</ul></td>'
                           + '</tr>';
            html += append_row;
        });
        return html;
    }

    _messageColors(message) {
        message = breakLine(escapeHtml(message));
        message = message.replace(/{([^}]*)}/g, '<span class="ui basic label">$1</span>');
        return message;
    }

    _generateExtract(extract_json) {
        var before = escapeHtml(extract_json[0]),
            marked = escapeHtml(extract_json[1]),
            after =  escapeHtml(extract_json[2]),
            extract = breakLine(before)
                    + '<mark>' + breakLine(marked) + '</mark>'
                    + breakLine(after);
        extract = extract.replace(/\n/g, "<br />").replace(/\t/g, "");
        return extract;
    }

}