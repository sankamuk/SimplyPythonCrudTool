Configurations
==============

The application is configurable with environment variable. Below we present the list of configurations and there usage.

.. topic:: Basic configuration for quick start.

    You should set the below before even initiating quick start for the application.
    - SCT_DB_NAME

    - SCT_DB_SCHEMA

    - SCT_DB_USER

    - SCT_DB_HOST

    - SCT_DB_PORT

    - SCT_DB_PWD

    With this in place your basic CRUD operation will be **ON**.


Below is the component wise configurations.


**DB Setup**: RDBMS hosting the primary datastore can be configured using below setting.


==========================  =====================================================================================================================================
Config         Remark
==========================  =====================================================================================================================================
SCT_DB_HOST                 Database host
SCT_DB_PORT                 Database port
SCT_DB_NAME                 Database name
SCT_DB_SCHEMA               Database schema
SCT_DB_USER                 Database user
SCT_DB_PWD                  Database user password
SCT_DB_TABLE_BLACKLIST      Regular expression which can be use to restrict access to one or more table using this application, blank string means no blacklist
==========================  =====================================================================================================================================


**UI Setup**: Web UI operation settings.


==========================  ===================================================
Config         Remark
==========================  ===================================================
SCT_UI_PAGESIZE             Max record to show per page
SCT_UI_DOWNLOAD_SIZE        Max record in downloaded CSV
SCT_UI_UPLOAD_SIZE          Max record that can be appended uploaded feature
==========================  ===================================================


**Audit Setup**: Currently only RDBMS based audit is supported.
                 Currently also the Audit table need to be available in same DB instance like primary data but it can reside on different schema.

Audit table need to be available before starting tool::

    create table governance.sct_audits (
        audit_id serial PRIMARY KEY,
        audit_user VARCHAR (100) not null,
        audit_time timestamp NOT NULL DEFAULT NOW(),
        operation_performed VARCHAR (100) not null,
        table_name VARCHAR (100) not null,
        operation_status VARCHAR (15) not null,
        operation_metadata VARCHAR (5000)
    );


==========================  =================
Config         Remark
==========================  =================
SCT_AUDIT_TYPE              Audit database
SCT_AUDIT_DB_SCHEMA         Audit schema
SCT_AUDIT_DB_TABLE          Audit table
==========================  =================


**Authentication Setup**: Currently only Okta based authentication is supported.
                          There is also new user registration page where new user request for access which drops mail to admin to add user to Okta organization.

=========================== ====================
Config                      Remark
=========================== ====================
SCT_AUTH_OKTA_DOMAIN        Okta Domain
SCT_AUTH_OKTA_CLIENT_ID     Okta Client Id
SCT_AUTH_OKTA_CLIENT_SECRET Okta Client secret
=========================== ====================


**Authorization Setup**: Current there are four predefined roles for authorization, below is the access for the same.

- **NONE**: No access

- **VIEWER**: View table data only, no mutation allowed

- **OPERATOR**: View and mutate table data

- **ADMIN**: View and mutate table data also track audits


.. note::  If you have not enabled authentication you need to set ``SCT_ACCESS_ANONYMOUS_ROLE`` to ``ADMIN``.

           You can use wild card \* if you want to give ***all authenticated*** user to a role.



==========================  =================================================
Config         Remark
==========================  =================================================
SCT_ACCESS_ANONYMOUS_ROLE   Roles assigned to anonymous user (without login)
SCT_ACCESS_ADMIN            List of principal assigned ADMIN role
SCT_ACCESS_OPERATOR         List of principal assigned OPERATOR role
SCT_ACCESS_VIEWER           List of principal assigned VIEWER role
==========================  =================================================


**Email Setup**: If you do not want to use email notification set enabled to blank string. If you enable you will need to provide configuration from your email provider.

==========================  ==================================================
Config                      Remark
==========================  ==================================================
SCT_MAIL_ENABLED            Mail notification is enabled or disabled
SCT_MAIL_SERVER             Mail Server
SCT_MAIL_PORT               Mail Server Port
SCT_MAIL_USE_TLS            Mail Server TLS Support
SCT_MAIL_USE_SSL            Mail Server SSL Support
SCT_MAIL_USERNAME           Mail Server User
SCT_MAIL_PASSWORD           Mail Server User Password
SCT_MAIL_RECIPIENTS         Notification Recipients (Comma Separated List)
==========================  ==================================================


.. warning:: All configuration defaults are available for verification and updating in module ``utilities.sct_env``.
