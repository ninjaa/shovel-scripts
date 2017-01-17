# # sh.py - Tasks and helpers to configure my shell


# ## Absolute imports
from distutils.util import strtobool
import json
import jinja2
import MySQLdb
import os
import platform
from subprocess import call, check_output, Popen, PIPE
import shlex
from shovel import task
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
    LINUX_DISTRO_FLAVOR,
    LINUX_DISTRO_VERSION,
    MY_SHOVEL_ROOT_DIR,
    run_shell_cmd,
)

@task
def ls_installed():
    """ Lists installed packages """
    if LINUX_DISTRO_FLAVOR == "rhel":
        run_shell_cmd("rpm -qa")
    elif LINUX_DISTRO_FLAVOR == "ubuntu":
        run_shell_cmd("dpkg -l")
    else:
        print("Your Linux Distribution {flavor} {version} was unrecognized".format(
            flavor=LINUX_DISTRO_FLAVOR, 
            version=LINUX_DISTRO_VERSION
        ))
