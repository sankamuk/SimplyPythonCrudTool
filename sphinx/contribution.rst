Contribution
==============

Below is the process for contribution setup.

Get Application
~~~~~~~~~~~~~~~~~~~

Command::

    > git clone https://github.com/sankamuk/SimplyPythonCrudTool.git

.. note::  Of course you need local `GIT <https://git-scm.com/>`_ installation before you proceed.


Build Documentation
~~~~~~~~~~~~~~~~~~~

Command::

    > sphinx-apidoc -f -o . ../app
    > sphinx-build -b html . ../docs

.. note::  You should be in ``sphinx`` directory before triggering the build.

Build Package
~~~~~~~~~~~~~~~~~~~

Command::

    > python -m build --sdist

.. note::  You should be in project home before triggering the build.


Guidelines
~~~~~~~~~~~~~~~~~~~

[***TO DO***]
