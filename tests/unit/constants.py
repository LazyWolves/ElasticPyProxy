SAMPLE_HAPROXY_CONFIG = """
listen haproxynode
	bind *:7001
	balance roundrobin
	option forwardfor
	http-request set-header X-Forwarded-Port %[dst_port]
	http-request set-header X-CLIENT-IP %[src]
	http-request add-header X-Forwarded-Proto https if { ssl_fc }
	option httpchk HEAD / HTTP/1.1\r\nHost:localhost
	    server node5 3.81.160.200:6003 check
        server-template node 4 10.0.0.1:8080 check disabled
"""

SAMPLE_HAPROXY_TEMPLATE = """
listen haproxynode
	bind *:7001
	balance roundrobin
	option forwardfor
	http-request set-header X-Forwarded-Port %[dst_port]
	http-request set-header X-CLIENT-IP %[src]
	http-request add-header X-Forwarded-Proto https if { ssl_fc }
	option httpchk HEAD / HTTP/1.1\r\nHost:localhost
	{{nodes}}
"""
