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

# the following line allows local imports from pwd
if __package__ is None:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

configFileStream = file('config.yml', 'r')
config = yaml.load(configFileStream)


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
def dump_mysql_db(dbName, dbUsername=config["db_server_root_username"], dbPassword=config["db_server_root_password"], dbHost=config["db_server"], dumpFolder=config["db_dump_location"]):
	""" Function to dump mysql db to dump folder """
	dumpFilename = "{dbName}_{timeStr}.sql".format(dbName=dbName,timeStr=get_strftime())
	dumpAbsolutePath = os.path.join(dumpFolder, dumpFilename)
	print(dumpAbsolutePath)
	try:
		run_shell_cmd("mysqldump -u {dbUsername} -p'{dbPassword}' -h {dbHost} {dbName} > {dumpAbsolutePath}".format(dbUsername=dbUsername, dbPassword=dbPassword, dbHost=dbHost, dbName=dbName, dumpAbsolutePath=dumpAbsolutePath))
		print("successfully dumped {dbName} to {dumpAbsolutePath}".format(dbName=dbName, dumpAbsolutePath=dumpAbsolutePath))
	except: # catch *all* exceptions
		e = sys.exc_info()[0]
		print("Error: {exception}".format(exception=e))



@task
def show_databases(dbUsername=config["db_server_root_username"], dbPassword=config["db_server_root_password"], dbHost=config["db_server"], dumpFolder=config["db_dump_location"]):
	db = MySQLdb.connect(
		host=dbHost,
		user=dbUsername,
		passwd=dbPassword,
		db="mysql")
	
	cur = db.cursor()
	# Use all the SQL you like
	cur.execute("SHOW DATABASES;")
	
	for row in cur.fetchall():
		print(row[0])
	
	db.close()

