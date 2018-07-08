
def percent(smaller, bigger, as_text=False):
    if bigger:
        percent_tmp = float(smaller) / float(bigger)
        result = int(round(percent_tmp * 100))
    else:
        result = 0
    if as_text:
        result = str(result) + "%"
    return result


def list_average_as_int(values):
    if not values:
        return 0
    result = sum(values) / float(len(values))
    return int(round(result))


def bytes_to_kilobytes_as_int(bytes_value):
    return int(round(bytes_value / 1024))


def bytes_to_megabytes_as_string(bytes_value):
    mb_value = float(bytes_value) / 1024 / 1024
    return "%0.2f" % (mb_value,)


def convert_dict_to_list(dict_data, key_order):
    converted = []
    for single_dict in dict_data:
        list_item = []
        for key in key_order:
            list_item.append(single_dict[key])
        converted.append(list_item)
    return converted
