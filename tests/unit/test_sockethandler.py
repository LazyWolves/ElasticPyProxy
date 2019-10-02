from src.core.haproxyupdater.sockethandler import SocketHandler
import logging

haproxy_sock_file = "/var/run/haproxy/haproxy.sock"
test_command = "show stat\n"

socket_handler = SocketHandler(logger=logging, sock_file=haproxy_sock_file)

class TestSockerHandler:
    def test_connect_socket(self):
        is_connected = socket_handler.connect_socket()

        assert is_connected == True

    def test_send_command(self):
        status, response = socket_handler.send_command(command=test_command)

        assert status == True
        assert response != None
        assert "qcur" in response
