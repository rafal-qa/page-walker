class SummaryReport {
    
    constructor() {
        this.stats = $('#stats-main');
        this.stat_data = data_summary_stat;
        this.config_data = data_summary_config;
    }

    addStats() {
        for (var name in this.stat_data) {
            var value = this.stat_data[name],
                class_name = '.stats-' + name;
            $(class_name + ' .value', this.stats).text(value);
            if (name === 'unique_errors') {
                var color = value > 0 ? 'red' : 'green';
                $(class_name, this.stats).addClass(color);
            }
        }
    }

    fillMainTable() {
        for (var name in this.config_data) {
            var value = this.config_data[name];
            if (name === "page_start") {
                var link = '<a href="' + value + '">' + breakLine(value) + '</a>';
                $('td.info-' + name).html(link);
            } else {
                $('td.info-' + name).text(value);
            }
        }
        if (this.config_data.validator_enabled === "No") {
            $('.validator-details-table').hide();
        }
        if (this.config_data.check_external_links === "No") {
            $('.info-check_external_links_timeout').parent().hide();
        }
    }

}