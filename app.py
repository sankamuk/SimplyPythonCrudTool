"""
    app.py
    -------
    Simple Python Crud Tool - Entrypoint Script
"""
from flask import Flask, redirect, url_for, g
import secrets
from logging.config import dictConfig
from flask_cors import CORS
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from utilities.sct_env import *
from utilities.sct_db import DbBackEnd
from utilities.sct_logging import logger_conf_dict
from routes.sct_routes import define_routes
from utilities.sct_security import define_security

# Create Application
app = Flask(__name__)
app.config.update({'SECRET_KEY': secrets.token_hex(64)})
CORS(app)
login_manager = LoginManager()
login_manager.init_app(app)

# Logging
dictConfig(logger_conf_dict)

# Authentication
define_security(app, login_manager)

# Init Database
schema = {sct_db_schema, sct_audit_db_schema}
db = DbBackEnd(sct_db_name, schema, sct_db_user, sct_db_pwd, sct_db_host, sct_db_port)

# Views
define_routes(app, db)


@app.route("/")
def home():
    return redirect(url_for('data'))


# Init Application
if __name__ == '__main__':
    app.run()
