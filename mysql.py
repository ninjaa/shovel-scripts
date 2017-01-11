# mysql.py

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


@task
def dump(dbName, 
         dbUsername=config["db_server_root_username"], 
         dbPassword=config["db_server_root_password"], 
         dbHost=config["db_server"], 
         dumpFolder=config["db_dump_location"],
         forceOverwriteDumpfile=False
        ):
    """ Function to dump mysql db to dump folder """
    dumpFilename = "{dbName}_{timeStr}.sql".format(
        dbName=dbName, timeStr=get_strftime())
    dumpAbsolutePath = os.path.join(dumpFolder, dumpFilename)
    print(dumpAbsolutePath)
    existsDumpAbsolutePath = os.path.isfile(dumpAbsolutePath)
    if (
        (not existsDumpAbsolutePath) or 
        forceOverwriteDumpfile or 
        (
            existsDumpAbsolutePath and 
            cmd_offer_boolean_choice(
                "Dump file exists at {dumpAbsolutePath}. Overwrite it?".format(dumpAbsolutePath=dumpAbsolutePath)
            )
        )):
        try:
            run_shell_cmd(
                "mysqldump -u {dbUsername} -p'{dbPassword}' -h {dbHost} {dbName} > {dumpAbsolutePath}".format(
                    dbUsername=dbUsername, 
                    dbPassword=dbPassword, 
                    dbHost=dbHost, 
                    dbName=dbName, 
                    dumpAbsolutePath=dumpAbsolutePath)
            )
            print("successfully dumped {dbName} to {dumpAbsolutePath}".format(
                dbName=dbName, 
                dumpAbsolutePath=dumpAbsolutePath)
            )
        except:  # catch *all* exceptions
            e = sys.exc_info()[0]
            print("Error: {exception}".format(exception=e))
    else:
        print("User elected not to overwrite dumpfile. Exiting.")


@task
def import_sql(
    dbName, 
    dumpFilename, 
    dbUsername=config["db_server_root_username"], 
    dbPassword=config["db_server_root_password"], 
    dbHost=config["db_server"], 
    dumpFolder=config["db_dump_location"],
    forceOverwriteExistingDb=False):
    """ Function to import mysql db from dumpfile """
    # if dumpFilename argument is an all numeric date suffix eg 20161111
    # create dumpFilename as eg dbName_2016111
    if len(dumpFilename) == 8 and dumpFilename.isdigit():
        dumpFilename = dbName + "_" + dumpFilename

    # tacks on sql file extension if forgotten
    if len(dumpFilename) > 4 and dumpFilename[-4:] != ".sql":
        dumpFilename = dumpFilename + ".sql"

    dumpAbsolutePath = os.path.join(dumpFolder, dumpFilename)
    print(dumpAbsolutePath)

    mysqlDatabases = get_databases(dbUsername, dbPassword, dbHost)
    print(mysqlDatabases)

    if dbName in mysqlDatabases:
        if forceOverwriteExistingDb or cmd_offer_boolean_choice("A MySQL Database with the name \"{dbName}\" already exists. Overwrite it?".format(dbName=dbName)):
            print("should overwrite")
        else:
            print("should not overwrite")
    else:
        print("No MySQL Database with the name \"{dbName} already exists. Create it first.")


@task
def show_databases(dbUsername=config["db_server_root_username"], dbPassword=config["db_server_root_password"], dbHost=config["db_server"]):
    mysqlDatabases = get_databases(dbUsername, dbPassword, dbHost)
    print("\n".join(mysqlDatabases))


def get_databases(dbUsername=config["db_server_root_username"], dbPassword=config["db_server_root_password"], dbHost=config["db_server"]):
    db = MySQLdb.connect(
        host=dbHost,
        user=dbUsername,
        passwd=dbPassword,
        db="mysql")

    cur = db.cursor()
    # Use all the SQL you like
    cur.execute("SHOW DATABASES;")

    mysqlDatabases = []
    for row in cur.fetchall():
        dbName = row[0]
        mysqlDatabases.append(dbName)

    db.close()
    
    return mysqlDatabases


