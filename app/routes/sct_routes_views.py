"""
    sct_routes_views.py
    -------
    This module consists of application views
"""
from flask import render_template, request, url_for, redirect
from math import ceil
from datetime import datetime
from flask_login import current_user

from app.utilities.sct_env import *
from app.utilities.sct_security import get_user_role
from app.utilities.sct_mail import send_mail


def define_routes_view(app):
    """
    Application Routes

    :param app: Flask application object
    :return: None
    """

    db = app.config["SCT_DATA_DB"]
    uploads = app.config["SCT_UPLOAD_HANDLER"]

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

        db.add_audit(sct_audit_db_table, user_name, "READ_TABLE", table_name, "SUCCESS", {
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

        db.add_audit(sct_audit_db_table, user_name, "READ_AUDIT", sct_audit_db_table, "SUCCESS", {
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

    @app.route("/register", methods=["GET"])
    def register():
        """
        Handles registration request

        :return: Table Page <HTML>
        """
        app.logger.info("Registration request")
        user_email = request.args.get("user_email")
        user_name = request.args.get("user_name")
        user_permission = request.args.get("user_permission")
        app.logger.info("Registration request made by {} with email {} for access type {}".format(
            user_name, user_email, user_permission))

        send_mail(app,
                  mail_type="register",
                  user_email=user_email,
                  user_name=user_name,
                  user_permission=user_permission)

        return redirect(url_for('data'))
