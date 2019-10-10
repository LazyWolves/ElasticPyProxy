import logging
from src.core.haproxyupdater.haproxyreloader import HaproxyReloader

service_name = "haproxy"
haproxy_binary = "/usr/sbin/haproxy"
haproxy_config_file = "/etc/haproxy/haproxy.cfg"
haproxy_socket_file = "/var/run/haproxy/haproxy.sock"
pid_file = "/run/haproxy.pid"

class TestHaproxyReloader:
    
    def test_reload_haproxy_by_systemd(self):

        start_by = "systemd"
        reloaded = HaproxyReloader.reload_haproxy(start_by=start_by, logger=logging, service_name=service_name)

        assert reloaded == True

    def test_reload_haproxy_by_binary(self):

        start_by = "binary"
        reloaded = HaproxyReloader.reload_haproxy(start_by="binary",
                                                  haproxy_binary=haproxy_binary,
                                                  haproxy_config_file=haproxy_config_file,
                                                  haproxy_socket_file=haproxy_socket_file,
                                                  pid_file=pid_file,
                                                  logger=logging
                                                )

        assert reloaded == True
        