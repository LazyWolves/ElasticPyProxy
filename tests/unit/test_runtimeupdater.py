import os
import logging
from src.core.haproxyupdater.runtimeupdater import RuntimeUpdater
from src.core.haproxyupdater.sockethandler import SocketHandler

haproxy_sock = "/var/run/haproxy/haproxy.sock"
backend_name = "haproxynode"

class TestRuntimeUpdater:
    pass

