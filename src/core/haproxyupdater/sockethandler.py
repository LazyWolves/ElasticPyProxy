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
        self.sock_files = kwargs.get("sock_file").split(",")
        self.sock_files = [sock_file.strip() for sock_file in self.sock_files]
        self.logger = kwargs.get("logger")

    def connect_socket(self, sock_file):

        """ Method to connect to haproxy unix socket

            This method creates a socket connection to the given haproxy unix socket

            Returns:
                bool : Successfully created socket connection or not
        """
        try:

            # try connecting to haproxy socket file
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect(sock_file)
        except Exception as ex:

            '''
                Log exception
            '''
            self.logger.critical("Unable to connect to haproxy socket file. Encountered following exception : {}".format(str(ex)))

            return False

        return True

    def send_command(self, **kwargs):

        """ Method to send command to haproxy unix socket and get response

            It will first create a socket connection to the haproxy socket
            and then send the given command and get response.

            Args:
                **kwargs (dictionary) : Dictionary containing params

            Returns:
                bool : Successfully sent command or not
                str : response sent by the haproxy unix socket
        """
        response = None
        command = kwargs.get("command").encode()
        command_type = kwargs.get("command_type", "GET")

        if command_type == "GET":
            return self.send_one(self.sock_files[0], command)
        else:
            return self.send_all(command)

    def destroy_socket(self):
        self.socket.close()

    def send_one(self, sock_file, command):
        # connect to the haproxy socket
        connected = self.connect_socket(sock_file)

        if not connected:
            return False, None

        try:
            # send command
            self.socket.send(command)
            response = ""

            # Get the entire respnse in chunks of 16 bytes
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

    def send_all(self, command):

        final_status = True

        for sock_file in self.sock_files:
            status, response = self.send_one(sock_file, command)

            if not status:
                final_status = False

        return final_status, response
