"""
.. module:: sockethandler
   :synopsis: Module for handling socket operation

"""

import socket

class SocketHandler(object):

    """ Class containing methods for handling socket operation

        This is a generic class for handling all socket operation.
        All the commands which are to be sent to haproxy and done via methods in
        this class.

        Args:
            **kwargs (dictionary) : Dictionary containing params
    """
    
    def __init__(self, **kwargs):

        """ Init method for the class

            Args:
                **kwargs (dictionary) : Dictionary containing params
        """

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

            '''
                Log exception
            '''
            self.logger.critical("Unable to connect to haproxy socket file. Encountered following exception : {}".format(str(ex)))

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

            '''
                Log error
            '''
            self.logger.critical("Issue in send/receive with haproxy socket. Encountered following exception : {}".format(str(ex)))
            response = None

        self.destroy_socket()

        if response == None:
            return False, response

        return True, response

    def destroy_socket(self):
        self.socket.close()
