
Installation
==============

This is a Python Flask based Web application thus you have different options to host this. Below we discuss possible options:

* [TESTING] Local execution
* `Docker <docker_installation.html>`_
* `Custom <custom_installation.html>`_

Below we only discuss the quick start local execution option.


Step by Step Guide to Local Installation
----------------------------------------

Install Python
+++++++++++++++++

Depends on your OS build all detail can be found in `GUIDE <https://wiki.python.org/moin/BeginnersGuide/Download>`_

.. note::  This application is build with **Python version 3**.

Setup a Virtual Environment
+++++++++++++++++++++++++++

Though its not mandatory to use virtual environment but its always advisable, find the `GUIDE <https://docs.python.org/3/library/venv.html>`_

.. note::  Before you proceed, do not forget to initiate your **virtual environment** .

Example::

    > python -m venv venv
    > venv\Scripts\activate.bat


Download Application
+++++++++++++++++++++

.. note::  Before we proceed you should have created and initiated your virtual environment.

Just install the application from pip repo. Below is the command for the same::

    > pip install simple-python-crud-tool

.. note::  Once install you should have your start script available in CMD ``sct-run``.

Setup Environment
+++++++++++++++++++++

As already discussed in `CONFIGURATION <configuration.html>`_ this application is dependent on environment,
thus all you need to do before starting up us to set environment as below::

    > SET SCT_DB_NAME=******
    > SET SCT_DB_USER=******
    > SET SCT_DB_PWD=******
    > SET SCT_DB_HOST=******
    > SET SCT_AUTH_OKTA_DOMAIN=******
    > SET SCT_AUTH_OKTA_CLIENT_ID=******
    > SET SCT_AUTH_OKTA_CLIENT_SECRET=******

.. note::  Above configuration is not exhaustive rather just representative.

Execute Application
+++++++++++++++++++++

Now its time of run the application, and for that you do::

    > sct-run

.. note::  Now your application will be available locally `AT <http://localhost:5000/>`_


.. warning::  Our recommendation usage is Docker.





