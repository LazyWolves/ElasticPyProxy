"""
.. module:: orchestrator
   :synopsis: Module for initialising backend fetcher

"""

from .awsfetcher.awsfetcher import AwsFetcher

def get_orchestrator_handler(config, logger=None):

    """ Method for deciding which fetcher to use

        Decide which fetcher to use depending on the orchestrator mentioned
        in the config.

        Args:
            config (dictionary) : dictionary holding ep2 config
            logger (object) : logger object

        Returns:
            object : Backend fetcher

    """
    orchestrator = config.get("haproxy").get("orchestrator")

    if orchestrator.lower() == "aws":
        handler = prepare_aws_handler(config.get(orchestrator))

    return handler

def prepare_aws_handler(config):

    """ Prepares the AWS fetcher

        Args:
            config (dictionary) : dictionary containing ep2 config

        Returns:
            srv.nodefetchers.awsfetcher.awsfetcher : Aws backend fetecher
    """
    aws_access_key_id = config.get("aws_access_key_id")
    aws_secret_access_key = config.get("aws_secret_access_key")
    ip_type = config.get("ip_type")
    asg_name = config.get("asg_name")
    region_name = config.get("region_name")

    aws_handler = AwsFetcher(aws_access_key_id=aws_access_key_id,
                             aws_secret_access_key=aws_secret_access_key,
                             ip_type=ip_type,
                             asg_name=asg_name,
                             region_name=region_name
                            )

    return aws_handler
