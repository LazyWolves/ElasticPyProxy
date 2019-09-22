"""
.. module:: basefectcher
   :synopsis: Base class for all kinds of backend fetchers

"""

class BaseFetcher(object):

    """ Base class for all kinds of backend fetchers

        This class is the base/super class for all backend fetchers.
        Individual backend fetchers have to inherit this class and
        an optionally override the methods present in this class

        Args:
            **kwargs (dictionary) : Dictionary containing params
    """
    def __init__(self, **kwargs):

        """ Init method for BaseFetcher

            Args:
                **kwargs (dictionary) : Dictionary containing params
        """
        self.response = kwargs.get("response")

    def __check_response(self):

        """ Method to check validity of the received response

            Check if we got a response successfully. Should be overridden by individual fetchers

            Returns:
                bool : Whether response is valid or not
        """
        return True

    def fetch(self):

        """ Method for fecthing backend nodes from orchestrator

            Make request for nodes. Should be overridden by individual fetchers
        """
        pass
