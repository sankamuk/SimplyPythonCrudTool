"""
    app.py
    -------
    Simple Python Crud Tool - Entrypoint Script
"""
from flask import Flask, redirect, url_for, g
import flask_excel
from flask_apscheduler import APScheduler
from flask_uploads import UploadSet, configure_uploads, DATA
import secrets
from logging.config import dictConfig
from flask_cors import CORS
from flask_login import (
    LoginManager
)

from utilities.sct_env import *
from utilities.sct_db import DbBackEnd
from utilities.sct_logging import logger_conf_dict
from routes.sct_routes import define_routes
from utilities.sct_security import define_security
from utilities.sct_mail import enable_email_support
from utilities.sct_schedules import sct_scheduled_bulk_loader

# Create Application
# # Initiate application
app = Flask(__name__)
# # Set secret
app.config.update({'SECRET_KEY': secrets.token_hex(64)})
CORS(app)
# # Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
# # Initiate download manager
flask_excel.init_excel(app)
# # Initiate upload manager
files_uploads = UploadSet("files", DATA)
app.config["UPLOADED_FILES_DEST"] = 'static/uploads'
configure_uploads(app, files_uploads)


# # Initiate scheduler
def sct_scheduled_tasks():
    """SCT Scheduled Tasks"""
    sct_scheduled_bulk_loader(app, db)


class Config:
    """App configuration."""
    sct_sch_cfg = {
        "id": "job1",
        "func": sct_scheduled_tasks,
        "trigger": "interval",
        "seconds": int(sct_scheduler_interval_value)
    }
    JOBS = [sct_sch_cfg]
    SCHEDULER_API_ENABLED = True


app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)

# # Initiate mail
if bool(sct_mail_enabled):
    enable_email_support(app)

# Logging
dictConfig(logger_conf_dict)

# Authentication
define_security(app, login_manager)

# Init Database
schema = {sct_db_schema, sct_audit_db_schema}
db = DbBackEnd(sct_db_name, schema, sct_db_user, sct_db_pwd, sct_db_host, sct_db_port)

# Views
define_routes(app, db, files_uploads)


@app.route("/")
def home():
    return redirect(url_for('data'))


# Init Application
if __name__ == '__main__':
    scheduler.start()
    app.run()
