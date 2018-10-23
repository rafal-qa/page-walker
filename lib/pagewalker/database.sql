CREATE TABLE config (
	option text,
	value text
);

CREATE TABLE pages (
	id integer PRIMARY KEY AUTOINCREMENT,
	parent_id integer,
	url text,
	completion_status integer,
	http_status integer,
	exception_id integer,
	file_type integer
);

CREATE TABLE pages_stat (
	page_id integer,
	time_dom_content integer,
	time_load integer,
	file_content_length integer
);

CREATE TABLE devtools_resource (
	id integer PRIMARY KEY AUTOINCREMENT,
	url text,
	is_truncated integer,
	is_external integer
);

CREATE TABLE devtools_request (
	id integer PRIMARY KEY AUTOINCREMENT,
	page_id integer,
	resource_id integer,
	error_id integer,
	http_status integer,
	from_cache integer,
	data_received integer,
	time_started integer,
	time_load integer,
	is_main integer
);

CREATE TABLE devtools_console_log (
	id integer PRIMARY KEY AUTOINCREMENT,
	level_id integer,
	source_id integer,
	description text
);

CREATE TABLE devtools_console (
	id integer PRIMARY KEY AUTOINCREMENT,
	page_id integer,
	log_id integer
);

CREATE TABLE devtools_js_exception_text (
	id integer PRIMARY KEY AUTOINCREMENT,
	description text
);

CREATE TABLE devtools_js_exception (
	id integer PRIMARY KEY AUTOINCREMENT,
	page_id integer,
	exception_id integer
);

CREATE TABLE html_validator_message (
	id integer PRIMARY KEY AUTOINCREMENT,
	is_error integer,
	description text
);

CREATE TABLE html_validator (
	id integer PRIMARY KEY AUTOINCREMENT,
	page_id integer,
	message_id integer,
	extract_id integer,
	line integer,
	html_type integer
);

CREATE TABLE html_validator_extract (
	id integer PRIMARY KEY AUTOINCREMENT,
	extract_json text
);

CREATE TABLE pages_file_type (
	id integer PRIMARY KEY AUTOINCREMENT,
	content_type text
);

CREATE TABLE devtools_request_error (
	id integer PRIMARY KEY AUTOINCREMENT,
	name text
);

CREATE TABLE pages_connection_exception (
	id integer PRIMARY KEY AUTOINCREMENT,
	name string
);
