from .awsfetcher.awsfetcher import AwsFetcher

def get_orchestrator_handler(config):
    orchestrator = config.get("haproxy").get("orchestrator")

    if orchestrator.lower() == "aws":
        handler = prepare_aws_handler(config.get(orchestrator))

    return handler

def prepare_aws_handler(config):
    aws_access_key_id = config.get("aws_access_key_id")
    aws_secret_access_key = config.get("aws_secret_access_key")
    ip_type = config.get("ip_type")
    asg_name = config.get("asg_name")

    aws_handler = AwsFetcher(aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key,
                             ip_type=ip_type,
                             asg_name=asg_name
                            )

    return aws_handler
