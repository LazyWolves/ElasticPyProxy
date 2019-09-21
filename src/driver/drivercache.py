"""
.. module:: drivercache
   :synopsis: caching layer for ep2

"""

class DriverCache(object):
    """Class to provide caching for ep2
 
    The backends fetched in a given run is stored in memory.
    The backends fetched in next run witll be compared to the ones already
    held by this class (node_ips). If there is a mismatch, only then update
    will be done

    Args:
        node_ips (list) : list of backend IPs

    """
    def __init__(self, node_ips):
        """Init method

        Method for initialising drivercache

        Args:
            node_ips (list) : list of backend IPs

        """

        self.node_ips = set()
        if node_ips:
            self.node_ips = node_ips

    def need_to_update(self, node_ips):
        """Method to check if haproxy needs to be updated

        Args:
            node_ips (list) : list of backend IPs

        Returns:
            bool: Whether to update haproxy or not

        """

        if node_ips == self.node_ips:
            return False

        if node_ips != self.node_ips:
            self.node_ips = node_ips
            return True
