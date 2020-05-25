# ElasticPyProxy : A controller for dynamic scaling of Haproxy backend servers

ElasticPyProxy (EP2) is a controller written completely in python for dynamically scaling HAProxy backend servers. Using this
controller, it is possible to integrate HAProxy with a server orchestrator which spwans servers dynamically and scales
out and in very frequently. As of now it provides support for the following:

- AWS Autoscaling groups
- Consul

however handler for any orchestrator which exposes an API for getting live backends can be added easily.

It is to be noted that **consul is not an orchestrator** but a service discovery tool. It can be used to discovery
A given service can be discovered with consul and later the hosts/nodes which are the provider of that service
can be discovered by either consul DNS or consul catalog API. If a node providing the given services goes down,
the api will remove those nodes from the catalogue and show only the live ones.

In the rest of the documentation we will continue refering to AWS ASG while explaining the differemt features
of EP2 but evrything will be applicable to Consul as well. 

So, going ahead with aws, it is possible, using EP2 to integrate HAProxy with a AWS Autoscaling Group. Once integrated, the
HAProxy backend servers will scale out and in with the ASG of interest. Thus, whenever the ASG spawns a new instance, that
instance will get added to haproxy's concerned backend/listener and when the ASG removes a backend, that particular server 
will also be removed from HAProxy's concerned backend/listener.

Know more about Hashicorp Consul `here <https://www.consul.io/>`_

In the rest of the documentation, for simplicity the term **orchestrator** will be used to refer to AWS ASG
and consul (although consul is not an orchestrator as already mentioned above but a service discovery mechanism,
any orchestrator can be exposed via consul, even AWS ASG) and the backend servers will be refered to as 
just **backends**

## How EP2 works

Simple put, EP2 continuously polls the orchestrator and checks what are the available backends and updates haproxy accordingly.
However it can be made to do this simple job in more than one way as needed by the user or the host system. Following are the
main tasks done by the components present in EP2

**EP2 working:**

- The system where EP2 runs should have the HAProxy (v1.8 or above) binary, HAproxy UNIX socket exposed and 
  accessible, optionally systemd service file properly configured.

- When EP2 starts, the first thing it does is bootstrap the controller. The bootstrapping includes creating clients
  for accessing the orchestrator, making the first call to orchestrator API for getting current live backends, updating
  the haproxy config file using the provided template.
 
- Once the config file has been updated, the bootstrapper checks if HAProxy is already running. If it is already running,
  the bootstrapper simply reloads HAProxy so that the new configuration takes affect. If Haproxy is stopped the it starts
  it.
  
- Once bootstrap is done, we now have a running haproxy with the current live backends added to it. Post this, EP2 enters
  its poll-update-repeat loop.
  
- Once EP2 enters the loop, it primarily does two things. Firstly it polls the orchestrator for the current backend nodes. On
  getting the list of current live backends it compares it against a locally saved in memory list of live backends.
  If there is a difference, it updates the local in-memory list and geoes on to update HAProxy otherwise it does nothing
  
- EP2 can update haproxy in two ways. First way is, it simply formats the configured haproxy template file with the live
  backend servers, updates the HAProxy config file with the contents of the formatted template file and reloads HAProxy.
  
- Since HAProxy reload (post v1.8) is hitless, reload wont cause any downtime.

- EP2 allows two ways to reload HAProxy, one via systemd service and the other via the HAProxy binary. The respective params
  must be provided in EP2 config accordingly. More on this below.
  
- The issue with the above method of updating is, HAProxy has to be reloaded. When the number of reloads is less, it is not
  a big issue. However if the number of reload is too high, it can cause overhead since reload essentially involves  transfer
  of connections/sockets from old process to the new process.
  
- The second method of updation is the one in which reload is not required at all. It updates HAProxy in runtime using the
  UNIX socket file it exposes. This is to some extent complicated than the previous method. Once the new backends are added
  the config file is also updated so that the runtime configuration and the config file on disk remains consistent, but there
  is no need to reload HAProxy.
  
- Once updation is done, it waits for a configured amount of time before polling for backends again and repeating the same
  processes.
  
  ### Major components of EP2
  
  - Backend fetcher : The backend fetcher fetches the live backends from the configured orchestrator. As mentioned earlier
    for now this is AWS.
    
  - HaproxyUpdater : This updates the HAProxy, either by updating config or via socket at runtime.
  
  - ConfigHandler : This is used by HaproxyUpdater to handle the HAProxy config updation
  
  - RuntimeUpdater : This is used by HaproxyUpdater to update HAProxy at runtime via socket.
  
  - HaproxyReloader : This is used to reload HAProxy wither via systemd or via binary.
  
  ### Backend fetcher
  
  The awsfetcher and the consulfetcher, fetches the available servers in the concerned asg or service respectively.
  For AWS ASG, boto3 library is used and for Consul, the Consul catalog API is used.
  
  ### Updating HAProxy via config
  
  As mentioned above, one of the ways HAProxy can be updated using EP2 is via updating its config direcly. In both the
  updation methods, EP2 is preconfigured with a template HAProxy config (mentioned below). 
  
  Once the current live backend servers are available, EP2 formats the template and populates it with the current live backends.
  Then it replaces the contents of the actually HAProxy config file with the contents of this formatted template file.
  After this is done it reloads HAProxy either via **systemd** or via **binary**.
  
  Both the path to Haproxy config file and path to the HAProxy template file should be provided in EP2 config.
  
  ### Updating HAProxy at Runtime
  
  In this method, HAProxy has to be preconfigured with a number of inactive or disabled backend servers. This is taken care of
  by the **bootstrapper**. When bootstrap runs, apart from creating the live backend servers it also creates a number of
  inactive dummy backend servers with dummy address.
  
  The number of dummy backend servers to be created is decided by the config param **node_slots**. If the number of live backend
  servers fetched from the orchestrator is **x**, then the number of dummy inactive servers created is **node_slots - x**.
  
  Now whenever a scale in activity happens, that is the orchestrator removes some of the live servers, EP2 finds out which
  servers are out of service. It marks them as inactive and adds them to the inactive pool.
  
  Whenever a new server is spawned up, EP2 picks an inactive server from the pool, changes its address to the address of the
  newly spawned backend server and marks it as ready. Thus the inactive server now becomes active and it represents the
  newly spawned backend server.
  
  Once the runtime config of HAProxy has been updated, same configuration is replicated in the config file so that it stays at
  par with the running config of HAProxy.
  
  It is worth noting that in this procedure, the value of the **node_slots** param should always be greater than the
  total amount of live servers the orchestrator can contain/spawn at any given time. This should be easily
  figured out from the **min/max** criteria of the orchestrator in use.
  
  ### Reloading HAProxy via systemd
  
  When updating HAProxy via config, HAProxy has to be reloaded and one such way to reload HAProxy is via **systemd**. For this
  there should be a properly configured systemd service file such that systemd reload works properly.
  
  The command used is the usual systemd command
  
  ```
  systemctl reoad [haproxy_servicefile_name]
  ```
  
  The HAProxy systemd service file name should be provided as a EP2 config param.
  
  ### Reloading HAProxy via binary
  
  The other way to reload haproxy is by executing the binary. For this is to work the following things must be provided in EP2
  config :
  
  - haproxy_config_file : The haproxy config file
  - haproxy_binary : The location of the HAProxy binary which is usually ``` /usr/sbin/haproxy```
  - haproxy_socket_file : The location of the HAProxy unix socket file.
  - pid_file : The location of the HAProxy PID file which is usually ```/run/haproxy.pid```
  
  The command fired is the usual one
  
  ```
     [haproxy_binary] -W -q -D -f [haproxy_config_file] -p [pid_file] -x [socket_file] -sf $(cat [pid_file])
  ```
  
  The above causes hitless reload of HAProxy.
  
  ### Bootstrapping EP2
  
  At the very beginning when EP2 is started, bootstrapping takes place. The following essentially happens in the bootstrap
  process :
  
  - The desired nodefetcher is initialised. As of now it is the **awsfetcher**. As a part of the initialisation of the
    awsfetcher, the asg and ec2 boto3 clients are created using the provided aws credentials.
    
  - The the very first call to get the live backend servers is made.
  
  - Once EP2 has the live backend server addresses, irrespective of whether EP2 is configured to use update via config or
    update at runtime, EP2 updates the haproxy config with the formatted template file contents. It is during this time
    EP2 creates the inactive pool if it is configured to use updae by runtime on later runs.
   
  - Once the updation is done, it checks whether HAProxy is running or not. If its not running, the it starts HAProxy.
    If it was running then it simply reloads it using the configured method.
    
  - Once bootstrap is done, EP2 enters its loop.
  
  ## Installing EP2
  
  EP2 can be installed either using pip or can be built from source.
  
  **Installing via pip**
  
  Inorder to install via pip, execute the following
  
  ```
  sudo pip3 install git+git://github.com/djmgit/ElasticPyProxy
  
  ```
  
  **Installing from source**
  
  Inorder to install from source perform the following actions:
  
  -  Clone this repo and enter into it using ``` git clone https://github.com/djmgit/ElasticPyProxy.git ```
  -  Run the following command ``` sudo python3 setup.py install ```
  
  Once installation is done, ep2 will be installed at **/usr/bin/ep2**
  
  Also the following files and directories will be created:
  
  - /var/log/ep2
  - /etc/ep2
  - /etc/ep2/ep2.conf
  - /etc/ep2/haproxy.cfg.template

## Configuring EP2

A sample EP2 config file is given below:

```
  [haproxy]
  haproxy_config_file = /etc/haproxy/haproxy.cfg
  template_file = /home/deep/elasticpyproxy/etc/haproxy.config.template
  backend_port = 6003
  haproxy_binary = /usr/sbin/haproxy
  start_by = systemd
  haproxy_socket_file = /var/run/haproxy/haproxy.sock
  pid_file = /run/haproxy.pid
  backend_name = haproxynode
  update_type = update_by_runtime
  node_slots = 5
  service_name = haproxy
  lock_dir = /home/deep/elasticpyproxy/etc
  orchestrator = aws
  sleep_before_next_run = 5
  log_file = /var/log/ep2/ep2.log
  
  [AWS]
  aws_access_key_id =
  aws_secret_access_key =
  asg_name =
  region_name =
```
For Consul, the following block can be used instead of [AWS]

```
  [CONSUL]
  service_name =
  consul_ip =
  consul_port =
  only_passing =
  tags =
```

Params involved:

- haproxy_config_file : This is the path to the actual haproxy config file. Usually it is /etc/haproxy/haproxy.cfg
- template_file : Path to the template file. This is the file that will be populated and used to update the actual
                  haproxy config file.
- backend_port : The port used by backend servers.
- haproxy_binary : The HAProxy binary file location.
- start_by : How to start/reload HAProxy. Can be **systemd** or **binary**
- haproxy_socket_file : Path to HAProxy socket file. If Haproxy has been configure to spawn multiple process via nbproc, then paths to multiple socket files can be provided here separated by comma
- pid_file : Path to HAProxy pid file
- backend_name : The name of the HAProxy backend/listener name under which the live backend servers fetched from orchestrator will be added.
- backend_maxconn : Max connections for individual backends
- check_interval : Interval for performing health checks for individual backends
- update_type : How to update HAProxy. Either **update_by_config** or **udpate_by_runtime**
- node_slots : Total number of slots for backend servers. As mentioned above, this will be used to calculate inactive servers.
- service_name : Service name for HAProxy systemd service. Required only when using reload by systemd
- lock_dir : Path to directory for storing EP2 lock file.
- orchestrator : The backend orchestrator. As of now it can only be **aws**
- sleep_before_next_run : Amount of time to wait before next poll-update run
- log_file : The file to output logs

[AWS]

- aws_access_key_id : aws creds
- aws_secret_access_key : aws creds
- asg_name : Name of the autoscaling group
- region_name : aws region name where the asg exists

[CONSUL]

- service_name : Name of the service which has already been registered with consul and whose providers we want to discover
- consul_ip : IP adress where consul catalog API is running. Default is 127.0.0.1. If the node where EP2 is running has been added the the consul cluster, then consul api should be accessed via 127.0.0.1 if not changed otherwise.

- consul_port : Port for the Consul catalog API. Default is 8500
- only_passing : can be **True** or **False**. If True, then only those backends will be discovered and added for which the service checks are passing. Please refer Consul doc to learn more about service checks. Default value is True.
- tags : Comma separated values of tags to filter services.


A sample haproxy template file is shown below

```
global
	log /dev/log	local0
	log /dev/log	local1 notice
	chroot /var/lib/haproxy
	stats socket /var/run/haproxy/haproxy.sock mode 660 level admin expose-fd listeners
	stats timeout 30s
	user haproxy
	group haproxy
	daemon

	# Default SSL material locations
	ca-base /etc/ssl/certs
	crt-base /etc/ssl/private

	# Default ciphers to use on SSL-enabled listening sockets.
	# For more information, see ciphers(1SSL). This list is from:
	#  https://hynek.me/articles/hardening-your-web-servers-ssl-ciphers/
	# An alternative list with additional directives can be obtained from
	#  https://mozilla.github.io/server-side-tls/ssl-config-generator/?server=haproxy
	ssl-default-bind-ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:RSA+AESGCM:RSA+AES:!aNULL:!MD5:!DSS
	ssl-default-bind-options no-sslv3
	stats socket ipv4@127.0.0.1:9999 level admin
  stats timeout 2m

defaults
	log	global
	mode	http
	option	httplog
	option	dontlognull
  	timeout connect 5000
  	timeout client  50000
  	timeout server  50000
	errorfile 400 /etc/haproxy/errors/400.http
	errorfile 403 /etc/haproxy/errors/403.http
	errorfile 408 /etc/haproxy/errors/408.http
	errorfile 500 /etc/haproxy/errors/500.http
	errorfile 502 /etc/haproxy/errors/502.http
	errorfile 503 /etc/haproxy/errors/503.http
	errorfile 504 /etc/haproxy/errors/504.http

listen haproxynode
	bind *:7001
	balance roundrobin
	option forwardfor
	http-request set-header X-Forwarded-Port %[dst_port]
	http-request set-header X-CLIENT-IP %[src]
	http-request add-header X-Forwarded-Proto https if {{ ssl_fc }}
	option httpchk HEAD / HTTP/1.1\r\nHost:localhost
	{{nodes}}

listen stats
    bind :32700
    stats enable
    stats uri /stat
    stats hide-version

```

The backend/listener used (```haproxynode```) in this case should be mentiond in **EP2 config**.
The backend/listener of interest should have the template varibale ``nodes`` in jinja templating format.
This template varibale will be replaced with the live backend servers in each run.

Once this template is formatted, the actual HAProxy config will be updated with the formatted contents of this
template file.

So, whatever changes one usually has to make to HAProxy config, they have to be made here.

## Starting EP2

Execute the following for starting EP2:

```
  sudo ep2 -f [Path to ep2.conf]
```

Stop EP2 by CTRL+C.

The ideal way to run EP2 would be to use a process manager like **systemd** or **supervisord**.



  
  

