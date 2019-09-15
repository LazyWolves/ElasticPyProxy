class DriverCache(object):
    def __init__(self, node_ips):
        self.node_ips = set()
        if node_ips:
            self.node_ips = node_ips

    def need_to_update(self, node_ips):
        if node_ips == self.node_ips:
            return False

        if node_ips != self.node_ips:
            self.node_ips = node_ips
            return True
