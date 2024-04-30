import re
import typing


def except_blank(str_list: typing.List) -> typing.List:
    if str_list:
        return [_str.strip() for _str in str_list if not _str.isspace()]
    return []


def remove_non_printable(text: str) -> str:
    """
    删除字符串中的非空字符
    比如：
        |>>> t="Lodgement\nDate"
        |>>> remove_non_printable(t)
        |>>>'LodgementDate'
    """
    return re.sub(r'[^\x20-\x7E]', '', text)


def data_wash_tag(data_list):
    for item in range(len(data_list)):
        data_list[item] = re.sub('</.*?>', '\n',data_list[item])
        data_list[item] = re.sub('<br>', '\n',data_list[item])
        data_list[item] = re.sub('<.*?>', '',data_list[item])
        # data_list[item] = re.sub(r'[^\x20-\x7E]', '', data_list[item])
        data_list[item] = data_list[item].replace('\\', '')
    return data_list


def data_wash_null(data_list):
    # for item in range(len(data_list)):
    data_list= re.sub('[\\\,\n,\\\\n,\\\\t,\\\\r]', '',data_list)
        # data_list[item] = re.sub('<br>', '\n',data_list[item])
        # data_list[item] = re.sub('<.*?>', '',data_list[item])
        # data_list[item] = re.sub(r'[^\x20-\x7E]', '', data_list[item])
        # data_list[item] = data_list[item].replace('\\', '')
    return data_list