import socket

class SocketHandler(object):

    def __init__(self, **kwargs):

        # get the desired params
        self.sock_file = kwargs.get("sock_file")
