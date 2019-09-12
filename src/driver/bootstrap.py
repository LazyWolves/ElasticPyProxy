from src.core.haproxyupdater.haproxyupdate import HaproxyUpdate
from src.core.nodefetchers.awsfetcher.awsfetcher import AwsFetcher
from src.core.nodefetchers.orchestrator import get_orchestrator_handler

def bootstrap(**kwargs):
    config = kwargs.get("config")
    haproxy_config = config.get("haproxy")

    orchestrator = haproxy_config.get("orchestrator")

    orchestratorHandler = get_orchestrator_handler(config)
    asg_ips = orchestratorHandler.fetch()

    haproxyupdater = HaproxyUpdate(haproxy_config_file=haproxy_config.get("haproxy_config_file"),
                                   template_file=haproxy_config.get("template_file"),
                                   )

    
