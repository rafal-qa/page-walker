class DataParser {

    constructor(data_head, data_main) {
        this.data = data_main;
        this.current_index = 0;
        this.max_index = data_main.length - 1;

        // assign index used by "data_main" list to column name from "data_head"
        // to be able get value by column name, not list index
        var column_to_index = {},
            column_name;
        for (var index = 0; index < data_head.length; index++) {
            column_name = data_head[index];
            column_to_index[column_name] = index;
        }
        this.column_to_index = column_to_index;

        // match value of column "id" with index on "data_main" list
        // to be able get value by "id", not list index
        var index_of_id = column_to_index.id,
            id_to_index = {},
            value_of_id;
        for (var index = 0; index < data_main.length; index++) {
            value_of_id = data_main[index][index_of_id];
            id_to_index[value_of_id] = index;
        }
        this.id_to_index = id_to_index;
    }

    hasData() {
        if (this.data.length) {
            return true;
        } else {
            return false;
        }
    }

    get(column) {
        var index = this.column_to_index[column];
        return this.data[this.current_index][index];
    }

    getByIdValue(id_value, column) {
        id_value = parseInt(id_value);
        var index_of_id = this.id_to_index[id_value],
            index_of_column = this.column_to_index[column];
        return this.data[index_of_id][index_of_column];
    }

    setIndexById(id) {
        id = parseInt(id);
        this.current_index = this.id_to_index[id];
    }

    forward() {
        if (this.current_index >= this.max_index) {
            return false;
        } else {
            this.current_index++;
            return true;
        }
    }

    reset() {
        this.current_index = 0;
    }

    getAsLink(column, truncated=false) {
        var url = this.get(column);
        if (url === null) {
            return "";
        }
        if (truncated) {
            return breakLine(url) + " [...]";
        } else {
            return this._clickableLink(url);
        }
    }

    _clickableLink(url) {
        var anchor, url_with_host;
        if (url === "" || url === "/") {
            anchor = "(home)";
        } else {
            anchor = breakLine(url);
        }
        if (this._isAbsolute(url)) {
            url_with_host = url;
        } else {
            url_with_host = data_summary_config.page_host + url;
        }
        return '<a href="' + url_with_host + '">' + anchor + '</a>';
    }

    _isAbsolute(url) {
        return url.startsWith("http://") || url.startsWith("https://");
    }

}