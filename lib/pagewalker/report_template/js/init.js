/* global _report_, data_summary_error, data_summary_config */

function mainMenuStatus() {
    Object.keys(data_summary_error).forEach(function(key) {
        var count = data_summary_error[key];
        if (count) {
            var color = "red",
                caption = count;
        } else {
            var color = "green",
                caption = "ok";
        }
        var label = $('#main-menu a[data-report="' + key + '"] span');
        label.addClass(color);
        label.text(caption);
        label.css("visibility", "visible");
    });
}

function hideHtmlValidator() {
    var validator =  $('#main-menu a[data-report="validator"]');
    validator.addClass("disabled");
    $('span', validator).remove();
    if (_report_ === 'summary') {
        $('.validator-details-table').hide();
    }
}

function escapeHtml(string) {
    var toReplace = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '`': '&#x60;',
        '=': '&#x3D;'
    };
    return String(string).replace(/[&<>"'`=]/g, function (s) {
        return toReplace[s];
    });
}

// additional word breaks (default break after '?' and '-')
function breakLine(string) {
    // after slashes
    string = string.replace(/\//g, "/<wbr>");
    // after every 50-char non-brekable excerpt
    string = string.replace(/([^?/\- ]{50})/g, "$1<wbr>");
    return string;
}

function nullToString(string) {
    if (string === null) {
        return "";
    } else {
        return string;
    }
}

function httpStatusInfo(http_status) {
    if (http_status === null || http_status === "") {
        return "Unknown";
    }
    var codes = {
        200: "OK",
        301: "Moved Permanently",
        302: "Found",
        303: "See Other", 
        304: "Not Modified",
        307: "Temporary Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        408: "Request Timeout",
        410: "Gone",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
        504: "Gateway Timeout"
    };
    if (http_status in codes) {
        http_status += " " + codes[http_status];
    }
    return http_status;
}

function help() {
    var help_button = $('#help-button'),
        help_message = $('#help-message');
    help_button.on('click','button',function(){
        help_button.hide();
        help_message.show();
    });
    $('#help-message').on('click','.close',function(){
        help_message.hide();
        help_button.show();
    });
}

$(document).ready(function() {
    "use strict";

    mainMenuStatus();
    if (data_summary_config["validator_enabled"] === "No") {
        hideHtmlValidator();
    }
    $('#main-menu a[data-report="' + _report_ + '"]').addClass('active');

    if (_report_ === 'summary') {
        var summary_report = new SummaryReport();
        summary_report.addStats();
        summary_report.fillMainTable();
    } else if (_report_ === 'pages') {
        var pages_report = new PagesReport();
        pages_report.addStats();
        pages_report.insertDataToTable();
        pages_report.initTabs('pages');
        pages_report.initDetailsModal();
    } else if (_report_ === 'resources') {
        var resources_report = new ResourcesReport();
        resources_report.addStats();
        resources_report.insertDataToTable();
        resources_report.initTabs('internal');
        resources_report.initDetailsModal();
    } else if (_report_ === 'javascript') {
        var javascript_report = new JavascriptReport();
        javascript_report.addStats();
        javascript_report.insertDataToTable();
        javascript_report.initTabs('javascript');
        javascript_report.initDetailsModal();
    } else if (_report_ === 'devtools') {
        var devtools_report = new DevtoolsReport();
        devtools_report.addStats();
        devtools_report.insertDataToTable();
        devtools_report.initTabs('devtools');
        devtools_report.initDetailsModal();
    } else if (_report_ === 'validator') {
        var validator_report = new ValidatorReport();
        validator_report.addStats();
        validator_report.insertDataToTable();
        validator_report.initTabs('raw');
        validator_report.initDetailsModal();
    }

    help();
} );