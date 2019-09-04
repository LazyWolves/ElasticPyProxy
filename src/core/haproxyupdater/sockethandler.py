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
        except Exception as ex:

            '''
                Log exception
            '''

            return False

        return True

    def send_command(self, **kwargs):
        response = None
        command = kwargs.get("command")

        try:
            self.socket.send(command)
            response = ""

            while True:
                res_buf = self.socket.recv(16)
                if res_buf:
                    response += res_buf
                else:
                    break
        except Exception as ex:
            response = None

        if response == None:
            return False, response

        return True, response

    def destroy_socket(self):
        self.socket.close()
