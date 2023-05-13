"""
    Simple Python CRUD Tool
    -----------------------
    Web Based DB Client to View, Query & Mutate data in a secured and trackable manner.

    `DOCUMENTATION <https://sankamuk.github.io/SimplyPythonCrudTool/>`_

    .. note:: This is under development, expect breaking changes until first release.
"""
from setuptools import setup, find_packages

setup(
    name='simple-python-crud-tool',
    version='1.0.0',
    license='MIT',
    keywords='python flask database crud',
    description="Simple Python CRUD Tool",
    author='Sankar Mukherjee',
    author_email='sanmuk21@gmail.com',
    python_requires='>=3',
    packages=['app', 'app.utilities', 'app.routes'],
    py_modules=['app.sct_app'],
    install_requires=[
        'Flask',
        'Flask-Login',
        'Flask-Cors',
        'pyOpenSSL',
        'requests',
        'psycopg2-binary',
        'mysql-connector-python',
        'Flask-Excel',
        'Flask-Reuploaded',
        'Flask-APScheduler',
        'Flask-Mail',
        'jinja2'
    ],
    include_package_data=True,
    project_urls={
        'Documentation': 'https://sankamuk.github.io/SimplyPythonCrudTool'
    },
    entry_points={
        'console_scripts': [
            'sct-run=app.sct_app:init_sct_app',
        ],
    },
)
