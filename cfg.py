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

MY_HOME_DIR = os.environ['HOME']
MY_SHOVEL_ROOT_DIR = os.path.join(MY_HOME_DIR, ".shovel")

# the following line allows local imports from pwd
if __package__ is None:
    sys.path.append(MY_SHOVEL_ROOT_DIR)


# ## Relative imports
from lib import (
    cmd_offer_boolean_choice,
    CONFIG,
    get_strftime,
    MY_SHOVEL_ROOT_DIR,
    run_shell_cmd,
)

MY_APPS = CONFIG['apps']


@task
def ls_apps(apps=CONFIG['apps']):
    ''' Helper function prints all apps in config.yml '''
    print(apps.keys())


@task
def install_app(
    appName,
    env=CONFIG['env'],
    tld=CONFIG['tld'],
    wwwRoot=CONFIG['www_root'],
    wwwDir=CONFIG['www_dir']
):
    ''' Installs an app of given appName if found in MY_APPS '''
    if appName in MY_APPS.keys():
        print("appName {} found".format(appName))
    
        appContainerDirname = "{}.{}".format(appName, tld)
        appContainerDirPath = os.path.join(wwwRoot, appContainerDirname)
        print("App Container Dir is found at {}".format(appContainerDirPath))
        if not os.path.isdir(appContainerDirPath):
            os.mkdir(appContainerDirPath, 0775)
        
        



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
        print("cp {srcFile} to {destFile}".format(
            srcFile=srcFile, destFile=destFile))
        copyfile(srcFile, destFile)
