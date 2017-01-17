# # setup.py - steps to help you setup your local


# ## Absolute imports
from distutils.util import strtobool
import fnmatch
import json
import jinja2
import MySQLdb
import os
from subprocess import call, check_output, Popen, PIPE
import shlex
from shovel import task
from shutil import copyfile
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
    run_shell_cmd,
    TEMPLATE_DIR,
)


@task
def setup_magento_server(
    env=CONFIG['env'],
    tld=CONFIG['tld'],
    wwwRoot=CONFIG['www_root'],
    wwwDir=CONFIG['www_dir']
):
    ''' Setup linux system suitable for installation of Magento 1.9.x '''
    # https://www.rosehosting.com/blog/install-magento-2-on-an-ubuntu-14-04-vps/
    if LINUX_DISTRO_FLAVOR == 'ubuntu' and LINUX_DISTRO_VERSION == '14.04':
        run_shell_cmd("sudo apt-get update && sudo apt-get -y upgrade")
        run_shell_cmd(
            "sudo apt-get install -y software-properties-common curl nano")
        run_shell_cmd(
            "sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xcbcb082a1bb943db")
        run_shell_cmd(
            "sudo add-apt-repository 'deb [arch=amd64,i386,ppc64el] http://mirror.lstn.net/mariadb/repo/10.1/ubuntu trusty main'")
        run_shell_cmd("sudo apt-get update")
        #run_shell_cmd("sudo apt-get install -y mariadb-server")
        #run_shell_cmd("sudo mysql_secure_installation")

        run_shell_cmd("sudo add-apt-repository -y ppa:ondrej/php")
        run_shell_cmd("sudo apt-get update")
        run_shell_cmd("sudo apt-get install -y php5.6-fpm php5.6-cli php5.6-gd php5.6-imagick php5.6-mysqlnd php5.6-mcrypt php-pear php5.6-curl php5.6-intl php5.6-gd php5.6-xs")

        run_shell_cmd("sudo add-apt-repository -y ppa:nginx/stable")
        run_shell_cmd("sudo apt-get update")
        run_shell_cmd("sudo apt-get install -y nginx")

        run_shell_cmd("sudo apt-get install -y redis-server redis-tools")

        run_shell_cmd("curl -sS https://getcomposer.org/installer | php")
        run_shell_cmd("sudo mv composer.phar /usr/local/bin/composer")

        print("please run the following commands manually")
        print("sudo apt-get install -y mariadb-server")


@task
def cfg_magento_server(
    env=CONFIG['env'],
    tld=CONFIG['tld'],
    wwwRoot=CONFIG['www_root'],
    wwwDir=CONFIG['www_dir'],
    wwwUser=CONFIG['www_user'],
    wwwGroup=CONFIG['www_grp'],
    dbDumpLocation=CONFIG['db_dump_location'],
):
    ''' Configures installed packages '''
    if LINUX_DISTRO_FLAVOR == 'ubuntu' and LINUX_DISTRO_VERSION == '14.04':
        # overwrite /etc/nginx.conf from
        # templateDir/ubuntu/14.04/etc/nginx.conf
        nginxConfSrcPath = os.path.join(
            TEMPLATE_DIR,
            LINUX_DISTRO_FLAVOR,
            "nginx.conf.{env}.example".format(env=env)
        )
        nginxConfDestPath = "/etc/nginx/nginx.conf"
        run_shell_cmd("sudo cp {} {}".format(
            nginxConfSrcPath, nginxConfDestPath))
        # start nginx
        run_shell_cmd("sudo service nginx restart")

        # enable nginx on startup
        run_shell_cmd("sudo update-rc.d nginx defaults")

        # overwrite /etc/redis.conf from templateDir/ubuntu/14.04/etc/redis.conf
        # start redis
        run_shell_cmd("sudo service redis-server start")
        # enable redis on startup
        run_shell_cmd("sudo update-rc.d redis_6379 defaults")

        # overwrite /etc/php/5.6/fpm/php.ini from
        # templateDir/ubuntu/14.04/etc/php/5.6/php.ini
        phpIniSrcPath = os.path.join(
            TEMPLATE_DIR,
            LINUX_DISTRO_FLAVOR,
            "php.ini"
        )
        phpIniDestPath = "/etc/php/5.6/fpm/php.ini"
        run_shell_cmd("sudo cp {} {}".format(
            phpIniSrcPath, phpIniDestPath
        ))

        # overwrite /etc/php/5.6/fpm/php.ini from
        # templateDir/ubuntu/14.04/etc/php/5.6/php.ini
        phpFpmPoolSrcPath = os.path.join(
            TEMPLATE_DIR,
            LINUX_DISTRO_FLAVOR,
            "www.conf"
        )
        phpFpmPoolDestPath = "/etc/php/5.6/fpm/pool.d/www.conf"
        run_shell_cmd("sudo cp {} {}".format(
            phpFpmPoolSrcPath, phpFpmPoolDestPath
        ))

        run_shell_cmd("sudo service php5.6-fpm start")

        run_shell_cmd("sudo mkdir -p {}".format(dbDumpLocation))
        run_shell_cmd(
            "sudo chown -R {}:{} {}".format(wwwUser, wwwGroup, wwwRoot))
