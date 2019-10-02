from src.core.haproxyupdater.confighandler import ConfigHandler
from .constants import SAMPLE_HAPROXY_CONFIG, SAMPLE_HAPROXY_TEMPLATE
import logging
import os

class TestConfigHandler:
    def test_update_config(self):
        pass

    def test_read_write_file(self):
        file = "haproxy.cfg.test"

        status, content = ConfigHandler.read_write_file(operation="write", file=file, logger=logging, content=SAMPLE_HAPROXY_CONFIG)

        assert status == True
        assert content == None

        status, content = ConfigHandler.read_write_file(operation="read", file=file, logging=logging)

        assert status == True
        assert "haproxynode" in content

        self.remove_file(file)

    def remove_file(self, file_name):
        base_path = os.path.dirname(os.path.realpath(__file__))
        if os.path.exists(os.path.join(base_path, file_name)):
            os.unlink(os.path.join(base_path, file_name))
