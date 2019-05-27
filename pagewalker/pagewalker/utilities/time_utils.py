from datetime import datetime


def current_date_time():
    time_format = "%Y-%m-%d %H:%M:%S"
    return datetime.now().strftime(time_format)


def current_date_time_safe_precise():
    time_format = "%Y-%m-%d_%H-%M-%S_%f"
    return datetime.now().strftime(time_format)


def time_diff_ms(start, end):
    if start is None or end is None:
        return None
    else:
        value = end - start
        value = round(value * 1000)
        return value
