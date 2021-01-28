# -*- coding: utf-8 -*-
import os

lenth_list = [7, 8, 9, 10]


def make_null_string(v, add_string="="):
    """
    :param v:
    :param add_string:
    :return:
    """
    append_string = ""
    while v > 0:
        append_string = "{0}{1}".format(add_string, append_string)
        v = v - 1
    return append_string


def format_file(old_file, new_file, add_string="="):
    """
    :param old_file:
    :param new_file:
    :param add_string:
    :return:
    """
    if not os.path.exists(old_file):
        raise FileExistsError("{0} 文件不存在！".format(old_file))
    with open(old_file, 'r') as fff:
        data = fff.readlines()
    for e in data:
        print("开始处理：{0}".format(e))
        val = e.split('|')
        new_data = list()
        if len(lenth_list) != len(val):
            raise Exception('配置与文件字段长度不一样')
        for i in range(0, len(val)):
            elength = lenth_list[i]
            if len(val[i]) >= elength:
                new_data.append(val[i])
                continue
            add_len = elength - len(val[i].strip('\n'))
            add_data = make_null_string(v=add_len, add_string=add_string)
            if val[i].endswith('\n'):
                data_new = val[i].replace('\n', "{0}\n".format(add_data))
            else:
                data_new = "{0}{1}".format(val[i], add_data)
            new_data.append(data_new)
        str_data = '|'.join(new_data)
        with open(new_file, 'a') as Pfaff:
            Pfaff.write(str_data)


format_file(old_file='111.txt', new_file='222.txt')
