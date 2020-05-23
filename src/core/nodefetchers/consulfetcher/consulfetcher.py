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
                                                service_name=self.service_name
                                           )

        if self.tags and len(self.tags) != 0:
            formatted_tags = self.__get_formatted_tags(self.tags)

            consul_request_url_with_service = "{consul_request_url_with_service}?{formatted_tags}".format(
                                                    consul_request_url_with_service=consul_request_url_with_service,
                                                    formatted_tags=formatted_tags
                                              )

        consul_response = requests.get(consul_request_url_with_service)
        consul_response_json = consul_response.json()

        node_ips = []

        for node in consul_response_json:
            node_ips.append(node.get("Address"))

        return node_ips

if __name__ == "__main__":
    cf = ConsulFetcher(consul_ip="127.0.0.1", consul_port=8500, service_name="web",tags=["apache","web"])
    print (cf.fetch())
