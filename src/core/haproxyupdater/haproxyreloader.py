import os
import subprocess

class HaproxyReloader(object):

    @staticmethod
    def reload_haproxy(**kwargs):
        start_by = kwargs.get("start_by")

        if start_by == "systemd":
            service_name = kwargs.get("service_name")

            reloaded = HaproxyReloader.__reload_by_systemd(service_name)

            return reloaded

        elif start_by == "binary":
            binary = kwargs.get("haproxy_binary")
            haproxy_config_file = kwargs.get("haproxy_config_file")

            reloaded = HaproxyReloader.__reload_by_binary(binary, haproxy_config_file)

            return reloaded

    @staticmethod
    def __reload_by_systemd(service_name):
        pass

    @staticmethod
    def __reload_by_binary(service_name, haproxy_config_file):
        pass

    @staticmethod
    def __execute_shell(command):

        proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        output, errors = proc.communicate()
        proc_exit_code = proc.returncode

        if proc_exit_code != 0:

            '''
                Log the error and the exit code
            '''

            return False

        return True
