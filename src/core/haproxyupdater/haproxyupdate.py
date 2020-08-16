"""
.. module:: haproxyupdate
   :synopsis: Module for updating haproxy

"""

import os
from .confighandler import ConfigHandler
from .runtimeupdater import RuntimeUpdater
from .haproxyreloader import HaproxyReloader

class HaproxyUpdate(object):

    """ Class for handling haproxy update and reload

        This class contains handlers which controls haproxy uptation and reload.
        Haproxy can be updated wither by updating its config file followed by
        a reload via systemd or via binary. The other way to reload haproxy is
        via the exposed socket. This type of update does not require any reload

        For updating via runtime haproxy needs to maintain a pool if inactive
        backends. When a new live backend comes, we can pull an inactive live backend
        and make it live changing its ip to that of the live backend

        Args:
            **kwargs (dictionary) : params in key/value dict format
    """
    def __init__(self, **kwargs):

        """ Init method for the class

            Extracts the desired params and stores them as instance variables
            Also it sanitisez the params

            Args:
                **kwargs (dictionary) : params in key/value dict format
        """

        # Extract the desired params
        self.haproxy_config_file = kwargs.get("haproxy_config_file")
        self.template_file = kwargs.get("template_file")
        self.backend_port = int(kwargs.get("backend_port"))
        self.node_list = kwargs.get("node_list")
        self.haproxy_binary = kwargs.get("haproxy_binary")
        self.start_by = kwargs.get("start_by")
        self.haproxy_socket_file = kwargs.get("haproxy_socket_file")
        self.pid_file = kwargs.get("pid_file")
        self.backend_name = kwargs.get("backend_name")
        self.update_type = kwargs.get("update_type")
        self.node_slots = int(kwargs.get("node_slots"))
        self.service_name = kwargs.get("service_name")
        self.backend_maxconn = kwargs.get("backend_maxconn")
        self.check_interval = kwargs.get("check_interval")
        self.sa_mode = kwargs.get("sa_mode", False)
        self.logger = kwargs.get("logger")

        """
            Valid methods to start haproxy.

            .. note::
                init methods is not supported yet.
        """
        self.valid_start_by = [
            "binary",
            "systemd",
            "init"
        ]

        """
            Valid methods to update haproxy
        """

        self.valid_update_types = [
            "update_by_config",
            "update_by_runtime"
        ]

    def __sanitise(self):

        """ Method to for performing sanity checks on the params

            This method will check that the params received are inline
            with what we desire.

            Returns:
                bool : Result of sanity check

        """
        if not os.path.isfile(self.haproxy_config_file):
            return False

        if not os.path.isfile(self.template_file):
            return False

        if self.backend_port < 0 or self.backend_port > 65536:
            return False

        if not self.backend_name:
            return False

        if self.node_slots and self.node_slots <= 0:
            return False

        if not self.update_type:
            return False

        if self.update_type not in self.valid_update_types:
            return False

        if not self.node_slots:
            return False

        if self.node_slots <=0:
            return False

        if not self.node_list:
            return False

        if not self.haproxy_socket_file:
            return False

        for sock_file in self.haproxy_socket_file.split(","):
            if not os.path.exists(sock_file.strip()):
                return False

        if self.update_type == "update_by_config":
            if not self.start_by:
                return False

            if not self.start_by in self.valid_start_by:
                return False

            if self.start_by == "systemd":
                if not self.service_name:
                    return False

            if self.start_by == "binary":
                if not self.haproxy_binary:
                    return False

                if not os.path.isfile(self.haproxy_binary):
                    return False

                if not self.pid_file:
                    return False

                if not os.path.isfile(self.pid_file):
                    return False

        return True

    def update_node_list(self, node_list):

        """Method to update active node list

           This method will e called to update the list of active backends.
           Haproxy needs to be updated and optionally reloaded if this list changes

           Args:
                node_list (list) : List containing IPs/Hostnames of active backends
        """
        self.node_list = node_list

    def update_agent_ip(self, agent_ip, agent_action):

        self.agent_ip = agent_ip
        self.agent_action = agent_action

    def update_haproxy(self):

        """ Updates haproxy config

            This method updates haproxy config with the help of the util methods.

            Returns:
                bool : Wether haproxy was updated successfully or not.

        """
        if not self.__sanitise():
            return False

        if self.update_type == "update_by_runtime":
            updated = self.__update_haproxy_by_runtime()

        else:
            updated = self.update_haproxy_by_config_reload()

        return updated

    def update_haproxy_by_config_reload(self, update_only=False):

        """ Method to update haproxy via config reload

            This method will update haproxy via updating its config and subsequently reloading it.
            The actual update will be done by the confighandler module and reload will be
            done by haproxyreloader. Optinaly is **upate_only** is set to True then only config
            will be updated and reload will not be done.

            Args:
                update_only (bool) : Whether only update is required or both update and reload is required.

            Returns:
                bool : Whether successfully updated/reloaded as the case may be
        """

        if self.update_type == "update_by_config":

            """
                If update is to be done via config updation, then total number of backend node
                slots will be set to the number of active backends found. This because, for
                update via config we do not require any pool of inactive nodes. So number of
                slots will be and should be equal to number of active backends.
            """

            # check for sa_mode

            if not self.sa_mode:
                self.node_slots = len(self.node_list)

        # check if EP2 is running in sa_mode

        if self.sa_mode == True:
            status, nodes = RuntimeUpdater.get_haproxy_stats(sock_file=self.haproxy_socket_file,
                                                     backend_name=self.backend_name,
                                                     logger=self.logger
                                                    )
            if not status:
                return status

            node_ips = nodes.get("active_nodes").keys() + [self.agent_ip]
            self.node_slots = len(node_ips)

            #update haproxy
            updated = ConfigHandler.update_config(haproxy_config_file=self.haproxy_config_file,
                                                template_file=self.template_file,
                                                node_list=node_ips,
                                                backend_port=self.backend_port,
                                                node_slots=self.node_slots,
                                                backend_maxconn=self.backend_maxconn,
                                                check_interval=self.check_interval,
                                                logger=self.logger
                                            )
        else:
            # update haproxy
            updated = ConfigHandler.update_config(haproxy_config_file=self.haproxy_config_file,
                                            template_file=self.template_file,
                                            node_list=self.node_list,
                                            backend_port=self.backend_port,
                                            node_slots=self.node_slots,
                                            backend_maxconn=self.backend_maxconn,
                                            check_interval=self.check_interval,
                                            logger=self.logger
                                            )

        if update_only:

            # if it was update only, the return
            return updated

        # Reload haproxy
        reloaded = HaproxyReloader.reload_haproxy(start_by=self.start_by,
                                                haproxy_config_file=self.haproxy_config_file,
                                                service_name=self.service_name,
                                                haproxy_binary=self.haproxy_binary,
                                                pid_file=self.pid_file,
                                                haproxy_socket_file=self.haproxy_socket_file,
                                                logger=self.logger
                                                )

        return reloaded

    def __update_haproxy_by_runtime(self):
        """ Method to update haproxy via runtime change over unix socket

            This method updates haproxy via runtime using runtimeupdater module.
            Once it is updated over the socket, the changes takes place almost instantly
            without any need to reload. Once updating is done, the config file is also
            updated so that the runtime config and the actual config on disk stays
            consistent. Like this, even if we have to restart haproxy for some reason,
            it will start back with its proper configuration and not stale configuration.

            Returns:
                bool : Successfully updated or not

        """

        if self.sa_mode == True:
            updated, stats = RuntimeUpdater.update_haproxy_runtime(node_ip=self.agent_ip,
                                                            agent_action=self.agent_action,
                                                            port=self.backend_port,
                                                            sock_file=self.haproxy_socket_file,
                                                            node_name=self.backend_name,
                                                            sa_mode=self.sa_mode,
                                                            logger=self.logger)
        else:
            updated, stats = RuntimeUpdater.update_haproxy_runtime(node_ips=self.node_list,
                                                            port=self.backend_port,
                                                            sock_file=self.haproxy_socket_file,
                                                            node_name=self.backend_name,
                                                            sa_mode=self.sa_mode,
                                                            logger=self.logger)

        if not updated:
            return False

        if self.sa_mode == True:
            status, nodes = RuntimeUpdater.get_haproxy_stats(sock_file=self.haproxy_socket_file,
                                                             backend_name=self.backend_name,
                                                             logger=self.logger
                                                            )
            if not status:
                return status

            node_ips = nodes.get("active_nodes").keys() + [self.agent_ip]
            inactive_nodes = len(nodes.get("inactive_nodes"))

            # Update the config after updating haproxy
            updated = ConfigHandler.update_config(haproxy_config_file=self.haproxy_config_file,
                                                template_file=self.template_file,
                                                node_list=node_ips,
                                                backend_maxconn=self.backend_maxconn,
                                                check_interval=self.check_interval,
                                                backend_port=self.backend_port,
                                                inactive_nodes_count=inactive_nodes,
                                                logger=self.logger)

        else:
            # Update the config after updating haproxy
            updated = ConfigHandler.update_config(haproxy_config_file=self.haproxy_config_file,
                                                template_file=self.template_file,
                                                node_list=self.node_list,
                                                backend_maxconn=self.backend_maxconn,
                                                check_interval=self.check_interval,
                                                backend_port=self.backend_port,
                                                inactive_nodes_count=stats.get("inactive_nodes_count"),
                                                logger=self.logger)

        if not updated:
            '''
                Log error, runtime updation succeeded but config file could not be updated
            '''

        return True

if __name__ == "__main__":
    hup = HaproxyUpdate(
        haproxy_config_file="/etc/haproxy/haproxy.cfg",
        template_file="/home/deep/elasticpyproxy/etc/haproxy.cofig.template",
        backend_port=6003,
        node_list=["10.42.0.197"],
        haproxy_binary="/usr/sbin/haproxy",
        start_by="binary",
        haproxy_socket_file="/var/run/haproxy/haproxy.sock",
        backend_name="haproxynode",
        service_name="haproxy",
        node_slots=6,
        pid_file="/run/haproxy.pid",
        update_type="update_by_config"
    )

    res = hup.update_haproxy()
    print (res)
