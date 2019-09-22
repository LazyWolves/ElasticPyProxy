"""
.. module:: botohandler
   :synopsis: Module for handling aws node fetching operations

"""

import boto3

class BotoHandler(object):
    """ Class for handling aws node fetching operations

        Methods in this class handle aws operations for retreiving the
        list of active backends. It first uses boto3 asg client for
        describing the asg of interest. Once we have the instance ids
        in that asg, we use ec2 client for describing those instances
        for getting their public/private ips

    """
    
    @staticmethod
    def get_auto_scaling_client(**kwargs):

        """ Method for initialising asg boto client

            Args:
                **kwargs (object) : kwargs must contains config dictionary, logger object.

            Returns:
                boto3.client : boto3 asg client
        """

        aws_access_key_id = kwargs.get("aws_access_key_id")
        aws_secret_access_key = kwargs.get("aws_secret_access_key")
        logger = kwargs.get("logger")
        region_name = kwargs.get("region_name")

        client = None

        try:
            client = boto3.client(
                "autoscaling",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        except Exception as ex:

            '''
                Log the exception
            '''
            logger.critical("Boto client creation failure for autoscaling with error : {}".format(str(ex)))

        return client

    @staticmethod
    def get_ec2_client(**kwargs):

        """ Method for initialising ec2 boto client

            Args:
                **kwargs (object) : kwargs must contains config dictionary, logger object.

            Returns:
                boto3.client : boto3 ec2 client
        """
        aws_access_key_id = kwargs.get("aws_access_key_id")
        aws_secret_access_key = kwargs.get("aws_secret_access_key")
        logger = kwargs.get("logger")
        region_name = kwargs.get("region_name")

        client = None

        try:
            client = boto3.client(
                "ec2",
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
            )
        except Exception as ex:

            '''
                Log the exception
            '''
            logger.critical("Boto client creation failure for autoscaling with error : {}".format(str(ex)))

        return client

    @staticmethod
    def get_instance_ips_for_asg(**kwargs):

        """ Method for getting aws live instance IPs

            Args:
                **kwargs (object) : kwargs must contains config dictionary, logger object.

            Returns:
                list : List of live backend IPs
        """
        asg_client = kwargs.get("asg_client")
        ec2_client = kwargs.get("ec2_client")
        asg_name = kwargs.get("asg_name")
        ip_type = kwargs.get("ip_type")
        logger = kwargs.get("logger")

        asg_instance_ids = BotoHandler.__get_instance_ids_for_asg(asg_client, asg_name, logger)
        if not asg_instance_ids:
            return None
        asg_instance_ips = BotoHandler.__get_instance_ips(ec2_client, asg_instance_ids, ip_type, logger)

        return asg_instance_ips

    @staticmethod
    def __get_instance_ids_for_asg(boto_client, asg_name, logger=None):

        """ Method for getting aws live instance ids belonging to the asg of interest

            Args:
                boto_client (boto3.client) : boto3 asg client
                asg_name (str) : name of the asg
                logger (object) : logger object

            Returns:
                list : List of live backend instance IDs
        """
        try:

            # Describe the esired asg
            response = boto_client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[
                    asg_name,
                ]
            )
        except Exception as ex:
            logger.critical("Failed to get instance ids for ASG with error : {}".format(str(ex)))
            return None

        instances = response.get("AutoScalingGroups")[0]["Instances"]

        instance_ids = []

        # Loop over the fetched instanced and extract their instance IDs
        for instance in instances:
            instance_ids.append(instance.get("InstanceId"))

        if len(instance_ids) == 0:
            return None

        return instance_ids

    @staticmethod
    def __get_instance_ips(boto_client, instance_ids, ip_type, logger=None):

        """ Method for getting aws live instance ips from instance IDs

            Args:
                boto_client (boto3.client) : boto3 ec2 client
                instance_ids (list) : List of instance IDs
                ip_type (str) : Type of ip wanted - public or private
                logger (object) : logger object

            Returns:
                list : List of live backend instance IPs
        """
        try:
            response = boto_client.describe_instances(
                InstanceIds=instance_ids
            )
        except Exception as ex:
            logger.critical("Failed to get instance ids for ASG with error : {}".format(str(ex)))
            return None

        if ip_type == "private":
            ip_key = "PrivateIpAddress"
        else:
            ip_key = "PublicIpAddress"

        instance_ips = []

        for reservation in response.get("Reservations"):
            for instance in reservation.get("Instances"):
                instance_ip = instance.get(ip_key)
                if instance_ip:
                    instance_ips.append(instance_ip)

        return instance_ips
