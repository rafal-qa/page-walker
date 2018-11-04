
/* global data_links_head, data_links_main, data_links_stat */

class LinksReport extends Report {

    constructor() {
        super();
        this.links_list = new DataParser(data_links_head, data_links_main);
        this.table = $('.table-wrapper.report-links table');
        this.table_loaded = {
            "links": false
        };
        this.table_order = {
            "links": [[2, "desc"]]
        };
    }

    addStats() {
        var stats = $('#stats-main');
        for (name in data_links_stat) {
            var value = data_links_stat[name],
                class_name = '.stats-' + name;
            $(class_name + ' .value', stats).text(value);
            if (name === 'failed') {
                var color = value > 0 ? 'red' : 'green';
                $(class_name, stats).addClass(color);
            }
        }
    }

    insertDataToTable() {
        var html = "";
        if (!this.links_list.hasData()) {
            return false;
        }
        this.links_list.reset();
        do {
            var link_id = this.links_list.get("id"),
                url = this.links_list.getAsLink("url"),
                redirect_url = this.links_list.getAsLink("redirect_url"),
                occurrences = this.links_list.get("occurrences"),
                http_status_code = this.links_list.get("http_status"),
                http_exception_name = this.links_list.get("exception_name");

            var status_name = "",
                status_css = "";
            if (http_status_code === null) {
                if (http_exception_name !== null) {
                    status_name = http_exception_name;
                    status_css = "error";
                }
            } else {
                status_name = httpStatusInfo(http_status_code);
                status_css = this._statusCSS(http_status_code);
            }

            html += '<tr data-link-id="' + link_id + '">'
                    + '<td>' + url + '</td>'
                    + '<td>' + redirect_url + '</td>'
                    + '<td class="' + status_css + '">' + status_name + '</td>'
                    + '<td><a class="ui blue label details">' + occurrences + '</a></td>'
                  + '</tr>';
        }
        while (this.links_list.forward());
        $("tbody", this.table).html(html);
    }

    _statusCSS(status_code) {
        var status_type = status_code.toString().charAt(0);
        if (status_type === "1" || status_type === "2") {
            return "positive";
        } else {
            return "error";
        }
    }

    insertDataToModal(clicked_element) {
        var link_id = clicked_element.closest("tr").attr("data-link-id");
        this.links_list.setIndexById(link_id);
        var modal = $('#details-modal'),
            url = this.links_list.getAsLink("url");
        $('.ui.message', modal).html(url);
        var content = this._modalContent();
        $('table tbody', modal).html(content);
    }

    _modalContent() {
        var pages_with_link = this.links_list.get("pages_with_link"),
            html = "";
        for (var i = 0; i < pages_with_link.length; i++) {
            var page_id = pages_with_link[i];
            this.pages.setIndexById(page_id);
            var append_row = '<tr>'
                             + '<td>' + this.pages.getAsLink("url") + '</td>'
                           + '</tr>';
            html += append_row;
        }
        return html;
    }

}