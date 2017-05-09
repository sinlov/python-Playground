# coding=utf-8
import sys

import re
import os
import file_system_utils
import platform
import logging
import subprocess

__author__ = 'sinlov'

logger = logging.getLogger('cmd_tool')


def prepare_cmd(cmd):
    cmd = cmd.replace('\\', '/')
    cmd = re.sub('/+', '/', cmd)
    if not os.path.isabs(cmd):
        cur_dir = file_system_utils.get_cur_dir()
        cmd = os.path.join(cur_dir, cmd)

    parent_path = os.path.dirname(cmd)
    os.chdir(parent_path)
    file_system_utils.change_cur_dir(parent_path)
    logging.info('change cur dir path to : %s' % parent_path)

    cmd = os.path.split(cmd)[-1]
    return cmd


def send_err_to_srv(cmd, stdoutput, erroutput):
    logging.info(cmd)
    print(cmd)
    sys.stdout.flush()


def exec_cmd(cmd):
    logging.info('exec cmd: ' + cmd)

    cmd = cmd.replace('\\', '/')
    cmd = re.sub('/+', '/', cmd)

    if platform.system() == 'Windows':
        sub_process = subprocess.STARTUPINFO
        sub_process.dwFlags = subprocess.STARTF_USESHOWWINDOW
        sub_process.wShowWindow = subprocess.SW_HIDE
        cmd = str(cmd).encode('gbk')

    s = subprocess.Popen(cmd, shell=True)
    ret = s.wait()

    if ret:
        s = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        std_output, err_output = s.communicate()
        send_err_to_srv(cmd, std_output, err_output)
        cmd += 'exec error : \n'
        cmd += err_output
        logging.error(cmd)
        logging.error('\nexec_cmd error: <<std_output>>' + std_output)
        logging.error('\nexec_cmd error: <<err_output>>' + err_output)
    else:
        cmd += 'exec success : '
        logging.info(cmd)

    return ret
