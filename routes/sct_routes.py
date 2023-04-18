"""
    sct_routes.py
    -------
    This module consists of application views
"""
from flask import render_template, request, redirect, url_for
from math import ceil
from datetime import datetime
import json
from flask_login import current_user

from utilities.sct_env import *
from utilities.sct_security import get_user_role


def define_routes(app, db):
    """
    Application Routes

    :param app: Flask application object
    :param db: Database Interface Object <DbBackEnd>
    :return: None
    """

    @app.route("/data", methods=["GET"])
    def data():
        """
        Generate table view

        :return: Table Page <HTML>
        """
        app.logger.info("Fetching table list, user {}".format(current_user.get_id()))

        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_list = db.get_table_list(sct_db_schema)
        app.logger.debug("Table list: {}".format(table_list))

        table_name = request.args.get("table_name") if request.args.get("table_name") else table_list[0]
        page_num = int(request.args.get("page_num")) if request.args.get("page_num") else 1
        app.logger.info("Dataset - table_name = {}, page_num = {}".format(table_name, page_num))

        table_details = db.get_table_info(table_name, page_num, sct_ui_pagesize)
        app.logger.debug("Table details: {}".format(table_details))

        current_pg = (page_num if 0 < page_num <= ceil(table_details["table_count"] / sct_ui_pagesize) else
                      1 if page_num < 1 else ceil(table_details["table_count"] / sct_ui_pagesize))
        app.logger.info("Current Page: {}".format(current_pg))

        db.add_audit(sct_audit_db_table, user_name, "READ_TABLE", table_name, {
            "page_num": page_num,
            "current_page": current_pg,
            "table_count": table_details["table_count"]
        })
        return render_template("index.html",
                               record_count=sct_ui_pagesize,
                               page_num=current_pg,
                               total_page=ceil(table_details["table_count"] / sct_ui_pagesize),
                               table_name=table_name,
                               table_list=table_list,
                               table_count=table_details["table_count"],
                               view_column_list=(table_details["view_columns"]).keys(),
                               insert_column_list=table_details["insert_columns"],
                               pk_column_list=table_details["pk_columns"],
                               data_list=table_details["table_data"],
                               logged_in_user=user_name,
                               logged_user_role=user_role,
                               current_server_time=datetime.now().strftime("%d %B, %Y %H:%M:%S (%A)")
                               )

    @app.route("/audit", methods=["GET"])
    def audit():
        """
        Get Audits

        :return: Audit Page <HTML>
        """
        app.logger.info("Audit processing, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_list = db.get_table_list(sct_db_schema)
        app.logger.debug("Table list: {}".format(table_list))

        page_num = int(request.args.get("page_num")) if request.args.get("page_num") else 1
        app.logger.info("Dataset - table_name = {}, page_num = {}".format(sct_audit_db_table, page_num))

        audit_details = db.get_audits(sct_audit_db_table, page_num, sct_ui_pagesize)
        app.logger.debug("Audits: {}".format(audit_details))
        current_pg = (page_num if 0 < page_num <= ceil(audit_details["audits_count"] / sct_ui_pagesize) else
                      1 if page_num < 1 else ceil(audit_details["audits_count"] / sct_ui_pagesize))
        app.logger.info("Current Page: {}".format(current_pg))

        db.add_audit(sct_audit_db_table, user_name, "READ_AUDIT", sct_audit_db_table, {
            "page_num": page_num,
            "current_page": current_pg,
            "audit_count": audit_details["audits_count"]
        })
        return render_template("audits.html",
                               record_count=sct_ui_pagesize,
                               page_num=current_pg,
                               total_page=ceil(audit_details["audits_count"] / sct_ui_pagesize),
                               table_list=table_list,
                               table_count=audit_details["audits_count"],
                               data_list=audit_details["audits_data"],
                               logged_in_user=user_name,
                               logged_user_role=user_role,
                               current_server_time=datetime.now().strftime("%d %B, %Y %H:%M:%S (%A)")
                               )

    @app.route("/api/add", methods=["POST"])
    def api_add():
        """
        Add record API

        :return: Table Page <HTML>
        """
        app.logger.info("Adding record to table, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_name = request.args.get("table_name")
        app.logger.info("Table name: {}".format(table_name))

        table_details = db.get_table_columns(table_name)
        app.logger.debug("Table details: {}".format(table_details))

        parm_dict = dict()
        for col in table_details["insert"].keys():
            parm_dict[col] = request.form[col]
        app.logger.info("Add record detail: {}".format(parm_dict))

        db.add_table_record(table_name, **parm_dict)
        app.logger.info("Successfully added record.")

        db.add_audit(sct_audit_db_table, user_name, "ADD_ROW", table_name, {
            "record_detail": parm_dict,
            "status": "SUCCESS"
        })
        return redirect(url_for('data', table_name=table_name))

    @app.route("/api/drop", methods=["POST"])
    def api_drop():
        """
        Drop record API

        :return: Table Page <HTML>
        """
        app.logger.info("Dropping record to table, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_name = request.args.get("table_name")
        page_num = int(request.args.get("page_num"))
        element_id = int(request.form["id"])
        app.logger.info("Deleted record detail - table_name = {}, page_num = {}, element_id = {}".format(table_name,
                                                                                                         page_num,
                                                                                                         element_id))

        table_details = db.get_table_info(table_name, page_num, sct_ui_pagesize)
        app.logger.debug("Table details: {}".format(table_details))

        rec_to_delete = table_details["table_data"][element_id]
        app.logger.info("Deleted record: {}".format(rec_to_delete))

        db.drop_table_record(table_name, **rec_to_delete)
        app.logger.info("Successfully deleted record.")

        db.add_audit(sct_audit_db_table, user_name, "DELETE_ROW", table_name, {
            "record_deleted": rec_to_delete,
            "status": "SUCCESS"
        })
        return redirect(url_for('data', table_name=table_name))

    @app.route("/api/edit", methods=["POST"])
    def api_edit():
        """
        Update record API

        :return: Table Page <HTML>
        """
        app.logger.info("Updating record to table, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_name = request.args.get("table_name")
        page_num = int(request.args.get("page_num"))
        element_id = int(request.form["id"])
        app.logger.info("Update record detail - table_name = {}, page_num = {}, element_id = {}".format(table_name,
                                                                                                        page_num,
                                                                                                        element_id))

        table_details = db.get_table_info(table_name, page_num, sct_ui_pagesize)
        app.logger.debug("Table details: {}".format(table_details))

        rec_to_edit = table_details["table_data"][element_id]
        app.logger.info("Edit record (Initial Version): {}".format(rec_to_edit))

        parm_dict = dict()
        for col in table_details["insert_columns"].keys():
            if col not in table_details["pk_columns"] and len(request.form[col]):
                app.logger.debug("Getting column value from HTTP request.")
                parm_dict[col] = request.form[col]
            else:
                app.logger.debug("Getting column value from current DB data.")
                parm_dict[col] = rec_to_edit[col]

        app.logger.info("Edit record (Updated Version): {}".format(parm_dict))

        db.edit_table_record(table_name, **parm_dict)
        app.logger.info("Successfully updated record.")

        db.add_audit(sct_audit_db_table, user_name, "UPDATE_ROW", table_name, {
            "record_before": rec_to_edit,
            "record_after": parm_dict,
            "status": "SUCCESS"
        })
        return redirect(url_for('data', table_name=table_name))

    @app.route("/api/upload", methods=["POST"])
    def api_upload():
        """
        Upload data file API

        :return: Table Page <HTML>
        """
        app.logger.info("Updating file to server, user {}".format(current_user.get_id()))
        table_name = request.args.get("table_name")
        return redirect(url_for('data', table_name=table_name))

    @app.route("/api/download", methods=["POST"])
    def api_download():
        """
        Download data as CSV

        :return: Table Page <HTML>
        """
        app.logger.info("Downloading data as CSV, user {}".format(current_user.get_id()))
        table_name = request.args.get("table_name")
        return redirect(url_for('data', table_name=table_name))
