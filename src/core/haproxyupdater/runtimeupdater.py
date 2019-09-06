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
            "active_nodes": active_nodes,
            "inactive_nodes": inactive_nodes
        }

        return True, nodes

    @staticmethod
    def update_runtime_util(haproxy_sock, node_ips, nodes):
        active_nodes = nodes.get("active_nodes")
        inactive_nodes = nodes.get("inactive_nodes")

    @staticmethod
    def update_haproxy_runtime(**kwargs):
        node_ips = kwargs.get("nodes")
        port = kwargs.get("port")
        sock_file = kwargs.get("sock_file")
        backend_name = kwargs.get("node_name")

        socketHandler = SocketHandler(sock_file=sock_file)

        socket_created = socketHandler.create_socket()

        if not socket_created:SocketHandler
            return False

        got_status, nodes = RuntimeUpdater.__get_haproxy_stats(socketHandler, backend_name)

        if not got_status:
            return False

        updated = RuntimeUpdater.update_runtime_util(socketHandler, node_ips, nodes)

        if not updated:
            return False

        return True
