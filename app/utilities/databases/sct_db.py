"""
    sct_db.py
    -------
    This module initiates SCT Tool RDBMS operations
"""
import os
import glob
from importlib import import_module
from inspect import getmembers, isabstract, isclass

from app.utilities.sct_env import *


def init_app_database(app):
    """
    Initiate application databased for SCT tool

    :param app: Flask application object
    :return: None
    """

    mod_path = "app.utilities.databases.sct_{}".format(sct_db_type)
    py_module = import_module(mod_path)
    db = None
    for c in getmembers(py_module, lambda m: isclass(m) and not isabstract(m)):
        if c[0] == "DbBackEnd":
            db = (c[1])(sct_db_name, sct_db_schema, sct_db_user, sct_db_pwd, sct_db_host, sct_db_port)
    if not db:
        app.logger.error("Could not initiate DB. Exiting!")
        raise Exception("Could not initiate DB")

    app.logger.info("Successfully initiated {} DB.".format(sct_db_type))
    app.config["SCT_DATA_DB"] = db


def init_audit_database(app):
    """
    Initiate application databased for SCT tool

    :param app: Flask application object
    :return: None
    """

    if (sct_db_type == "sqlite" and sct_audit_type == "sqlite" and
            sct_db_name == ":memory:" and sct_audit_db_name == ":memory:"):
        app.config["SCT_AUDIT_DB"] = app.config["SCT_DATA_DB"]
    else:
        mod_path = "app.utilities.databases.sct_{}".format(sct_audit_type)
        py_module = import_module(mod_path)
        db = None
        for c in getmembers(py_module, lambda m: isclass(m) and not isabstract(m)):
            if c[0] == "DbBackEnd":
                db = (c[1])(
                    sct_audit_db_name, sct_audit_db_schema, sct_audit_db_user, sct_audit_db_pwd,
                    sct_audit_db_host, sct_audit_db_port)
        if not db:
            app.logger.error("Could not initiate audit DB. Exiting!")
            raise Exception("Could not initiate audit DB")
        app.config["SCT_AUDIT_DB"] = db

    if sct_audit_table_create.lower() == "yes":
        (app.config["SCT_AUDIT_DB"]).create_audit_table(sct_audit_db_table)

    app.logger.info("Successfully initiated {} audit DB.".format(sct_db_type))

