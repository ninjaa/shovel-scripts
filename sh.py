# # sh.py - Tasks and helpers to configure my shell


# ## Absolute imports
from distutils.util import strtobool
import json
import jinja2
import MySQLdb
import os
from subprocess import call, check_output, Popen, PIPE
import shlex
from shovel import task
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
def install_byobu_bashrc():
    """ Overwrites byobu's bashrc with canonical version from tplDir """
    tplDir = os.path.join(MY_SHOVEL_ROOT_DIR, "templates")
    tplBashrcPath = os.path.join(tplDir, "bashrc.{env}.example".format(env=CONFIG["env"]))
    byobuBashrcPath = "/usr/share/byobu/profiles/bashrc"
    owByobuBashrcCmd = "sudo cp {tplBashrcPath} {byobuBashrcPath}".format(
        tplBashrcPath=tplBashrcPath,
        byobuBashrcPath=byobuBashrcPath
    )
    run_shell_cmd(owByobuBashrcCmd)

