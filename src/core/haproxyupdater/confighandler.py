'''
    Config hanfler for handlung haproxy config file
'''

class ConfigHandler(object):

    @staticmethod
    def update_config(**kwargs):
        
        # get desired params
        haproxy_config_file = kwargs.get("haproxy_config_file")
        template_file = kwargs.get("template_file")
        node_list = kwargs.get("node_list")
        backend_port = kwargs.get("backend_port")

        # load config and templates
        with open(haproxy_config_file) as f:
            haproxy_config = f.read()

        with open(template_file) as f:
            template = f.read()

        node_template = "server node{node_id} {ip}:{port} check"
        
        nodes_str = ""
