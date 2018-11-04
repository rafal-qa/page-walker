
/* global data_javascript_head, data_javascript_main, data_javascript_stat */

class JavascriptReport extends Report {

    constructor() {
        super();
        this.javascript = new DataParser(data_javascript_head, data_javascript_main);
        this.table = $('.table-wrapper.report-javascript table');
        this.table_loaded = {
            "javascript": false
        };
        this.table_order = {
            "javascript": [[1, "desc"]]
        };
    }

    addStats() {
        var stats = $('#stats-main');
        for (name in data_javascript_stat) {
            var value = data_javascript_stat[name],
                class_name = '.stats-' + name;
            $(class_name + ' .value', stats).text(value);
            if (name === 'exception') {
                var color = value > 0 ? 'red' : 'green';
                $(class_name, stats).addClass(color);
            }
        }
    }

    insertDataToTable() {
        var html = "";

        if (!this.javascript.hasData()) {
            return false;
        }
        this.javascript.reset();
        do {
            var excpetion_id = this.javascript.get("id"),
                description = this.javascript.get("description"),
                occurrences = this.javascript.get("occurrences");

            html += '<tr data-exception-id="' + excpetion_id + '">'
                    + '<td>' + breakLine(escapeHtml(description)) + '</td>'
                    + '<td><a class="ui red label details">' + occurrences + '</a></td>'
                  + '</tr>';
        }
        while (this.javascript.forward());

        $("tbody", this.table).html(html);
    }

    insertDataToModal(clicked_element) {
        var exception_id = clicked_element.closest("tr").attr("data-exception-id");
        this.javascript.setIndexById(exception_id);
        
        var modal = $('#details-modal'),
            description = this.javascript.get("description");
        description = breakLine(escapeHtml(description));
        $('.exception-description', modal).html(description);

        var content = this._modalContent();
        $('table tbody', modal).html(content);
    }

    _modalContent() {
        var pages_with_error = this.javascript.get("pages_with_error"),
            html = "";
        for (var i = 0; i < pages_with_error.length; i++) {
            var page_id = pages_with_error[i];
            this.pages.setIndexById(page_id);
            var append_row = '<tr>'
                             + '<td>' + this.pages.getAsLink("url") + '</td>'
                           + '</tr>';
            html += append_row;
        }
        return html;
    }

}