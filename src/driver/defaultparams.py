default_params = {
    "haproxy_config_file" : "/etc/haproxy/haproxy.cfg",
    "template_file" : "/etc/ep2/ep2.template",
    "backend_port" : 6003,
    "haproxy_binary" : "/usr/sbin/haproxy",
    "start_by" : "binary",
    "haproxy_socket_file" : "/var/run/haproxy/haproxy.sock",
    "pid_file" : "/run/haproxy.pid",
    "backend_name" : "haproxynode",
    "update_type" : "update_by_runtime",
    "node_slots" : 50,
    "service_name" : "haproxy",
    "lock_dir" : "/run",
    "orchestrator" : "aws",
    "sleep_before_next_run" : 5,
    "sleep_before_next_lock_attempt" : 5,
    "log_file" : "/var/log/ep2/ep2.log"
}
