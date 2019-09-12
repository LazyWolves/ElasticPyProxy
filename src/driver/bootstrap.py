from src.core.haproxyupdater.haproxyupdate import HaproxyUpdate
from src.core.nodefetchers.awsfetcher.awsfetcher import AwsFetcher
from src.core.nodefetchers.orchestrator import get_orchestrator_handler

def bootstrap(**kwargs):
    config = kwargs.get("config")

    orchestrator = config.get("orchestrator")

    orchestratorHandler = get_orchestrator_handler(config)

    
