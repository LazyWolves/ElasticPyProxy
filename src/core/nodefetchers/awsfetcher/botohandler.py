import boto3

class boto3(object):
    
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
