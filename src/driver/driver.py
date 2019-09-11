from src.core.haproxyupdater.haproxyupdate import HaproxyUpdate
from src.core.nodefetchers.awsfetcher.awsfetcher import AwsFetcher
from configparser import SafeConfigParser
import time
import optparse
import os

CONFIG_FILE = "ep2.config"
LOCK_FILE = "ep2.lock"

def drive():
    global CONFIG_FILE

    # parse args
    parser = optparse.OptionParser()
    parser.add_option('-f', action="store", dest="config", help="Config file")
    options, args = parser.parse_args()

    if options.config:
        CONFIG_FILE = options.config

    config = __load_config()

    if not __sanitize_config(config):

        exit(2)

def __load_config():
    parser = SafeConfigParser()
    parser.read(CONFIG_FILE)

    config = {}

    for section in parser.sections():
        config[section] = {}
        for name, value in parser.items(section):
            config[section][name] = value

    return config

def __can_aquire_lock(lock_dir):
    if os.path.exists(lock_dir):
        return True

def __aquire_lock(lock_dir):
    lock_file = os.path.join(lock_dir, LOCK_FILE)
    try:
        if not os.path.exists(lock_file):
            with open(lock_file, "w") as lock_file:
                lock_file.write(os.getpid())
            return True
        return False
    except Exception as ex:
        return False

def __release_lock(lock_dir):
    lock_file = os.path.join(lock_dir, LOCK_FILE)
    try:
        if os.path.exists(lock_file):
            os.unlink(lock_file)
        return True
    except Exception as ex:
        return False

def __sanitize_config(config):

    return True
