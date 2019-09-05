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
            if len()
            

