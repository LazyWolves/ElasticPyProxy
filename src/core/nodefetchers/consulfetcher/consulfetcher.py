import requests
from src.core.nodefetchers.basefetcher import BaseFetcher

class ConsulFetcher(BaseFetcher):

    def __init__(self, **kwargs):
        self.consul_ip = kwargs.get("consul_ip")
        self.consul_port = kwargs.get("consul_port")
        self.service_name = kwargs.get("service_name")
        self.tags = kwargs.get("tags")

    def __check_response(self):
        return True

    def __get_formatted_tags(self, tags):
        formatted_tag_list = ["tag={tag}".format(tag=tag) for tag in tags]
        formatted_tags = "&".join(formatted_tag_list)

        return formatted_tags

    def fetch(self):
        consul_request_url_base = "http://{consul_ip}:{consul_port}/v1/catalog".format(
                                        consul_ip=self.consul_ip,
                                        consul_port=self.consul_port
                                   )
        consul_service_path = "/service"
        consul_request_url_with_service = "{consul_request_url_base}{consul_service_path}/{service_name}".format(
                                                consul_request_url_base=consul_request_url_base,
                                                consul_service_path=consul_service_path,
                                                consul_request_url_with_service=self.service_name
                                           )
        
                                
