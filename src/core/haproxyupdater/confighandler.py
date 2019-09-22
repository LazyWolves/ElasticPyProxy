from jinja2 import Template

'''
    Config hanfler for handlung haproxy config file
'''

class ConfigHandler(object):
    """
    """

    @staticmethod
    def update_config(**kwargs):
        
        # get desired params
        haproxy_config_file = kwargs.get("haproxy_config_file")
        template_file = kwargs.get("template_file")
        node_list = kwargs.get("node_list")
        backend_port = kwargs.get("backend_port")
        inactive_nodes_count = kwargs.get("inactive_nodes_count")
        node_slots = kwargs.get("node_slots")
        logger = kwargs.get("logger")

        could_read, template = ConfigHandler.read_write_file(operation="read", file=template_file, logger=logger)

        if not could_read:

            logger.critical("Could not read template file : {}".format(template_file))
            return False

        node_template = "    server node{node_id} {ip}:{port} check"
        inactive_nodes_template = "    server-template node {count} 10.0.0.1:8080 check disabled"

        nodes_str = ""

        if inactive_nodes_count and inactive_nodes_count != 0:
            node_id = inactive_nodes_count + 1

            for node_ip in node_list:
                haproxy_node = node_template.format(node_id=node_id, ip=node_ip, port=backend_port)
                nodes_str += (haproxy_node + "\n")
                node_id += 1

            inactive_nodes = inactive_nodes_template.format(count=inactive_nodes_count)
            nodes_str += (inactive_nodes + "\n")

        else:
            inactive_nodes_count = node_slots - len(node_list)
            node_id = inactive_nodes_count + 1

            for node_ip in node_list:
                haproxy_node = node_template.format(node_id=node_id, ip=node_ip, port=backend_port)
                nodes_str += (haproxy_node + "\n")
                node_id += 1

            if inactive_nodes_count != 0:
                inactive_nodes = inactive_nodes_template.format(count=inactive_nodes_count)
                nodes_str += (inactive_nodes + "\n")

        template = Template(template)
        config_from_template = template.render({"nodes": nodes_str})

        could_write, _ = ConfigHandler.read_write_file(operation="write", file=haproxy_config_file, content=config_from_template)

        if not could_write:

            logger.critical("Failed to update haproxy config file : {}".format(haproxy_config_file))
            return False

        logger.info("Successfully updated haproxy config")

        return True

    @staticmethod
    def read_write_file(**kwargs):
        operation = kwargs.get("operation")
        file = kwargs.get("file")
        logger = kwargs.get("logger")

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
            logger.critical("Encountered following read/write exception : {}".format(str(ex)))
            return False, None

        return False, None

if __name__ == "__main__":
    ConfigHandler.update_config(haproxy_config_file="test", template_file="/home/deep/elasticpyproxy/etc/haproxy.cofig.template", node_list=["11.11.11.11", "44.44.44.44"], backend_port="22222")
