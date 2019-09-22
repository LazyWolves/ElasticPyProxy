# ElasticPyProxy : A controller for dynamic scaling of Haproxy backend servers

ElasticPyProxy (EP2) is a controller written completely in python for dynamically scaling HAProxy backend servers. Using this
controller, it is possible to integrate HAProxy with a server orchestrator which spwans servers dynamically and scales
out and in very frequently. As of now it provides support for **only for AWS** however handler for any orchestrator which
exposes an API for getting live backends can be added easily.

So, going ahead with aws, it is possible, using EP2 to integrate HAProxy with a AWS Autoscaling Group. Once integrated, the
HAProxy backend servers will scale out and in with the ASG of interest. Thus, whenever the ASG spawns a new instance, that
instance will get added to haproxy's concerned backend/listener and when the ASG removes a backend, that particular server 
will also be removed from HAProxy's concerned backend/listener.

In the rest of the documentation, Amazon Autoscaling Group will be refered to as the **orchestrator** and the backend servers will
be refered to as just **backends**

## How EP2 works

Simple put, continuously polls the orchestrator and checks what are the available backends and updates haproxy accordingly.
However it can be made to do this simple job in more than one way as needed by the user or the host system. Following are the
main tasks done by the components present in EP2

**EP2 working:**

- The system where EP2 runs should have the HAProxy (v1.8 and above) binary, HAproxy UNIX socket exposed and 
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
  getting the list of current live backends it compares it againts a locally saved in memory list of live backends.
  If there is a diiference, it updates the local in-memory list and geoes on to update HAProxy otherwise it does nothing
  
- EP2 can update haproxy in two ways. First way is, it simply formats the configures haproxy template file with the live
  backend servers, updates the HAProxy config file with the contents of the formatted template file and reloads HAProxy.
  
- Since HAProxy reload (post v1.8) is hitless, reload wont cause any downtime.

- EP2 allows two ways to reload HAProxy, one via systemd service and the other via the HAProxy binary. The respective params
  must be provided in EP2 config accordingly. More on this below.
  
- The issue with the above method of updating is, HAProxy has to be reloaded. When the number of reloads is less, it is not
  a big issue. Howver if the number of reload is too high, it can cause overhead since reload essentially involves  transfer
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
  
  ### AWS ASG Backend fetcher
  
  The **aws asg backend fectcher** or the awsfetcher in short, fetches the available servers in the concerned asg using
  the boto3 python libaray.
  
  It uses the boto3 asg client to get the instance IDs of the available instances in the desired asg and then uses
  boto3 ec2 client to get the public/private IPs of the available instances.
  
  ### Updating HAProxy via config
  
  As mentioned above, one of the ways HAProxy can be updated using EP2 is via updating its config direcly. In both the
  updation methods, EP2 is preconfigured with a template HAProxy config (mentioned below). 
  
  Once the current live backend servers are available, EP2 formats the template and populates it with the current live backends.
  Then it replaces the contents of the actually HAProxy config file with the contents if this formatted template file.
  After this is done it reloads HAProxy either via **systemd** or via **binary**.
  
  Both the path to Haproxy config file and path to the HAProxy template file should be provided in EP2 config.

