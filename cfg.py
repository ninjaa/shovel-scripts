# # cfg.py - Tasks and helpers that configure an application instance


# ## Absolute imports
from distutils.util import strtobool
import fnmatch
import json
import jinja2
import MySQLdb
import os
from subprocess import call, check_output, Popen, PIPE
import shlex
from shovel import task
from shutil import copyfile
import sys
from time import gmtime, strftime
import yaml


# ## Relative imports
from lib import (
    cmd_offer_boolean_choice, 
    CONFIG, 
    get_strftime, 
    MY_SHOVEL_ROOT_DIR,
    run_shell_cmd,
)

@task
def ow_dot_examples(
    appName,
    env=CONFIG['env'],
    tld=CONFIG['tld'],
    wwwRoot=CONFIG['www_root'],
    wwwDir=CONFIG['www_dir'],
):
    '''Overwrite every filename with filename.{env}.examples if one is found in that folder
    
    This command will scan the directory /{wwwRoot}/{appName}{tld}/{wwwDir} and copy over all files named *.{env}.example to the name of the file

    It takes 5 arguments, 4 arguments are mandatory:
    - appName
    - env defaults to CONFIG['env']
    - tld defaults to CONFIG['tld']
    - wwwRoot defaults to CONFIG['www_root']
    - wwwDir = CONFIG['www_dir']


    Examples:
        bmro cfg.ow_dot_examples www2 

    '''
    devFolderName = "{appName}.{tld}".format(appName=appName, tld=tld)
    devRootPath = os.path.join("/", wwwRoot, devFolderName)
    devWebRootPath = os.path.join(devRootPath, wwwDir)
    searchPattern = "*.{env}.example".format(env=env)
    matches = []
    for root, dirnames, filenames in os.walk(devWebRootPath):
        for filename in fnmatch.filter(filenames, searchPattern):
            matches.append(os.path.join(root, filename))

    print(matches)

    for srcFile in matches:
        destFile = srcFile.replace(".{env}.example".format(env=env), "")
        print("cp {srcFile} to {destFile}".format(srcFile=srcFile, destFile=destFile))
        copyfile(srcFile, destFile)

