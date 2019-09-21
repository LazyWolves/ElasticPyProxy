"""
.. module:: driver
   :synopsis: Main entry point for ep2

"""

from configparser import SafeConfigParser
import time
import optparse
import os
from .defaultparams import default_params
from .bootstrap import bootstrap
import logging

CONFIG_FILE = default_params.get("config")
LOCK_FILE = default_params.get("lock_file")

def drive():
    """
        **Method for starting ep2**

        This is the entry method which starts ep2 controller. It calls bootstrap module
        for bootstrapping ep2, reads ep2 config, initialises haproxy and starts the
        **poll-update-repeat loop**

    """
    global CONFIG_FILE
    global LOCK_FILE

    # parse args
    parser = optparse.OptionParser()
    parser.add_option('-f', action="store", dest="config", help="Config file")
    options, args = parser.parse_args()

    # if config file available as argument, then use it
    if options.config:
        CONFIG_FILE = options.config

    # parse the config and create a dictionary
    config = __load_config()
    haproxy_config = config.get("haproxy")

    # load values/defaults
    SLEEP_BEFORE_NEXT_RUN = int(haproxy_config.get("sleep_before_next_run", default_params.get("sleep_before_next_run")))
    SLEEP_BEFORE_NEXT_LOCK_ATTEMPT = int(haproxy_config.get("sleep_before_next_lock_attempt", default_params.get("sleep_before_next_lock_attempt")))
    LOG_FILE = haproxy_config.get("log_file", default_params.get("log_file"))

    logger = __setup_logging(LOG_FILE)

    if not __sanitize_config(config):

       # if configs fail sanity checks then exit ep2. Issue should have been logged already
        exit(2)

    # bootstrap the controller
    running, haproxyupdater, orchestratorHandler, driverCache = bootstrap(config=config, logger=logger)

    if not running:

        '''
            Error has already been logged. Exit with status code 2
        '''
        exit(2)

    '''
        After this point, Haproxy should be running with the lastest IPs
        fetched from the orchestrator. Now we can begin with the poll-update-repeat
        loop for updating backends fetched from ochestrator
    '''

    print ("Entering state loop...")
    i = 1
    while True:
        print ("run " + str(i))

        # Fetch backend IPs from orchestrator handler
        asg_ips = orchestratorHandler.fetch()

        # Proceed with updation only if IPs are not none
        if asg_ips != None:
            print (asg_ips)

            # check if update is actually neccessary. Compare with cache
            should_update = driverCache.need_to_update(set(asg_ips))
            if should_update:
                logger.info("Backends changed. Proceeding to update haproxy")

                # Inform the haproxyupdater about the new nodes
                haproxyupdater.update_node_list(asg_ips)

                # Update haproxy
                updated = haproxyupdater.update_haproxy()
                print (updated)
            else:
                logger.info("Backends not changed. Skipping update")
        else:
            logger.critical("No backends found. Skippin run")

        # sleep for configured time before the next run
        time.sleep(SLEEP_BEFORE_NEXT_RUN)
        i += 1

def __setup_logging(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger_handler = logging.FileHandler(log_file)
    logger_handler.setLevel(logging.DEBUG)
    logger_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
    logger_handler.setFormatter(logger_formatter)
    logger.addHandler(logger_handler)

    return logger

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
                lock_file.write(str(os.getpid()))
            return True
        return False
    except Exception as ex:
        print (ex)
        return False

def __release_lock(lock_dir):
    lock_file = os.path.join(lock_dir, LOCK_FILE)
    try:
        if os.path.exists(lock_file):
            os.unlink(lock_file)
        return True
    except Exception as ex:
        print (ex)
        return False

def __sanitize_config(config):

    return True

if __name__ == "__main__":
    drive()
