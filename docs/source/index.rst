.. ElasticPyProxy documentation master file, created by
   sphinx-quickstart on Sun Sep 22 00:06:26 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to ElasticPyProxy's documentation!
==========================================

ElasticPyProxy Code Documentation
******************************************
.. toctree::
   :maxdepth: 10
   :caption: Contents:

driver (Main entry point for ElasticPyProxy)
***********************************************
.. automodule:: src.driver.driver
    :members:

drivercache : Cache layer for EP2
***********************************************
.. automodule:: src.driver.drivercache
    :members:

bootstrap : Bootstrapper for ep2
***********************************************
.. automodule:: src.driver.bootstrap
    :members:

haproxyupdate : Module for updating haproxy
***********************************************
.. automodule:: src.core.haproxyupdater.haproxyupdate
    :members:

confighandler : Module for updating haproxy
***********************************************
.. automodule:: src.core.haproxyupdater.confighandler
    :members:

haproxyreloader : Module for reloading haproxy
***********************************************
.. automodule:: src.core.haproxyupdater.haproxyreloader
    :members:

runtimeupdater : Module for updating haproxy at runtime
***********************************************************
.. automodule:: src.core.haproxyupdater.runtimeupdater
    :members:

sockethandler : Module for handling socket operations
***********************************************************
.. automodule:: src.core.haproxyupdater.sockethandler
    :members:

basefetcher : Provides base class for backend fetchers
**********************************************************
.. automodule:: src.core.nodefetchers.basefetcher
    :members:

orchestrator : Module for providing appropriate backend fetcher
******************************************************************
.. automodule:: src.core.nodefetchers.orchestrator
    :members:

awsfetcher : Module for fecthing live backends from AWS
************************************************************
.. automodule:: src.core.nodefetchers.awsfetcher.awsfetcher
    :members:

botohandler : Module for handling AWS operations
************************************************************
.. automodule:: src.core.nodefetchers.awsfetcher.botohandler
    :members:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
