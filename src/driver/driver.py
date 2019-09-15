from configparser import SafeConfigParser
import time
import optparse
import os
from .defaultparams import default_params
from .bootstrap import bootstrap

CONFIG_FILE = default_params.get("CONFIG_FILE")
LOCK_FILE = default_params.get("LOCK_FILE")

def drive():
    global CONFIG_FILE

    # parse args
    parser = optparse.OptionParser()
    parser.add_option('-f', action="store", dest="config", help="Config file")
    options, args = parser.parse_args()

    if options.config:
        CONFIG_FILE = options.config

    config = __load_config()
    print (config)
    exit(0)

    SLEEP_BEFORE_NEXT_RUN = config.get("sleep_before_next_run", default_params.get("SLEEP_BEFORE_NEXT_RUN"))
    SLEEP_BEFORE_NEXT_LOCK_ATTEMPT = config.get("sleep_before_next_lock_attempt", default_params.get("SLEEP_BEFORE_NEXT_LOCK_ATTEMPT"))

    if not __sanitize_config(config):

        exit(2)

    running, haproxyupdater, orchestratorHandler = bootstrap(config=config)

    if not running:

        '''
            Error has already been logged. Exit with status code 2
        '''
        exit(2)

    '''
        After this point, Haproxy should be running with the lastest IPs
        fetched from the orchestrator.
    '''

    # Begin with state loop
    while True:
        lock_aquired = __aquire_lock(config.get("lock_dir"))
        if not lock_aquired:
            time.sleep(SLEEP_BEFORE_NEXT_LOCK_ATTEMPT)
            continue

        asg_ips = orchestratorHandler.fetch()
        haproxyupdater.update_node_list(asg_ips)
        updated = haproxyupdater.update_haproxy()
        lock_released = __release_lock(config.get("lock_dir"))
        time.sleep(SLEEP_BEFORE_NEXT_RUN)

def __load_config():
    parser = SafeConfigParser()
    parser.read(CONFIG_FILE)

    config = {}

    for section in parser.sections():
        config[section.lower()] = {}
        for name, value in parser.items(section):
            config[section.lower()][name] = value

    return config

def __can_aquire_lock(lock_dir):
    if not os.path.exists(lock_dir):
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

if __name__ == "__main__":
    drive()
