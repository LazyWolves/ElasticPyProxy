import os
from .sockethandler import SocketHandler


class RuntimeUpdater(object):

    @staticmethod
    def __get_haproxy_stats(haproxy_sock, backend_name):

        SHOW_STATUS = "show stat\n"
        has_stat, stats = haproxy_sock.send_command(command=SHOW_STATUS)
        if not has_stat:
            return False, None
        
        slots = stats.split("\n")
        active_nodes = {}
        inactive_nodes = []

        for node in slots:
            node_properties = node.split(",")
            if len(node_properties) > 80 and node_properties[0] == backend_name:
                node_name = node_properties[1]
                if node_name == "BACKEND":
                    continue
                node_state = node_properties[17]
                node_addr = node_properties[73].split(":")[0]

                if node_state == "MAINT":
                    inactive_nodes.append(node_name)
                else:
                    active_nodes[node_addr] = node_name

        nodes = {
            "active": active_nodes,
            "inactive_nodes": inactive_nodes
        }

        return True, nodes
            

