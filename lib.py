# lib.py

import json
import jinja2
from subprocess import call, check_output, Popen, PIPE
import shlex
from shovel import task
import sys
import os
import platform
#import ruamel.yaml
from time import gmtime, strftime
import yaml
import MySQLdb
from distutils.util import strtobool

MY_HOME_DIR = os.environ['HOME']
MY_SHOVEL_ROOT_DIR = os.path.join(MY_HOME_DIR, ".shovel")
CONFIG_FILE_PATH = os.path.join(MY_SHOVEL_ROOT_DIR, "config.yml")
TEMPLATE_DIR = os.path.join(MY_SHOVEL_ROOT_DIR, "templates")

# the following line allows local imports from pwd
if __package__ is None:
    sys.path.append(MY_SHOVEL_ROOT_DIR)

# not a @task
def run_shell_cmd(cmd, printCmd=True):
    ''' helper function to run shell command v2 '''
    print(cmd)
    print(check_output(cmd, shell=True))

# not a @task
def run_shell_command(cmdstr):
    ''' helper function to run shell command '''
    print("running command `{}`".format(cmdstr))
    cmd_args = shlex.split(cmdstr)
    print(cmd_args)
    proc = Popen(cmd_args, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    exitcode = proc.returncode
    print("exitcode {}, stdout {}, stderr {}".format(exitcode, out, err))
    return exitcode, out, err

@task
def gen_cfg_yml(env="dev"):
    ''' Generate config.yml from tpl '''
    run_shell_cmd("cp {xmplPath} {cfgPath}".format(
        xmplPath=os.path.join(
            MY_SHOVEL_ROOT_DIR, 
            "templates", 
            "config.yml.{env}.example".format(env=env)
        ),  cfgPath=CONFIG_FILE_PATH
    ))

def load_config():
    if not os.path.isfile(CONFIG_FILE_PATH):
        gen_cfg_yml()

    if os.path.isfile(CONFIG_FILE_PATH):
        configFileReader = file(CONFIG_FILE_PATH, 'r')
        config = yaml.load(configFileReader)
        return config
    else:
        return {}

CONFIG = load_config()

LINUX_DISTRO_TUPLE = platform.linux_distribution()
LINUX_DISTRO_FULL_FLAVOR = LINUX_DISTRO_TUPLE[0]
LINUX_DISTRO_VERSION = LINUX_DISTRO_TUPLE[1]

if LINUX_DISTRO_FULL_FLAVOR == 'Red Hat Enterprise Linux Server':
    LINUX_DISTRO_FLAVOR = 'rhel'
elif LINUX_DISTRO_FULL_FLAVOR == 'Ubuntu':
    LINUX_DISTRO_FLAVOR = 'ubuntu'
else: 
    print("Warning! no suitable linux distro found")
    print(LINUX_DISTRO_TUPLE)
    LINUX_DISTRO_FLAVOR = 'unknown'
    
#scriptPath = os.path.dirname(os.path.abspath(__file__))

def cmd_offer_boolean_choice(question):
    print(question + " (Answer [Y/N] and press Enter) ")
    return strtobool(raw_input())

# not a @task
def get_strftime(timePattern="%Y%m%d"):
	""" returns date string eg 20170107 """
	timestr = strftime(timePattern, gmtime())
	print(timestr)
	return timestr


@task
def show_cfg():
    ''' Print config variables in config.yml '''
    print(CONFIG)

@task
def update_cfg_yml():
    ''' update config.yml '''
    madeChanges = False

    for key, data in CONFIG.items():
        print("CONFIG['{key}']=\"{data}\"".format(key=key, data=data))
        if cmd_offer_boolean_choice("Update CONFIG['{key}']?".format(key=key)):
            print("Enter new value for CONFIG['{key}'] and then press enter:")
            CONFIG[key] = raw_input()
            madeChanges = True

    if madeChanges or cmd_offer_boolean_choice("Write new config.yml file despite no changes?"):
        if not os.path.isfile(CONFIG_FILE_PATH):
            print("No existing config.yml found at {cfp}, creating it").format(cfp=CONFIG_FILE_PATH)
            newconfigFilePatah = CONFIG_FILE_PATH
        else:
            print("Existing config.yml found at {cfp}, so creating new.config.yml").format(cfp=CONFIG_FILE_PATH)
            newConfigFilePath = os.path.join(MY_SHOVEL_ROOT_DIR, "new.config.yml")

        with open(newConfigFilePath, 'w') as newConfigFileWriter:
            yaml.dump(CONFIG, newConfigFileWriter, default_flow_style=False)
            print("Dumped new config.yml to #{newConfigFilePath}")

@task
def gen_sha1(rawPassword, forceUppercase=False):
    ''' Task takes a rawPassword as required argument and returns and prints out a SHA1 hash.
    Optional second boolean argument for forcing an Uppercase hash '''
    if forceUppercase:
        genSha1PwCmd = "echo -n {rawPassword} | sha1sum | awk '{{print toupper($1)}}'".format(rawPassword=rawPassword)
    else:
        genSha1PwCmd = "echo -n {rawPassword} | sha1sum | awk '{{print $1}}'".format(rawPassword=rawPassword)

    run_shell_cmd(genSha1PwCmd)
