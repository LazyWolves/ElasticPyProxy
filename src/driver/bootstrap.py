from src.core.haproxyupdater.haproxyupdate import HaproxyUpdate
from src.core.nodefetchers.awsfetcher.awsfetcher import AwsFetcher
from src.core.nodefetchers.orchestrator import get_orchestrator_handler
from src.core.haproxyupdater.haproxyreloader import HaproxyReloader
import os

COULD_NOT_READ_PID_FILE = "COULD_NOT_READ_PID_FILE"

def bootstrap(**kwargs):
    config = kwargs.get("config")
    logger = kwargs.get("logger")
    haproxy_config = config.get("haproxy")
    logger = kwargs.get("logger")

    orchestratorHandler = get_orchestrator_handler(config, logger=logger)
    asg_ips = orchestratorHandler.fetch()

    haproxyupdater = HaproxyUpdate(**haproxy_config, logger=logger)
    haproxyupdater.update_node_list(asg_ips)
    updated = haproxyupdater.update_haproxy_by_config_reload(update_only=True)

    if updated:
        running = __start_if_not_running_else_reload(haproxy_config, logger=logger)
        return running, haproxyupdater, orchestratorHandler

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
        print (ex)

        return False, None

    return True, None

def __start_if_not_running_else_reload(config, logger=None):
    
    is_haproxy_running, error = __is_haproxy_running(config, logger=logger)

    if not is_haproxy_running and config.get("start_by") == "systemd":
        started = HaproxyReloader.start_by_systemd(config.get("service_name"))

    return HaproxyReloader.reload_haproxy(**config)
