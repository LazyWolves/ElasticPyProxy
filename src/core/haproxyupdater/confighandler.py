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

        could_read, template = ConfigHandler.read_write_file(operation="read", file=template_file)

        if not could_read:
            return False

        node_template = "server node{node_id} {ip}:{port} check"
        
        nodes_str = ""

        for node_id, node_ip in enumerate(node_list):
            haproxy_node = node_template.format(node_id=node_id, ip=node_ip, port=backend_port)
            nodes_str += (haproxy_node + "\n")

        config_from_template = template.format(nodes=nodes_str)

        if not ConfigHandler.read_write_file(operation="write", file=haproxy_config_file, content=config_from_template):
            return False

        return True

    @staticmethod
    def read_write_file(**kwargs):
        operation = kwargs.get("operation")
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
                    return True, None
        except Exception as ex:

            '''
                Log exception
            '''
            return False, None

        return False, None

if __name__ == "__main__":
    ConfigHandler.update_config(haproxy_config_file="test", template_file="/home/deep/elasticpyproxy/etc/haproxy.cofig.template", node_list=["11.11.11.11", "44.44.44.44"], backend_port="22222")
