# ElasticPyProxy : A controller for dynamic scaling of Haproxy backends

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
