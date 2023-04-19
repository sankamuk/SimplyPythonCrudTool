"""
    sct_env.py
    -------
    Environment setup script
"""
import os

#######################################################################
# App Secret
# # Flask application secret
sct_app_secret = os.environ.get("SCT_APP_SECRET", "somenath@the@boss")
#######################################################################

#######################################################################
# Database Related
# # Database
sct_db_name = os.environ.get("SCT_DB_NAME", "default")
# # Schema
sct_db_schema = os.environ.get("SCT_DB_SCHEMA", "public")
# # Database user
sct_db_user = os.environ.get("SCT_DB_USER", "postgres")
# # Database host
sct_db_host = os.environ.get("SCT_DB_HOST", "localhost")
# # Database port
sct_db_port = os.environ.get("SCT_DB_PORT", "5432")
# # Database user password
sct_db_pwd = os.environ["SCT_DB_PWD"]
# # Table column comment that are not insert/update enabled
sct_table_auto_populated_column_comment = "NO_DIRECT_UPDATE"
# # Table columns to be available in lookup view for insert/updated in referred table
sct_table_referenced_column_in_lookup_view = "IS_LOOKED_UP"
#######################################################################

#######################################################################
# UI Related
# # Max record to show per page
sct_ui_pagesize = int(os.environ.get("SCT_UI_PAGESIZE", "5"))
# # Max record in downloaded CSV
sct_ui_download_size = int(os.environ.get("SCT_UI_DOWNLOAD_SIZE", "2000"))
# # Max record that can be appended uploaded feature
sct_ui_upload_size = int(os.environ.get("SCT_UI_UPLOAD_SIZE", "500"))
#######################################################################

#######################################################################
# Audit Related
# # Audit database
sct_audit_type = os.environ.get("SCT_AUDIT_TYPE", "db")
# # Audit schema
sct_audit_db_schema = os.environ.get("SCT_AUDIT_DB_SCHEMA", "governance")
# # Audit table
sct_audit_db_table = os.environ.get("SCT_AUDIT_DB_TABLE", "sct_audits")
#######################################################################

#######################################################################
# Scheduler
# # Scheduler Interval Value
sct_scheduler_interval_value = os.environ.get("SCT_SCHEDULER_INTERVAL_VALUE", "720")
# # Max failed attempt
sct_scheduler_job_max_attempt = os.environ.get("SCT_SCHEDULER_JOB_MAX_ATTEMPT", "1")
#######################################################################

#######################################################################
# Authentication
# # Okta Domain
sct_auth_okta_domain = os.environ.get("SCT_AUTH_OKTA_DOMAIN", None)
# # Okta Client Id
sct_auth_okta_client_id = os.environ.get("SCT_AUTH_OKTA_CLIENT_ID", None)
# # Okta Client secret
sct_auth_okta_client_secret = os.environ.get("SCT_AUTH_OKTA_CLIENT_SECRET", None)
#######################################################################

#######################################################################
# Authorization
# # Roles               - Available authorization roles supported by tool
# #         VIEWER      - No Access
# #         VIEWER      - View Tables and its Data
# #         OPERATOR    - (VIEW ROLE) + ADD,UPDATE,DROP Table Data
# #         ADMIN       - (OPERATOR ROLE) + View Audits
SCT_ACCESS_ROLES = ["ADMIN", "OPERATOR", "VIEWER", "NONE"]
# # Roles assigned to anonymous user (without login)
SCT_ACCESS_ANONYMOUS_ROLE = "NONE"
# # List of principal assigned ADMIN role
SCT_ACCESS_ADMIN = "*"
# # List of principal assigned OPERATOR role
SCT_ACCESS_OPERATOR = "*"
# # List of principal assigned VIEWER role
SCT_ACCESS_VIEWER = "*"
#######################################################################

#######################################################################
# MAIL Setup
# # Mail Server
sct_mail_enabled = os.environ.get("SCT_MAIL_ENABLED", "")
# # Mail Server
sct_mail_server = os.environ.get("SCT_MAIL_SERVER", None)
# # Mail Server POrt
sct_mail_port = os.environ.get("SCT_MAIL_PORT", None)
# # Mail Server TLS Support
sct_mail_use_tls = os.environ.get("SCT_MAIL_USE_TLS", "")
# # Mail Server SSL Support
sct_mail_use_ssl = os.environ.get("SCT_MAIL_USE_SSL", "")
# # Mail Server User
sct_mail_user = os.environ.get("SCT_MAIL_USERNAME", None)
# # Mail Server User Password
sct_mail_password = os.environ.get("SCT_MAIL_PASSWORD", None)
# # Notification Recipients (Comma Separated List)
sct_mail_recipients = os.environ.get("SCT_MAIL_RECIPIENTS", None)
#######################################################################
