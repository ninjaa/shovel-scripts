# # cfg.py - Tasks and helpers that configure an application instance


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


