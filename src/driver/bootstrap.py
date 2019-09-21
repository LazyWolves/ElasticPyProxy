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

    This method bootstraps EP2 Ot creates the neccessary objects and returns it
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

    driverCache = DriverCache(set(asg_ips))

    haproxyupdater = HaproxyUpdate(**haproxy_config, logger=logger)
    haproxyupdater.update_node_list(asg_ips)
    updated = haproxyupdater.update_haproxy_by_config_reload(update_only=True)

    if updated:
        running = __start_if_not_running_else_reload(haproxy_config, logger=logger)
        return running, haproxyupdater, orchestratorHandler, driverCache

    logger.critical("Haproxy config update at botstrap failed")

    return updated, haproxyupdater, orchestratorHandler

def __is_haproxy_running(config, logger=None):
    pid_file = config.get("pid_file")
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
        return False

    try:
        os.kill(pid, 0)
    except OSError as ex:
        '''
            Haproxy is not running, log
        '''

        logger.info("Haproxy is not running")

        return False, None

    return True, None

def __start_if_not_running_else_reload(config, logger=None):
    
    is_haproxy_running, error = __is_haproxy_running(config, logger=logger)

    if not is_haproxy_running and config.get("start_by") == "systemd":
        started = HaproxyReloader.start_by_systemd(config.get("service_name"), logger)

    return HaproxyReloader.reload_haproxy(**config, logger=logger)
