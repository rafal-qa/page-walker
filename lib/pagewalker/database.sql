CREATE TABLE config (
	option text,
	value text
);

CREATE TABLE pages (
	id integer PRIMARY KEY AUTOINCREMENT,
	parent_id integer,
	url text,
	status integer,
	exception_id integer,
	file_type integer
);

CREATE TABLE pages_stats (
	page_id integer,
	time_dom_content integer,
	time_load integer,
	file_content_length integer
);

CREATE TABLE resources (
	id integer PRIMARY KEY AUTOINCREMENT,
	url text,
	is_truncated integer,
	is_external integer
);

CREATE TABLE requests (
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

CREATE TABLE devtools_logs (
	id integer PRIMARY KEY AUTOINCREMENT,
	level_id integer,
	source_id integer,
	description text
);

CREATE TABLE pages_devtools_logs (
	id integer PRIMARY KEY AUTOINCREMENT,
	page_id integer,
	log_id integer
);

CREATE TABLE js_exceptions (
	id integer PRIMARY KEY AUTOINCREMENT,
	description text
);

CREATE TABLE pages_js_exceptions (
	id integer PRIMARY KEY AUTOINCREMENT,
	page_id integer,
	exception_id integer
);

CREATE TABLE validator_messages (
	id integer PRIMARY KEY AUTOINCREMENT,
	is_error integer,
	description text
);

CREATE TABLE pages_validator (
	id integer PRIMARY KEY AUTOINCREMENT,
	page_id integer,
	message_id integer,
	extract_id integer,
	line integer,
	html_type integer
);

CREATE TABLE validator_extracts (
	id integer PRIMARY KEY AUTOINCREMENT,
	extract_json text
);

CREATE TABLE file_types (
	id integer PRIMARY KEY AUTOINCREMENT,
	content_type text
);

CREATE TABLE requests_error (
	id integer PRIMARY KEY AUTOINCREMENT,
	name text
);

CREATE TABLE connection_exceptions (
	id integer PRIMARY KEY AUTOINCREMENT,
	name string
);
