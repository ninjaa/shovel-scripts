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

# the following line allows local imports from pwd
if __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

config = {'db_dump_location':'/srv/www/dbdumps'}

@task
def get_strftime(timePattern="%Y%m%d"):
	""" returns date string eg 20170107 """
	timestr = strftime(timePattern, gmtime())
	print(timestr)
	return timestr

@task
def run_shell_cmd(cmd, printCmd=True):
    ''' helper function to run shell command v2 '''
    print(cmd)
    print(check_output(cmd, shell=True))

@task
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
def dump_mysql_db(dbName, dbUsername="root", dbPassword="123", dbHost="localhost", dumpFolder=config['db_dump_location']):
	""" Function to dump mysql db to dump folder """
	dumpFilename = "{dbName}_{timeStr}.sql".format(dbName=dbName,timeStr=get_strftime())
	dumpAbsolutePath = os.path.join(dumpFolder, dumpFilename)
	print(dumpAbsolutePath)
	run_shell_cmd("mysqldump -u {dbUsername} -p{dbPassword} -h {dbHost} > {dumpAbsolutePath}".format(dbUsername=dbUsername, dbPassword=dbPassword, dbHost=dbHost, dumpAbsolutePath=dumpAbsolutePath))
#	pass
