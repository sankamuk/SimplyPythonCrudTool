
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

Download Application
+++++++++++++++++++++

Though this can be achieved in many way the simplest way is CLI using `GIT <https://git-scm.com/>`_. Below is the command for the same::

    $ git clone https://github.com/sankamuk/SimplyPythonCrudTool.git

.. note::  One can also simple download the application as a zip from GitHub repo.

Install Dependencies
+++++++++++++++++++++

With you in virtual environment, all you need to do for dependency installation is below::

    $ python -m pip install -r requirements.txt

.. note::  You should be inside the application folder with initiated virtual environment.

Execute Application
+++++++++++++++++++++

Now its time of run the application, and for that you do::

    $ python app.py

.. note::  Now your application will be available locally `AT <http://localhost:5000/>`_ . But before that you need to configure for any meaningful usage.


Though this could only be used for testing, nevertheless it is quick and easy method. Though our recommendation should be using Docker.





