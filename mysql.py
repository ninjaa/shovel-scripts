# # mysql.py - MySQL DB tasks and helper functions

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

def get_dumpfile_absolute_path(
    dumpFilename, 
    dumpFolder=config["db_dump_location"]):
    """

    Args:
        dumpFilename:
            is either an absolute path to an sql file, 
            the name of an existing sql file in the optional dumpFolder, 
            or an 8 digit date suffix such as 20161111, prompting a search for a dump file
            dbName_suffix.sql
    """
    # Get dumpAbsolutePath from dumbFilename and dumpFolder
    if os.path.isfile(dumpFilename):
        dumpAbsolutePath = dumpFilename
        dumpFolder = os.path.dirname(dumpAbsolutePath)
        dumpFilename = os.path.basename(dumpAbsolutePath)
    else:
        # tacks on sql file extension if forgotten
        if len(dumpFilename) >= 4 and dumpFilename[-4:] != ".sql":
            dumpFilename = dumpFilename + ".sql"

        dumpAbsolutePath = os.path.join(dumpFolder, dumpFilename)

    print dumpAbsolutePath
    print dumpFilename
    return dumpAbsolutePath, dumpFilename, dumpFolder

@task
def create_db(dbName, 
           dumpFilename=False,
           dbRootUsername=config["db_server_root_username"], 
           dbRootPassword=config["db_server_root_password"], 
           dbHost=config["db_server"], 
           dumpFolder=config["db_dump_location"],
          ):
    """ Creates a new mysql db with dbName and imports initial data from dumpFilename 

        Args:
            dbName: name of DB to create (required)
            dumpFilename:
                is either an absolute path to an sql file, 
                the name of an existing sql file in the optional dumpFolder, 
                or an 8 digit date suffix such as 20161111, prompting a search for a dump file
                dbName_suffix.sql
    """
    mysqlDbs = get_dbs(dbRootUsername, dbRootPassword, dbHost)
    protectedMysqlDbs = config["protected_mysql_dbs"]
    if dbName in protectedMysqlDbs:
        raise NameError(
            "{dbName} is in protected_mysql_dbs {protectedMysqlDbs}".format(
                dbName=dbName,
                protectedMysqlDbs=protectedMysqlDbs)
        )
    if dbName in mysqlDbs:
        print("WARNING: Mysql db {dbName} already exists, skipping create!".format(dbName=dbName))
    else:
        db = MySQLdb.connect(
            host=dbHost,
            user=dbRootUsername,
            passwd=dbRootPassword,
            db="mysql")

        cur = db.cursor()

        cur.execute("CREATE DATABASE IF NOT EXISTS {dbName};".format(dbName=dbName))
        print("Created MySQL db {dbName}".format(dbName=dbName))

    if dumpFilename:
        import_sql(dbName, dumpFilename, dbRootUsername, dbRootPassword, dbHost, dumpFolder,
               forceOverwriteExistingDb=True)


@task
def create_user(dbUsername,
            dbUserHost='localhost',
            dbPassword=False,
            dbRootUsername=config["db_server_root_username"], 
            dbRootPassword=config["db_server_root_password"], 
            dbHost=config["db_server"]
):
        """ This function creates mysql dbUsername@dbUserHost on dbHost
        """
        pass

@task
def dump(dbName, 
         dbUsername=config["db_server_root_username"], 
         dbPassword=config["db_server_root_password"], 
         dbHost=config["db_server"], 
         dumpFolder=config["db_dump_location"],
         forceOverwriteDumpfile=False
        ):
    """ Function to dump mysql db to dump folder """
    # @TODO Add ROW_FORMAT modifier to dump
    # http://stackoverflow.com/questions/8243973/force-row-format-on-mysqldump
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

    dumpAbsolutePath, dumpFilename, dumpFolder = get_dumpfile_absolute_path(dumpFilename,
                                                                            dumpFolder)

    #print dumpAbsolutePath

    mysqlDbs = get_dbs(dbUsername, dbPassword, dbHost)
    #print(mysqlDbs)

    if dbName in mysqlDbs:
        if forceOverwriteExistingDb or cmd_offer_boolean_choice("A MySQL Database with the name \"{dbName}\" already exists. Overwrite it?".format(dbName=dbName)):
            mysqlImportCmd = "mysql -u {dbUsername} -p'{dbPassword}' -h {dbHost} {dbName} < {dumpAbsolutePath}".format(dbUsername=dbUsername,
                                                                                                                      dbPassword=dbPassword,
                                                                                                                      dbHost=dbHost,
                                                                                                                      dbName=dbName,
                                                                                                                      dumpAbsolutePath=dumpAbsolutePath)
            print(mysqlImportCmd)
            run_shell_cmd(mysqlImportCmd)
        else:
            print("should not overwrite")
    else:
        print("No MySQL Database with the name \"{dbName} does not exist. Create it first.")


@task
def ls_dbs(dbUsername=config["db_server_root_username"], dbPassword=config["db_server_root_password"], dbHost=config["db_server"]):
    """ Lists all dbs in dbHost """
    mysqlDbs = get_dbs(dbUsername, dbPassword, dbHost)
    print("\n".join(mysqlDbs))
    print("DONE")

def get_dbs(
    dbUsername=config["db_server_root_username"], 
    dbPassword=config["db_server_root_password"], 
    dbHost=config["db_server"]
):
    db = MySQLdb.connect(
        host=dbHost,
        user=dbUsername,
        passwd=dbPassword,
        db="mysql")

    cur = db.cursor()
    # Use all the SQL you like
    cur.execute("SHOW DATABASES;")

    mysqlDbs = []
    for row in cur.fetchall():
        dbName = row[0]
        mysqlDbs.append(dbName)

    db.close()
    return mysqlDbs
    
@task
def ls_users(dbUsername=config["db_server_root_username"], dbPassword=config["db_server_root_password"], dbHost=config["db_server"]):
    """ Shows all mysql users """
    mysqlUsers = get_users(dbUsername, dbPassword, dbHost)
    
    print("MySQL users on {dbHost}:".format(dbHost=dbHost))
    for username in mysqlUsers.keys():
        for host in mysqlUsers[username].keys():
            print("'{username}'@'{host}'".format(username=username, host=host))
    
    print("DONE")


def get_users(dbUsername=config["db_server_root_username"], dbPassword=config["db_server_root_password"], dbHost=config["db_server"]):
    db = MySQLdb.connect(
        host=dbHost,
        user=dbUsername,
        passwd=dbPassword,
        db="mysql")

    cur = db.cursor()
    # Use all the SQL you like
    cur.execute("SELECT * FROM mysql.user;")

    mysqlUsers = {}
    for row in cur.fetchall():
        username = row[1]
        host = row[0]
        if not username in mysqlUsers.keys():
            mysqlUsers[username] = {}
        mysqlUsers[username][host] = row

    db.close()
    
    return mysqlUsers

