'''
    Base fetcher for all the fetcher classes
'''

class BaseFetcher(object):
    def __init__(self, **kwargs):
        self.response = kwargs.get("response")

    def __check_response(self):

        '''
            Check if we got a response successfully. Should be overridden by individual fetchers
        '''
        return True

    def fetch(self):

        '''
            Make request for nodes. Should be overridden by individual fetchers
        '''
        pass
