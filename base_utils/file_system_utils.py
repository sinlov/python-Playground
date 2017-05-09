# coding=utf-8

import logging
import os
import platform
import re

__author__ = 'sinlov'

logger = logging.getLogger('file_system')

__CUR_DIR = os.getcwd()


def get_full_path(filename):
    filename = filename.replace('\\', '/')
    filename = re.sub('/+', '/', filename)

    if os.path.isabs(filename):
        return filename
    dir_name = get_cur_dir()
    filename = os.path.join(dir_name, filename)
    filename = filename.replace('\\', '/')
    filename = re.sub('/+', '/', filename)
    return filename


def change_cur_dir(path):
    global __CUR_DIR

    __CUR_DIR = get_full_path(path)


def get_cur_dir():
    global __CUR_DIR
    ret_path = __CUR_DIR
    if platform.system() == 'Windows':
        ret_path = ret_path.decode('gbk')
    return ret_path

    caller_file = inspect.stack()[0][1]
    ret_path = os.path.abspath(os.path.dirname(caller_file))
    if platform.system() == 'Windows':
        ret_path = ret_path.decode('gbk')
    return ret_path
