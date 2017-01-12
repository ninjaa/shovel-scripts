# config.py
# This file is dedicated to generating and updating config.yml

import json
import jinja2
from subprocess import call, check_output, Popen, PIPE
import shlex
from shovel import task
import sys
import os
#import ruamel.yaml
from time import gmtime, strftime
import yaml
import MySQLdb
from distutils.util import strtobool

shovelRootPath = os.path.dirname(os.path.abspath(__file__))

if __package__ is None:
    sys.path.append(shovelRootPath)

from lib import cmd_offer_boolean_choice, get_strftime, run_shell_cmd

configFileStream = file(os.path.join(shovelRootPath,'config.yml'), 'r')
config = yaml.load(configFileStream)

if not "protected_mysql_dbs" in config.keys():
    config["protected_mysql_dbs"] = ["information_schema", "performance_schema", "mysql"]


