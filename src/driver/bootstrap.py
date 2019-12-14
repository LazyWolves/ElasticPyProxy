"""
.. module:: bootstrap
   :synopsis: Bootstrap EP2 controller

"""

from src.core.haproxyupdater.haproxyupdate import HaproxyUpdate
from src.core.nodefetchers.awsfetcher.awsfetcher import AwsFetcher
from src.core.nodefetchers.orchestrator import get_orchestrator_handler
from src.core.haproxyupdater.haproxyreloader import HaproxyReloader
from .drivercache import DriverCache
import os

COULD_NOT_READ_PID_FILE = "COULD_NOT_READ_PID_FILE"

def bootstrap(**kwargs):
    """Method to bootstrap EP2 controller

    This method bootstraps EP2 to creates the neccessary objects and returns it
    to the driver.

    Args:
        **kwargs (object) : kwargs must contains config dictionary, logger object.

    Returns:
        bool: Whether bootstrap updater was successfull or not
        src.core.haproxyupdater.haproxyupdate.HaproxyUPdate: Object for updating haproxy config
        src.core.nodefetchers.basefetcher: Object for fetching backends
    """

    config = kwargs.get("config")
    logger = kwargs.get("logger")
    haproxy_config = config.get("haproxy")
    logger = kwargs.get("logger")

    orchestratorHandler = get_orchestrator_handler(config, logger=logger)
    asg_ips = orchestratorHandler.fetch()

    if asg_ips == None or len(asg_ips) == 0:

        '''
            This is critical. Bootstrap cannnot work with 0 backends. EP2 must abort run
        '''
        logger.critical("No backends available. Bootstrap cannot proceed with 0 backends. Terminating EP2")
        exit (2)

    # Initialise driver cache with the fetched IPs
    driverCache = DriverCache(set(asg_ips))

    #Initialise haproxyupdater
    haproxyupdater = HaproxyUpdate(**haproxy_config, logger=logger)

    # Set the fectched nodes in haproxyupdater
    haproxyupdater.update_node_list(asg_ips)

    # update and reload haproxy
    updated = haproxyupdater.update_haproxy_by_config_reload(update_only=True)

    if updated:

        '''
            Start haproxy if its already not running. If its running then simply reload
            so that the new config takes affect.
        '''
        running = __start_if_not_running_else_reload(haproxy_config, logger=logger)
        return running, haproxyupdater, orchestratorHandler, driverCache

    logger.critical("Haproxy config update at botstrap failed")

    return updated, haproxyupdater, orchestratorHandler, driverCache

def __is_haproxy_running(config, logger=None):

    """Method for checking if haproxy is running

        This method checks whether haproxy is running by sending kill signal 0 to the PID
        of haproxy.

        Args:
            config (dictionary) :  haproxy config dictionary
            logger (object) : logger object

        Returns:
            bool : Whether haproxy is running or not
            str : error string

    """
    pid_file = config.get("pid_file")

    # return false if PID file path is invalid
    if not os.path.exists(pid_file):

        logger.warning("Haproxy pid file not found. Attempt to start haproxy will be made")
        return False, None

    error = None

    try:
        with open(pid_file) as f:
            pid = int(f.readline())
    except Exception as ex:
        '''
            Log exception
        '''

        logger.warning("Could not access haproxy pid file. Attempt to start haproxy will be made")
        return False, None

    try:

        # Try to send kill signal 0 to haproxy process
        os.kill(pid, 0)
    except OSError as ex:
        '''
            Haproxy is not running, log
        '''

        # Since there is an exception, haproxy is not running
        logger.info("Haproxy is not running")

        return False, None

    return True, None

def __start_if_not_running_else_reload(config, logger=None):

    """Method to start/reload haproxy if it is not running

        Args:
            config (dictionary) : haproxy config dictionary
            logger (object) : logging object

        Returns:
            bool : Whether successfully reloaded or not
    """
    
    is_haproxy_running, error = __is_haproxy_running(config, logger=logger)

    '''
        If haproxy is not running and ep2 is configured to start haproxy
        via systemd, then start it by systemd. If systemd is not required
        then do a not reload via binary. This is taken care by the reloader
        module.
    '''
    if not is_haproxy_running and config.get("start_by") == "systemd":
        started = HaproxyReloader.start_by_systemd(config.get("service_name"), logger)

    return HaproxyReloader.reload_haproxy(**config, logger=logger)
