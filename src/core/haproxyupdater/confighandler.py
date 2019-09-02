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
        try:
            with open(haproxy_config_file) as f:
                haproxy_config = f.read()
        except Exception as ex:

            '''
                log error
            '''

            return False

        with open(template_file) as f:
            template = f.read()

        node_template = "server node{node_id} {ip}:{port} check"
        
        nodes_str = ""

        for node_id, node_ip in enumerate(node_list):
            haproxy_node = node_template.format(node_id=node_id, ip=node, port=backend_port)
            node_str += (haproxy_node + "\n")

        config_from_template = template.format(nodes=node_str)

        with open(haproxy_config_file, "w") as f:
            f.write(config_from_template)

    @staticmethod
    def read_write_file(**kwargs):
        operation = kwargs.get(operation)
        file = kwargs.get("file")
        if operation == "write":
            content = kwargs.get("content")

        try:
            if operation == "read":
                with open(file) as f:
                    return True, f.read()
            else:
                with open(file, "w") as f:
                    f.write(content)
                    return True
        except Exception as ex:

            '''
                Log exception
            '''
            return False

        return False
