import boto3

class BotoHandler(object):
    
    @staticmethod
    def get_auto_scaling_client(**kwargs):
        aws_access_key_id = kwargs.get("aws_access_key_id")
        aws_secret_access_key = kwargs.get("aws_secret_access_key")

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

        client = boto3.client(
            "ec2",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        return client

    @staticmethod
    def get_instance_ids_for_asg(boto_client, asg_name):
        response = boto_client.describe_auto_scaling_groups(
            AutoScalingGroupNames=[
                asg_name
            ]
        )

        instances = response.get("AutoScalingGroups")[0]["Instances"]

        instance_ids = []

        for instance in instances:
            instance_ids.append(instance.get("InstanceId"))
