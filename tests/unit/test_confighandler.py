from src.core.haproxyupdater.confighandler import ConfigHandler
from .constants import SAMPLE_HAPROXY_CONFIG, SAMPLE_HAPROXY_TEMPLATE
import logging
import os

base_path = os.path.dirname(os.path.realpath(__file__))
haproxy_config_file_test = os.path.join(base_path, "haproxy.cfg.test")
haproxy_template_file_test = os.path.join(base_path, "haproxy.cfg.template.test")

class TestConfigHandler:
    def test_update_config(self):
        self.setup_env()
        base_path = os.path.dirname(os.path.realpath(__file__))

        udpated = ConfigHandler.update_config(haproxy_config_file=haproxy_config_file_test,
                                              template_file=haproxy_template_file_test,
                                              node_list=["1.1.1.1", "5.5.5.5"],
                                              backend_port=5555,
                                              inactive_nodes_count=4,
                                              logger=logging
                                            )

        assert udpated == True

        with open(haproxy_config_file_test) as f:
            cfg = f.read()

        assert "node5 1.1.1.1:5555 check" in cfg
        assert "node6 5.5.5.5:5555 check" in cfg
        assert "server-template node 4 10.0.0.1:8080 check disabled" in cfg

    def test_read_write_file(self):
        status, content = ConfigHandler.read_write_file(operation="write", file=haproxy_config_file_test, logger=logging, content=SAMPLE_HAPROXY_CONFIG)

        assert status == True
        assert content == None

        status, content = ConfigHandler.read_write_file(operation="read", file=haproxy_config_file_test, logging=logging)

        assert status == True
        assert "haproxynode" in content

        self.remove_file(haproxy_config_file_test)

    def setup_env(self):
        with open(haproxy_config_file_test, "w") as f:
            f.write(SAMPLE_HAPROXY_CONFIG)

        with open(haproxy_template_file_test, "w") as f:
            f.write(SAMPLE_HAPROXY_TEMPLATE)

    def remove_file(self, file_name):
        if os.path.exists(file_name):
            os.unlink(file_name)
