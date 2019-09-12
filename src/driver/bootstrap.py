from src.core.haproxyupdater.haproxyupdate import HaproxyUpdate
from src.core.nodefetchers.awsfetcher.awsfetcher import AwsFetcher
from src.core.nodefetchers.orchestrator import get_orchestrator_handler

def bootstrap(**kwargs):
    config = kwargs.get("config")
    haproxy_config = config.get("haproxy")

    orchestrator = haproxy_config.get("orchestrator")

    orchestratorHandler = get_orchestrator_handler(config)
    asg_ips = orchestratorHandler.fetch()

    haproxyupdater = HaproxyUpdate(**haproxy_config)
    haproxyupdater.update_node_list(asg_ips)
    updated = haproxyupdater.update_haproxy_by_config_reload(update_only=True)

    if updated:
        running = start_if_not_running(config.get("pid_file"))
        return running

    return updated_and_reloaded

    
