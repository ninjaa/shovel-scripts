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
    LINUX_DISTRO_FLAVOR,
    LINUX_DISTRO_VERSION,
    MY_SHOVEL_ROOT_DIR,
    run_shell_cmd,
    TEMPLATE_DIR,
)

@task
def install_nginx_conf():
    """ Overwrites byobu's bashrc with canonical version from tplDir """
    srcPath = os.path.join(TEMPLATE_DIR, LINUX_DISTRO_FLAVOR, "nginx.conf.{env}.example".format(env=CONFIG["env"]))
    destPath = "/etc/nginx/nginx.conf"
    owCmd = "sudo cp {srcPath} {destPath}".format(
        srcPath=srcPath,
        destPath=destPath
    )
    run_shell_cmd(owCmd)

