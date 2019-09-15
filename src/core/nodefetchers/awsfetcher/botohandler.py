import boto3

class BotoHandler(object):
    
    @staticmethod
    def get_auto_scaling_client(**kwargs):
        aws_access_key_id = kwargs.get("aws_access_key_id")
        aws_secret_access_key = kwargs.get("aws_secret_access_key")
        logger = kwargs.get("logger")

        client = boto3.client(
            "autoscaling",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        return client

    @staticmethod
    def get_ec2_client(**kwargs):
        aws_access_key_id = kwargs.get("aws_access_key_id")
        aws_secret_access_key = kwargs.get("aws_secret_access_key")
        logger = kwargs.get("logger")

        client = boto3.client(
            "ec2",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        return client

    @staticmethod
    def get_instance_ips_for_asg(**kwargs):
        asg_client = kwargs.get("asg_client")
        ec2_client = kwargs.get("ec2_client")
        asg_name = kwargs.get("asg_name")
        ip_type = kwargs.get("ip_type")
        logger = kwargs.get("logger")

        asg_instance_ids = BotoHandler.__get_instance_ids_for_asg(asg_client, asg_name, logger)
        asg_instance_ips = BotoHandler.__get_instance_ips(ec2_client, asg_instance_ids, ip_type, logger)

        return asg_instance_ips

    @staticmethod
    def __get_instance_ids_for_asg(boto_client, asg_name, logger=None):
        response = boto_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                asg_name,
            ]
        )

        instances = response.get("AutoScalingGroups")[0]["Instances"]

        instance_ids = []

        for instance in instances:
            instance_ids.append(instance.get("InstanceId"))

        return instance_ids

    @staticmethod
    def __get_instance_ips(boto_client, instance_ids, ip_type, logger=None):
        response = boto_client.describe_instances(
            InstanceIds=instance_ids
        )

        instances = response.get("Reservations")[0].get("Instances")

        if ip_type == "private":
            ip_key = "PrivateIpAddress"
        else:
            ip_key = "PublicIpAddress"

        instance_ips = []

        for instance in instances:
            instance_ips.append(instance.get(ip_key))

        return instance_ips
