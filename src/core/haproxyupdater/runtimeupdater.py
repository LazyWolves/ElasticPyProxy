"""
.. module:: runtimeupdater
   :synopsis: Module for updating haproxy at runtime

"""

import os
from .sockethandler import SocketHandler


class RuntimeUpdater(object):

    """ Class for updating haproxy at runtime

        This class conatins methods for updating haproxy backends at
        runtime without reloading it.

        This is done by communicating with haproxy over the unix
        socket file expsed by it.

        Once ep2 gets the ips/hostnames of the live backends, it
        communicates with haproxy over socket, extracts servers
        from inactive pool and updating their address with that of
        the live ones.
    """

    @staticmethod
    def __get_haproxy_stats(haproxy_sock, backend_name, logger=None):

        """ Method for getting haproxy stats

            Gets status information from haproxy over sockets.
            Status information includes list of beckends that are live
            and those which are disabled.

            Args:
                haproxy (str) : location of haproxy socket file
                backend_name (str) : name of the haproxy backend that we want to update
                logger (object) : logger object

            Returns:
                bool : Successfully fetched stats or not
                dict :  Dictionary of active nodes and inactive nodes
        """

        # command that will be sent to haproxy socket
        SHOW_STATUS = "show stat\n"

        # get stats
        has_stat, stats = haproxy_sock.send_command(command=SHOW_STATUS)
        if not has_stat:

            logger.critical("Failed to fetch haproxy status")
            return False, None
        
        slots = stats.split("\n")
        active_nodes = {}
        inactive_nodes = []

        # Iterate over the nodes and get active and inactive/disabled backends
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

        """ Method for updating haproxy backends using unix socket

            This method updates the haproxy backends by sending commands over the
            exposed unix socket.

            **Working**

            -   First it iterates over the active backends currently present in haproxy.
            -   If they are not present in the current fetched list of backends, then we 
                disable those backends and add them to the inactive pool.
            -   Next we iterate over the list of current live nodes fetched from orchestrator
            -   if they are already present as live backends in haproxy **even after the above
                elimination** then we skip.
            -   If they are not present then we fetch a inactive node from the inactive pool,
                change its address to that of the live node and enable back that node.

            Args:
                haproxy_sock (str) : Location of the haproxy unix socket file
                node_ips (list) : List of current live nodes fetched from orchestrator. (IP or hostname)
                nodes (dictionary) : Dictionary conatining haproxy active and inactive backends
                backend_name (str) : Name of the haproxy backend that needs to be updated.
                port (int) : port for the backend nodes
                logger (object) : Logger object 

            Retuns:
                dict : Dictionary conatining active node_ips and inactive nodes count
        """
        active_nodes = nodes.get("active_nodes")
        inactive_nodes = nodes.get("inactive_nodes")

        # Command templates for the comands
        SET_ADDR = "set server {backend_name}/{node_name} addr {addr} port {port}\n"
        MAKE_READY = "set server {backend_name}/{node_name} state ready\n"
        MAKE_MAINT = "set server {backend_name}/{node_name} state maint\n"

        unused_active_nodes = []

        '''
            Iterate over the haproxy active nodes and check if they are still active.
            If they are not active, add them to inactive pool.
        '''
        for active_node in active_nodes:
            if active_node not in node_ips:

                # send command to disable this node
                command_status, _ = haproxy_sock.send_command(command=MAKE_MAINT.format(backend_name=backend_name, node_name=active_nodes[active_node]))
                if command_status:

                    # if command execution was success then add it to inactive nodes list
                    inactive_nodes.append(active_nodes[active_node])
                    logger.info("Removed node:{server}/ip:{ip} from active backend pool".format(server=active_nodes[active_node], ip=active_node))
                else:
                    logger.critical("Failed removing node:{server}/ip:{ip}".format(server=active_nodes[active_node], ip=active_node))

                unused_active_nodes.append(active_node)

        for unused_active_node in unused_active_nodes:
            del active_nodes[unused_active_node]

        '''
            Iterate over the nodes present in the current active list
            and if they are not present in the active haproxy backend, add
            them to haproxy by converting an inactive node to an active node.
        '''
        for new_node_ip in node_ips:
            if active_nodes.get(new_node_ip):
                print ("skipping " + str(new_node_ip))
                continue
            else:
                if len(inactive_nodes) > 0:

                    # Fetch an inactive node from inactive list. 
                    node_to_use = inactive_nodes.pop(0)
                    logger.info("Using inactive node:{node} for ip:{ip}".format(node=node_to_use, ip=new_node_ip))

                    # Send command to socket for changing the address of that inactive node to the address of the
                    # current live backend under consideration
                    command_status, _ = haproxy_sock.send_command(command=SET_ADDR.format(backend_name=backend_name, node_name=node_to_use, addr=new_node_ip, port=port))
                    if not command_status:

                        '''
                            Log error
                        '''
                        logger.critical("Failed to change {node} backend addr to ip:{ip}".format(node=node_to_use, ip=new_node_ip))
                    else :
                        logger.info("Successfully changed {node} backend addr to ip:{ip}".format(node=node_to_use, ip=new_node_ip))

                    # Once the address has been changed successfully, make this inactive node active
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
