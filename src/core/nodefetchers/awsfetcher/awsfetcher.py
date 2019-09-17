import os
import requests
from src.core.nodefetchers.basefetcher import BaseFetcher
from .botohandler import BotoHandler

class AwsFetcher(object):
    def __init__(self, **kwargs):
        self.aws_access_key_id = kwargs.get("aws_access_key_id")
        self.aws_secret_access_key = kwargs.get("aws_secret_access_key")
        self.asg_name = kwargs.get("asg_name")
        self.ip_type = kwargs.get("ip_type")
        logger = kwargs.get("logger")

        self.asg_boto_client = BotoHandler.get_auto_scaling_client(aws_access_key_id=self.aws_access_key_id,
                                                                   aws_secret_access_key=self.aws_secret_access_key
                                                                )
        self.ec2_boto_client = BotoHandler.get_ec2_client(aws_access_key_id=self.aws_access_key_id,
                                                          aws_secret_access_key=self.aws_secret_access_key
                                                        )

    def __check_response(self):
        return True

    def fetch(self):
        if self.asg_boto_client == None or self.ec2_boto_client == None:
            return None
        asg_instance_ips = BotoHandler.get_instance_ips_for_asg(asg_client=self.asg_boto_client,
                                                                ec2_client=self.ec2_boto_client,
                                                                asg_name=self.asg_name,
                                                                ip_type=self.ip_type
                                                            )

        return asg_instance_ips

if __name__ == "__main__":
    asgf = AwsFetcher(aws_access_key_id="",
                      aws_secret_access_key="",
                      asg_name="test-auto",
                      ip_type="public")

    ips = asgf.fetch()
    print (ips)
