"""
.. module:: orchestrator
   :synopsis: Module for initialising backend fetcher

"""

from .awsfetcher.awsfetcher import AwsFetcher
from .consulfetcher.consulfetcher import ConsulFetcher

DEFAULT_CONSUL_IP = "127.0.0.1"
DEFAULT_CONSUL_PORT = "8500"

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
        handler = prepare_aws_handler(config.get(orchestrator), logger)

    if orchestrator.lower() == "consul":
        handler = prepare_consul_handler(config.get(orchestrator), logger)

    return handler

def prepare_aws_handler(config, logger):

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
                             region_name=region_name,
                             logger=logger
                            )

    return aws_handler

def prepare_consul_handler(config, logger):
    consul_ip = config.get("consul_ip", DEFAULT_CONSUL_IP)
    consul_port = config.get("consul_port", DEFAULT_CONSUL_PORT)
    service_name = config.get("service_name")
    tags = config.get("tags")
    only_passing = bool(config.get("only_passing", True))

    tags_list = []

    if tags:
        tags_list = [tag.strip() for tag in tags.split(",")]

    consul_fetcher = ConsulFetcher(
                        consul_ip=consul_ip,
                        consul_port=consul_port,
                        service_name=service_name,
                        tags=tags_list,
                        only_passing=only_passing,
                        logger=logger
                    )

    return consul_fetcher
