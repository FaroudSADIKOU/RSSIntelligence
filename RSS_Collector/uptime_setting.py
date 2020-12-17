# -*- coding: utf-8 -*-
"""
Created on Wed Sep 16 11:56:12 2020

@author: Faroud
"""
#
import locale
from subprocess import check_output, STDOUT
import subprocess
import sys

# ------
# uptime
# ------
"""
When trying to get a  Windows machine's uptime, we use a command 
that returns alot more information than just the uptime. 
We then get to find within all those returned information the 
one that we need. So we need an expression to filter the line 
we want. And depending on the default local language, it can be different

This function return the needed expression for either 
french or english
"""
def get_find_expression_for_win(local_language):
    a_find_expression = ""
    if local_language.startswith("fr"):
        a_find_expression = "depuis"
    elif local_language.startswith("en"):
        a_find_expression = "since"
    return a_find_expression

"""
"""
def get_uptime():
    uptime =""
    if sys.platform.startswith('linux'):
        # case we're on a linux os
        uptime = subprocess.check_output(['uptime'])
    elif sys.platform.startswith('win32'):
        # Windows case here
        #language checking
        find_expression = get_find_expression_for_win( locale.getdefaultlocale()[0] )
        try:
            command = "net statistics workstation | find " + "\"" + find_expression +"\""
            uptime = check_output(command, shell=True, stderr=STDOUT)
        except subprocess.CalledProcessError as e:
            #raise RuntimeError("command", e.cmd, "return with error code ", e.returncode, ":", e.output)
            print(e)
    return uptime



