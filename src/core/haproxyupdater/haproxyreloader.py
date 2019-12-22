"""
.. module:: haproxyreloader
   :synopsis: Module for reloader haproxy

"""

import os
import subprocess

class HaproxyReloader(object):

    """ Class for handling haproxy reload

        This class provides methods to reload haproxy, either
        via systemd or via the binary.

        In order to reload via bianry, the socket file and the PID file
        should be present as params along with the binary location.

        For systemd, the systemd service name should be provided
        as param.

        Both reload via systemd and reload via binary are done by execting shell
        commands via subprocess library
    """

    @staticmethod
    def reload_haproxy(**kwargs):

        """ Method for reloading haproxy

            Method for reloading haproxy. This takes the help of util method to reload
            haproxy either via systemd or binary.

            Other classes and methods will call this method for updating haporoxy
            with the required param.

            Args:
                **kwargs (dictionary) : Dictionary conatining params

            Returns:
                bool : Successfully reloaded or not
        """
        start_by = kwargs.get("start_by")
        logger = kwargs.get("logger")

        if start_by == "systemd":
            service_name = kwargs.get("service_name")

            reloaded = HaproxyReloader.__systemd_handler(service_name, "reload", logger)

            return reloaded

        elif start_by == "binary":

            # get the required params for bianry reload
            binary = kwargs.get("haproxy_binary")
            haproxy_config_file = kwargs.get("haproxy_config_file")

            # it is assumed that the socket referd to by the first file has got expose-fd listeners
            # this socket will be used for socket transfer between processes and for HAProxy reload.
            sock_file = kwargs.get("haproxy_socket_file").split(",")[0].strip()
            pid_file = kwargs.get("pid_file")

            reloaded = HaproxyReloader.__reload_by_binary(binary, haproxy_config_file, sock_file, pid_file, logger)

            return reloaded

    @staticmethod
    def start_by_systemd(service_name, logger=None):

        """ Method for starting haproxy via systemd

            Starts haproxy via systemd. Executes systemd start as a shell command.

            Args:
                logger (object) : logger object for logging
            
            Returns:
                bool : Successfully started or not
        """
        logger.info("Starting haproxy via systemd")
        started = HaproxyReloader.__systemd_handler(service_name, "start", logger)

        return started

    @staticmethod
    def __systemd_handler(service_name, operation, logger=None):

        """ Systemd handler for executing systemd shell commands

            Creates the command string and calls __execute_shell method to execute it

            Args:
                service_name (string) : name of the haproxy service
                operation (string) : name of the operation. For eg: start, reload, stop.
                logger (object) : logger object 
                
            Returns:
                bool : Successfully executed or not
        """

        logger.info("Reloading haproxy via systemd")
        command = "systemctl {operation} {service_name}".format(service_name=service_name, operation=operation)

        executed = HaproxyReloader.__execute_shell(command, logger)

        '''
            If any error has occurred, then it has already been logged.
            Return status
        '''

        return executed

    @staticmethod
    def __reload_by_binary(binary, haproxy_config_file, sock_file, pid_file, logger=None):

        """ Method for reloading haproxy via binary

            Reloads haproxy via binary. Creates the command string for reloading haproxy
            and then sends it to __execute_shell command.

            Args:
                binary (str) : Path to haporoxy binary
                haproxy_config_file (str) : Path to haproxy config file
                sock_file (str) : Path to haproxy socket file
                logger (object) : Logger object

            Returns:
                Successfully reloaded or not
        """

        logger.info("Reloading haproxy via binary")
        command_template = "{binary} -W -q -D -f {haproxy_config_file} -p {pid_file} -x {sock_file} -sf $(cat {pid_file})"

        command = command_template.format(binary=binary,
                                        haproxy_config_file=haproxy_config_file,
                                        pid_file=pid_file,
                                        sock_file=sock_file)

        executed = HaproxyReloader.__execute_shell(command, logger)

        '''
            If any error has occurred, then it has already been logged.
            Return status
        '''

        return executed

    @staticmethod
    def __execute_shell(command, logger=None):

        """Method for executing shell commands

            Args:
                command (str) : Command needed to executed
                logger (object) : Logger object

            Returns:
                bool : Successfully executed or not
        """

        # Execute shell command via subprocess
        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Extract both output and error
        output, errors = proc.communicate()

        # get return code
        proc_exit_code = proc.returncode

        logger.info("Executing command : {command}".format(command=command))

        if proc_exit_code != 0:

            '''
                Log the error and the exit code
            '''

            logger.critical("Encountered following errors with command : {command} : {errors}".format(command=command, errors=errors))
            return False

        return True
