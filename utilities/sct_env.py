"""
    sct_env.py
    -------
    Environment setup script
"""
import os

# App Secret
sct_app_secret = os.environ.get("SCT_APP_SECRET", "somenath@the@boss")

# Database Related
sct_db_name = os.environ.get("SCT_DB_NAME", "default")
sct_db_schema = os.environ.get("SCT_DB_SCHEMA", "public")
sct_db_user = os.environ.get("SCT_DB_USER", "postgres")
sct_db_host = os.environ.get("SCT_DB_HOST", "localhost")
sct_db_port = os.environ.get("SCT_DB_PORT", "5432")
sct_db_pwd = os.environ["SCT_DB_PWD"]

# UI Related
sct_ui_pagesize = int(os.environ.get("SCT_UI_PAGESIZE", "3"))

# Audit Related
sct_audit_type = os.environ.get("SCT_AUDIT_TYPE", "db")
sct_audit_db_schema = os.environ.get("SCT_AUDIT_DB_SCHEMA", "governance")
sct_audit_db_table = os.environ.get("SCT_AUDIT_DB_TABLE", "sct_audits")

# Authentication
sct_auth_okta_domain = os.environ.get("SCT_AUTH_OKTA_DOMAIN", None)
sct_auth_okta_client_id = os.environ.get("SCT_AUTH_OKTA_CLIENT_ID", None)
sct_auth_okta_client_secret = os.environ.get("SCT_AUTH_OKTA_CLIENT_SECRET", None)

# Authorization
SCT_ACCESS_ROLES = ["ADMIN", "OPERATOR", "VIEWER", "NONE"]
SCT_ACCESS_ANONYMOUS_ROLE = "NONE"
SCT_ACCESS_ADMIN = "iam.san.muk@gmail.com"
SCT_ACCESS_OPERATOR = "san_muk21@yahoo.co.in"
SCT_ACCESS_VIEWER = "sanmuk@live.in"
