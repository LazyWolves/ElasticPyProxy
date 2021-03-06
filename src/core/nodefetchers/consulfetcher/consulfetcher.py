import requests
from src.core.nodefetchers.basefetcher import BaseFetcher

class ConsulFetcher(BaseFetcher):

    """ Class for fetching live backends discovered by consul

        Contains methods to fetch live backends from consul using consul catalog API
        To make this class work properly, ep2 config must have aws section with
        the following

        - consul ip - default is 127.0.0.1
        - consul api port - default is 8500
        - service name registered with consul
        - tags - tags to filter
        - only_passing - to select nodes on which the service checks are passing

        Args:
            **kwargs (dictionary) : Dictionary containing params
    """

    def __init__(self, **kwargs):

        """ Init method for this class

            Method initialise consul variables
        """
        self.consul_ip = kwargs.get("consul_ip")
        self.consul_port = kwargs.get("consul_port")
        self.service_name = kwargs.get("service_name")
        self.tags = kwargs.get("tags")
        self.logger = kwargs.get("logger")
        self.only_passing = kwargs.get("only_passing")

    def __check_response(self):
        return True

    def __get_formatted_tags(self, tags):

        """
            Method to format list of tags into 'tag=<tag_value>&tag=...' format

            Args:
                tags (list): List of tags

            Returns:
                string: Formatted tags
        """
        formatted_tag_list = ["tag={tag}".format(tag=tag) for tag in tags]
        formatted_tags = "&".join(formatted_tag_list)

        return formatted_tags

    def fetch(self):

        """ Method for fetching backends

            This method queries consul catalog APIs to

            Returns:
                list : List of backends
        """
        consul_request_url_base = "http://{consul_ip}:{consul_port}/v1/catalog".format(
                                        consul_ip=self.consul_ip,
                                        consul_port=self.consul_port
                                   )
        consul_service_path = "/service"
        consul_passing_str = "passing"
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

        if "?" in consul_request_url_with_service:
            url_parts_joiner = "&"
        else:
            url_parts_joiner = "?"

        if self.only_passing == True:
            consul_request_url_with_service = "{consul_request_url_with_service}{url_parts_joiner}{consul_passing_str}".format(
                                                    consul_request_url_with_service=consul_request_url_with_service,
                                                    consul_passing_str=consul_passing_str,
                                                    url_parts_joiner=url_parts_joiner
                                              )

        consul_response_json = None

        try:
            consul_response = requests.get(consul_request_url_with_service)
            consul_response_json = consul_response.json()
        except Exception as ex:
            self.logger.critical("Failed to fetch consul nodes : {}".format(str(ex)))
            return consul_response_json

        node_ips = []

        for node in consul_response_json:
            node_ips.append(node.get("Address"))

        return node_ips

if __name__ == "__main__":
    cf = ConsulFetcher(consul_ip="127.0.0.1", consul_port=8500, service_name="web",tags=["apache","web"])
    print (cf.fetch())
