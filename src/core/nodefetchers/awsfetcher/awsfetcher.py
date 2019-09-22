"""
.. module:: awsfetcher
   :synopsis: Module for fetching backends from AWS

"""

import os
import requests
from src.core.nodefetchers.basefetcher import BaseFetcher
from .botohandler import BotoHandler

class AwsFetcher(object):

    """ Class for fetching libe backends from AWS

        Contains methods to fetch live backends from AWS using the boto3 library
        To make this class work properly, ep2 config must have aws section with
        access_key_id and secret_access_token specified along with aws region
        and ip_type which is required (public or private)

        Args:
            **kwargs (dictionary) : Dictionary containing params
    """
    def __init__(self, **kwargs):

        """ Init method for this class

            Apart from initialising the aws creds it also creates instances
            of boto3 clients for asg and ec2
        """

        self.aws_access_key_id = kwargs.get("aws_access_key_id")
        self.aws_secret_access_key = kwargs.get("aws_secret_access_key")
        self.asg_name = kwargs.get("asg_name")
        self.ip_type = kwargs.get("ip_type")
        self.region_name = kwargs.get("region_name")
        self.logger = kwargs.get("logger")

        # Initialise boto3 client for asg
        self.asg_boto_client = BotoHandler.get_auto_scaling_client(aws_access_key_id=self.aws_access_key_id,
                                                                   aws_secret_access_key=self.aws_secret_access_key,
                                                                   region_name=self.region_name,
                                                                   logger=self.logger
                                                                )

        # Initialise boto3 client for ec2
        self.ec2_boto_client = BotoHandler.get_ec2_client(aws_access_key_id=self.aws_access_key_id,
                                                          aws_secret_access_key=self.aws_secret_access_key,
                                                          region_name=self.region_name,
                                                          logger=self.logger
                                                        )

    def __check_response(self):
        return True

    def fetch(self):
        """ Method for fetching backends

            This method takes help of BotoHandler for fetching backends from AWS
            and return them to the caller

            Returns:
                list : List of backends
        """

        if self.asg_boto_client == None or self.ec2_boto_client == None:
            return None

        # get backends from AWS
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
