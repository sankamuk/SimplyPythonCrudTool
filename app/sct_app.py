"""
    app.py
    -------
    Simple Python Crud Tool - Entrypoint Script
"""
from flask import Flask, redirect, url_for
import flask_excel
from flask_apscheduler import APScheduler
from flask_uploads import UploadSet, configure_uploads, DATA
import secrets
from logging.config import dictConfig
from flask_cors import CORS
from flask_login import (
    LoginManager
)

from app.utilities.sct_env import *
from app.utilities.databases.sct_db import init_app_database, init_audit_database
from app.utilities.sct_logging import logger_conf_dict
from app.routes.sct_routes_api import define_routes_api
from app.routes.sct_routes_views import define_routes_view
from app.utilities.sct_security import define_security
from app.utilities.sct_mail import enable_email_support
from app.utilities.sct_schedules import sct_scheduled_bulk_loader

# Create Application
# # Initiate application
app = Flask(__name__)
# # Set secret
app.config.update({'SECRET_KEY': secrets.token_hex(64)})
CORS(app)


# Logging
dictConfig(logger_conf_dict)


# Database
init_app_database(app)
init_audit_database(app)


# Download & Upload Setup
# # Initiate download manager
flask_excel.init_excel(app)
# # Initiate upload manager
files_uploads = UploadSet("files", DATA)
app.config["UPLOADED_FILES_DEST"] = 'static/uploads'
configure_uploads(app, files_uploads)
app.config["SCT_UPLOAD_HANDLER"] = files_uploads


# Scheduler
# # Scheduler Actions
def sct_scheduled_tasks():
    """SCT Scheduled Tasks"""
    sct_scheduled_bulk_loader(app)


# # Scheduler Configuration
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


# # Scheduler Initiation
app.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(app)


# Notification
if bool(sct_mail_enabled):
    enable_email_support(app)


# Security
# # Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
# # Authentication
define_security(app, login_manager)


# Routes
# # API
define_routes_api(app)
# # Views
define_routes_view(app)


@app.route("/")
def home():
    """
    Default home route

    :return: SCT Application Home (HTML)
    """
    return redirect(url_for('data'))


# Init Application
def init_sct_app():
    """
    Initialize SCT Application

    :return: None
    """
    scheduler.start()
    app.run()


if __name__ == '__main__':
    init_sct_app()
