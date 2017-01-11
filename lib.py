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

# the following line allows local imports from pwd
if __package__ is None:
    sys.path.append(shovelRootPath)

configFileStream = file(os.path.join(shovelRootPath,'config.yml'), 'r')
config = yaml.load(configFileStream)

def cmd_offer_boolean_choice(question):
    print(question + " (Answer [Y/N] and press Enter) ")
    return strtobool(raw_input())

# not a @task
def get_strftime(timePattern="%Y%m%d"):
	""" returns date string eg 20170107 """
	timestr = strftime(timePattern, gmtime())
	print(timestr)
	return timestr

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

