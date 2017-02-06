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
    merge_dicts,
    MY_SHOVEL_ROOT_DIR,
    run_shell_cmd,
    TEMPLATE_DIR,
)

MY_APPS = CONFIG['apps']


@task
def ls_apps(apps=CONFIG['apps']):
    ''' Helper function prints all apps in config.yml '''
    print(apps.keys())

@task
def fix_permissions(
    appName, 
    dirPermissions=0775, 
    filePermissions=0664,
    env=CONFIG['env'],
    tld=CONFIG['tld'],
    wwwRoot=CONFIG['www_root'],
):
    ''' chmods appropriately '''
    if appName in MY_APPS.keys():
        print("appName {} found".format(appName))
        appConf = MY_APPS[appName]

        appContainerDirname = "{}.{}".format(appName, tld)
        appContainerDirPath = os.path.join(wwwRoot, appContainerDirname)
        print("App Container Dir is found at {}".format(appContainerDirPath))

        for root, subdirs, files in os.walk(appContainerDirPath):
            print files
            # for subdir in subdirs:
            #     run_shell_cmd("sudo chmod {dirPermissions} {subdir}".format(
            #         dirPermissions=dirPermissions,
            #         subdir=subdir
            #     ))
            # for filename in files:
            #     run_shell_cmd("sudo chmod {filePermissions} {filename}".format(
            #         dirPermissions=dirPermissions,
            #         filename=filename
            #     ))


@task
def install_app(
    appName,
    newBranch=False,
    env=CONFIG['env'],
    tld=CONFIG['tld'],
    wwwRoot=CONFIG['www_root'],
    wwwDir=CONFIG['www_dir'], 
    wwwUser=CONFIG['www_user'],
    wwwGroup=CONFIG['www_grp'],
    templateDir=TEMPLATE_DIR,
    nginxVhostRoot=CONFIG['nginx_vhost_root'],
    nginxUser=CONFIG['nginx_user'],
    nginxGroup=CONFIG['nginx_grp']
):
    ''' Installs an app of given appName if found in MY_APPS '''
    if appName in MY_APPS.keys():
        print("appName {} found".format(appName))
        appConf = merge_dicts(CONFIG, MY_APPS[appName])
        print appConf
        appConf['app_name'] = appName

        appContainerDirname = "{}.{}".format(appName, tld)
        appConf['fqdn'] = appContainerDirname
        appContainerDirPath = os.path.join(wwwRoot, appContainerDirname)
        print("App Container Dir is found at {}".format(appContainerDirPath))
        if not os.path.isdir(appContainerDirPath):
            os.mkdir(appContainerDirPath, 0775)
        
        appRoot = os.path.join(appContainerDirPath, wwwDir)
        appConf['app_root'] = appRoot
        if not os.path.isdir(appRoot):
            run_shell_cmd("git clone {appGitOrigin} {appRoot}".format(
                appGitOrigin=appConf['repo'],
                appRoot=appRoot
            ))

        # checkout branch
        if appConf['branch']:
            cwd = os.getcwd()
            os.chdir(appRoot)
            run_shell_cmd("git checkout {branchName}".format(
                branchName=appConf['branch']))
            os.chdir(cwd)
        
        # checkout new branch if explicitly named
        if newBranch:
            cwd = os.getcwd()
            os.chdir(appRoot)
            run_shell_cmd("get checkout -b {newBranch}".format(
                newBranch=newBranch
            ))
            run_shell_cmd("get push -u origin {newBranch}".format(
                newBranch=newBranch
            ))
            os.chdir(cwd)

        templateLoader = jinja2.FileSystemLoader(searchpath=templateDir)
        templateEnv = jinja2.Environment(loader=templateLoader)

        # generate vhost.conf
        filename = appContainerDirname + ".conf"
        run_shell_cmd("sudo chown -R {wwwUser}:{wwwGroup} {nginxVhostRoot}".format(
            wwwUser=wwwUser,
            wwwGroup=wwwGroup,
            nginxVhostRoot=nginxVhostRoot
        ))
        destPath = os.path.join(nginxVhostRoot, filename)
        tpl = templateEnv.get_template(appConf['vhost_conf_tpl'])
        output = tpl.render(appConf)
        with open(destPath, "wb") as outfile:
            outfile.write(output)
        print("printed out {filename} to {destPath}".format(
            filename=filename,
            destPath=destPath
        ))


        # generate local.xml

        for filename in appConf['generated_files'].keys():
            destPath = os.path.join(appRoot, appConf['generated_files'][filename])
            tpl = templateEnv.get_template(filename)
            output = tpl.render({ "cfg": appConf })
            with open(destPath, "wb") as outfile:
                outfile.write(output)
            print("printed out {filename} to {destPath}".format(
                filename=filename,
                destPath=destPath,
            ))

        # overwrite example files
        ow_dot_examples(appName, env, tld, wwwRoot, wwwDir)

        # create writable folders if required
        for writableFolder in appConf['writable_folders']:
            writableFolderPath = os.path.join(appRoot, writableFolder)
            if not os.path.isdir(writableFolderPath):
                os.mkdir(writableFolderPath, 0775)
            
            if os.path.isdir(writableFolderPath):
                run_shell_cmd("sudo chmod -R {nginxUser}:{nginxGroup} {writableFolderPath}".format(
                    nginxUser=nginxUser,
                    nginxGroup=nginxGroup,
                    writableFolderPath=writableFolderPath
                ))

        # fix_permissions
        # restart server
        



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
    print devWebRootPath
    print searchPattern
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
