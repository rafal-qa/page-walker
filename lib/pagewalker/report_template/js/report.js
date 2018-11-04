
/* global data_pages_head, data_pages_main */

class Report {

    // information about pages on every report
    constructor() {
        var pages = new DataParser(data_pages_head, data_pages_main);
        this.pages = pages;
    }

    initDataTable(tab) {
        var table_wrapper = $('.table-wrapper.report-' + tab);
        if (this.table_loaded[tab]) {
            table_wrapper.removeClass('hidden');
        } else {
            this.table_loaded[tab] = true;
            this._tableFirstTimeLoad(table_wrapper, tab);
        }
    }

    _tableFirstTimeLoad(table_wrapper, tab) {
        $('table', table_wrapper).DataTable( {
            "lengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
             "order": this.table_order[tab],
             "autoWidth": false,
             "initComplete": function() {
                 table_wrapper.removeClass('hidden');
                 $('.footer').removeClass('hidden');
                 this.api().columns.adjust();
            }
        } );
    }

    initTabs(default_tab) {
        var tabs = $('.tabular.menu');
        this._initDefaultTab(default_tab, tabs);
        this._showTabWithTable(tabs);
    }

    _initDefaultTab(default_tab, tabs) {
        this.initDataTable(default_tab);
        $('.item[data-tab="' + default_tab + '"]', tabs).addClass('active');
    }

    _showTabWithTable(tabs) {
        var that = this;
        $('.item', tabs).click(function() {
            if (!$(this).hasClass('active')) {
                var tab = $(this).attr('data-tab');
                $('.item', tabs).removeClass('active');
                $(this).addClass('active');
                $('.table-wrapper').addClass('hidden'); // hide all tables
                that.initDataTable(tab); // show only selected table
            }
        });
    }

    initDetailsModal() {
        var that = this;
        $('.table-wrapper table').on('click','.label.details',function(){
            that.insertDataToModal($(this));
            $('#details-modal').modal('show');
        });
    }

}