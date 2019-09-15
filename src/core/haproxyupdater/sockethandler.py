import socket

class SocketHandler(object):

    def __init__(self, **kwargs):

        # get the desired params
        self.sock_file = kwargs.get("sock_file")
        self.logger = kwargs.get("logger")

    def connect_socket(self):
        try:

            # try connecting to haproxy socket file
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect(self.sock_file)
        except Exception as ex:
            print (ex)
            '''
                Log exception
            '''

            return False

        return True

    def send_command(self, **kwargs):
        response = None
        command = kwargs.get("command").encode()

        connected = self.connect_socket()

        if not connected:
            return False, None

        try:
            # send command
            self.socket.send(command)
            response = ""

            while True:
                res_buf = self.socket.recv(16)
                if res_buf:
                    response += res_buf.decode()
                else:
                    break
        except Exception as ex:
            print (ex)
            response = None

        self.destroy_socket()

        if response == None:
            return False, response

        return True, response

    def destroy_socket(self):
        self.socket.close()
