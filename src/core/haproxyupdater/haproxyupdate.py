import os
from .confighandler import ConfigHandler
from .runtimeupdater import RuntimeUpdater
from .haproxyreloader import HaproxyReloader

class HaproxyUpdate(object):
    def __init__(self, **kwargs):

        '''
            Get desired params
        '''
        self.haproxy_config_file = kwargs.get("haproxy_config_file")
        self.template_file = kwargs.get("template_file")
        self.backend_port = kwargs.get("backend_port")
        self.node_list = kwargs.get("node_list")
        self.haproxy_binary = kwargs.get("haproxy_binary")
        self.init_file = kwargs.get("init_file")
        self.start_by = kwargs.get("start_by")
        self.haproxy_socket_file = kwargs.get("haproxy_socket_file")
        self.backend_name = kwargs.get("backend_name")
        self.update_type = kwargs.get("update_type")
        self.node_slots = kwargs.get("node_slots")
        self.service_name = kwargs.get("service_name")

        self.valid_start_by = [
            "binary",
            "systemd",
            "init"
        ]

        self.valid_update_types = [
            "update_by_config",
            "update_by_runtime"
        ]

    def __sanitise(self):

        '''
            Validate all the paths
        '''
        if not os.path.isfile(self.haproxy_config_file):
            return False

        if not os.path.isfile(self.template_file):
            return False

        if self.backend_port < 0 or self.backend_port > 65536:
            return False

        if self.haproxy_binary and not os.path.isfile(self.haproxy_binary):
            return False

        if self.init_file and not os.path.isfile(self.init_file):
            return False

        if self.haproxy_socket_file and not os.path.isfile(self.haproxy_socket_file):
            return False

        if not self.backend_name:
            return False

        if self.node_slots and self.node_slots <= 0:
            return False

    def update_haproxy(self):
        if not self.__sanitise():
            return False

        updated = ConfigHandler.update_config(haproxy_config_file=self.haproxy_config_file,
                                        template_file=self.template_file,
                                        node_list=self.node_list,
                                        backend_port=self.backend_port
                                        )

        reloaded = HaproxyReloader.reload_haproxy(start_by=self.start_by)

        return reloaded

    def __update_haproxy_by_runtime(self):
        updated, stats = RuntimeUpdater.update_haproxy_runtime(node_ips=self.node_list,
                                                        port=self.backend_port,
                                                        sock_file=self.haproxy_socket_file,
                                                        node_name=self.backend_name)

        if not updated:
            return False

        updated = ConfigHandler.update_config(haproxy_config_file=self.haproxy_config_file,
                                            template_file=self.template_file,
                                            node_list=self.node_list,
                                            backend_port=self.backend_port,
                                            inactive_nodes_count=stats.get("inactive_nodes_count"))

        if not updated:
            '''
                Log error, runtime updation succeeded but config file could not be updated
            '''

        return True
