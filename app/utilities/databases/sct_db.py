"""
    sct_db.py
    -------
    This module initiates SCT Tool RDBMS operations
"""
import os
from importlib import import_module
from inspect import getmembers, isabstract, isclass

from app.utilities.sct_env import *


def init_app_database(app):
    """
    Initiate application databased for SCT tool

    :param app:
    :return:
    """
    app_home = app.root_path
    mod_path = os.path.join(app_home, "utilities/databases/sct_{}.py".format(sct_db_type))
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

    :param app:
    :return:
    """
    app_home = app.root_path
    mod_path = os.path.join(app_home, "utilities/databases/sct_{}.py".format(sct_audit_type))
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

    if sct_audit_table_create.lower() == "yes":
        db.create_audit_table(sct_audit_db_table)

    app.logger.info("Successfully initiated {} audit DB.".format(sct_db_type))
    app.config["SCT_AUDIT_DB"] = db
