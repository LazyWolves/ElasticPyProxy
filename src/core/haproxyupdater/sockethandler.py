import socket

class SocketHandler(object):

    def __init__(self, **kwargs):

        # get the desired params
        self.sock_file = kwargs.get("sock_file")

    def create_socket(self):
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.settimeout(10)

        try:

            # try connecting to haproxy socket file
            self.socket.connect(self.sock_file)
        except Exception:

            '''
                Log exception
            '''

            return False

        return True
