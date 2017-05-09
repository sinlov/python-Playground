# coding=utf-8

import sys
import os
from os import path, access, R_OK

__author__ = 'sinlov'

reload(sys)
sys.setdefaultencoding('utf-8')


def is_input_file(file_path):
    if path.exists(file_path) and path.isfile(file_path) and access(file_path, R_OK):
        return True
    else:
        return False


# def file_exists(filename):
#     try:
#         with open(filename) as f:
#             return True
#     except IOError:
#         return False

def text_line_merge_line_by_line(source, comp, target):
    if path.exists(target):
        os.remove(target)
    t_file = open(target, 'a')
    t_file.write('<?xml version="1.0" encoding="utf-8"?>\n')
    t_file.write('<resources>\n')
    for s_line in open(source):
        e_s_line = read_each_line_by_name_xml(s_line)
        if e_s_line != "":
            for c_line in open(comp):
                e_c_line = read_each_line_by_name_xml(c_line)
                if e_s_line == e_c_line:
                    t_file.write(s_line)
    t_file.write('\n')
    t_file.write('</resources>')
    t_file.close()


def read_each_line_by_name_xml(t_line=str):
    e_line = t_line.split('\"')
    if len(e_line) > 5 and e_line[2] == ' name=':
        return e_line[3]
    else:
        return ""


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('You must input \n\t'
              'First params: source_path\n\t'
              'Second params: comp_path\n\t'
              '\n ---\n\t'
              'out will be source_path + ".merge_out"\n'
              '\nYour input error please check')
        exit(1)
    source_file = sys.argv[1]
    comp_file = sys.argv[2]
    if is_input_file(source_file) and is_input_file(comp_file):
        target_file = source_file + ".merge_out"
        text_line_merge_line_by_line(source_file, comp_file, target_file)
        print('merge success out file is ', target_file)
    else:
        print('You input is not file, please check')
        exit(1)
