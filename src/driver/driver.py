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

    config = _load_config()

    if not __sanitize_config(config):

        exit(2)
