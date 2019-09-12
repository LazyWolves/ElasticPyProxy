from .awsfetcher.awsfetcher import AwsFetcher

ORCHESTRATOR_HANDLERS = {
    "aws": AwsFetcher
}

def get_orchestrator_handler(orchestator):
    orchestrator = orchestator.lower()

    return ORCHESTRATOR_HANDLERS.get(orchestrator)
