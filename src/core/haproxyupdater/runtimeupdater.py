import os
from .sockethandler import SocketHandler


class RuntimeUpdater(object):

    @staticmethod
    def __get_haproxy_stats(haproxy_sock, backend_name, logger=None):

        SHOW_STATUS = "show stat\n"
        has_stat, stats = haproxy_sock.send_command(command=SHOW_STATUS)
        if not has_stat:

            logger.critical("Failed to fetch haproxy status")
            return False, None
        
        slots = stats.split("\n")
        active_nodes = {}
        inactive_nodes = []

        for node in slots:
            node_properties = node.split(",")
            if len(node_properties) > 80 and node_properties[0] == backend_name:
                node_name = node_properties[1]
                if node_name.lower() == "backend" or node_name.lower() == "frontend":
                    continue
                node_state = node_properties[17]
                node_addr = node_properties[73].split(":")[0]

                if node_state == "MAINT":
                    inactive_nodes.append(node_name)
                else:
                    active_nodes[node_addr] = node_name

        nodes = {
            "active_nodes": active_nodes,
            "inactive_nodes": inactive_nodes
        }

        return True, nodes

    @staticmethod
    def update_runtime_util(haproxy_sock, node_ips, nodes, backend_name, port, logger=None):
        active_nodes = nodes.get("active_nodes")
        inactive_nodes = nodes.get("inactive_nodes")

        SET_ADDR = "set server {backend_name}/{node_name} addr {addr} port {port}\n"
        MAKE_READY = "set server {backend_name}/{node_name} state ready\n"
        MAKE_MAINT = "set server {backend_name}/{node_name} state maint\n"

        unused_active_nodes = []

        for active_node in active_nodes:
            if active_node not in node_ips:
                command_status, _ = haproxy_sock.send_command(command=MAKE_MAINT.format(backend_name=backend_name, node_name=active_nodes[active_node]))
                if command_status:
                    inactive_nodes.append(active_nodes[active_node])
                    logger.info("Removed node:{server}/ip:{ip} from active backend pool".format(server=active_nodes[active_node], ip=active_node))
                else:
                    logger.critical("Failed removing node:{server}/ip:{ip}".format(server=active_nodes[active_node], ip=active_node))

                unused_active_nodes.append(active_node)

        for unused_active_node in unused_active_nodes:
            del active_nodes[unused_active_node]

        for new_node_ip in node_ips:
            if active_nodes.get(new_node_ip):
                print ("skipping " + str(new_node_ip))
                continue
            else:
                if len(inactive_nodes) > 0:
                    node_to_use = inactive_nodes.pop(0)
                    logger.info("Using inactive node:{node} for ip:{ip}".format(node=node_to_use, ip=new_node_ip))

                    command_status, _ = haproxy_sock.send_command(command=SET_ADDR.format(backend_name=backend_name, node_name=node_to_use, addr=new_node_ip, port=port))
                    if not command_status:

                        '''
                            Log error
                        '''
                        logger.critical("Failed to change {node} backend addr to ip:{ip}".format(node=node_to_use, ip=new_node_ip))
                    else :
                        logger.info("Successfully changed {node} backend addr to ip:{ip}".format(node=node_to_use, ip=new_node_ip))
                    command_status, _ = haproxy_sock.send_command(command=MAKE_READY.format(backend_name=backend_name, node_name=node_to_use))
                    if not command_status:

                        '''
                            Log error
                        '''
                        logger.critical("Failed to activate node:{node}".format(node=node_to_use))
                    else:
                        logger.info("Sucessfully activated node:{node}".format(node=node_to_use))
                else:

                    '''
                        Log error
                    '''
                    logger.critical("Insufficient nodes in inactive pool. Please increase node_slots and retsart ep2")

        stats = {
            "inactive_nodes_count": len(inactive_nodes),
            "nodes": node_ips
        }

        return True, stats

    @staticmethod
    def update_haproxy_runtime(**kwargs):
        node_ips = kwargs.get("node_ips")
        port = kwargs.get("port")
        sock_file = kwargs.get("sock_file")
        backend_name = kwargs.get("node_name")
        logger = kwargs.get("logger")

        socketHandler = SocketHandler(sock_file=sock_file, logger=logger)

        got_status, nodes = RuntimeUpdater.__get_haproxy_stats(socketHandler, backend_name, logger=logger)

        if not got_status:
            return False, None

        updated, stats = RuntimeUpdater.update_runtime_util(socketHandler, node_ips, nodes, backend_name, port, logger)
        if not updated:
            return False, None

        return True, stats
