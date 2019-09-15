import os
import subprocess

class HaproxyReloader(object):

    @staticmethod
    def reload_haproxy(**kwargs):
        start_by = kwargs.get("start_by")
        logger = kwargs.get("logger")

        if start_by == "systemd":
            service_name = kwargs.get("service_name")

            reloaded = HaproxyReloader.__systemd_handler(service_name, "reload", logger)

            return reloaded

        elif start_by == "binary":
            binary = kwargs.get("haproxy_binary")
            haproxy_config_file = kwargs.get("haproxy_config_file")
            sock_file = kwargs.get("sock_file")
            pid_file = kwargs.get("pid_file")

            reloaded = HaproxyReloader.__reload_by_binary(binary, haproxy_config_file, sock_file, pid_file, logger)

            return reloaded

    @staticmethod
    def start_by_systemd(service_name, logger=None):
        logger.info("Starting haproxy via systemd")
        started = HaproxyReloader.__systemd_handler(service_name, "start", logger)

        return started

    @staticmethod
    def __systemd_handler(service_name, operation, logger=None):
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

        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, errors = proc.communicate()
        proc_exit_code = proc.returncode

        logger.info("Executing command : {command}".format(command=command))

        if proc_exit_code != 0:

            '''
                Log the error and the exit code
            '''

            logger.critical("Encountered following errors with command : {command} : {errors}".format(command=command, errors=errors))
            return False

        return True
