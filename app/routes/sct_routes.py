"""
    sct_routes.py
    -------
    This module consists of application views
"""
import flask_excel
from flask import render_template, request, url_for, redirect
from math import ceil
from datetime import datetime
import random
from flask_login import current_user

from app.utilities.sct_env import *
from app.utilities.sct_security import get_user_role
from app.utilities.sct_mail import send_mail


def define_routes(app):
    """
    Application Routes

    :param app: Flask application object
    :return: None
    """

    db = app.config["SCT_DATA_DB"]
    audit_db = app.config["SCT_AUDIT_DB"]
    uploads = app.config["SCT_UPLOAD_HANDLER"]

    @app.route("/data", methods=["GET"])
    def data():
        """
        Generate table view

        :return: Table Page <HTML>
        """
        app.logger.info("Function: data, user {}".format(current_user.get_id()))

        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_list = db.get_table_list(sct_table_table_blacklist, sct_db_schema)
        app.logger.debug("Table list: {}".format(table_list))

        table_name = request.args.get("table_name") if request.args.get("table_name") else table_list[0]
        page_num = int(request.args.get("page_num")) if request.args.get("page_num") else 1
        app.logger.info("Dataset - table_name = {}, page_num = {}".format(table_name, page_num))

        search_col = request.args.get("search_col") if request.args.get("search_col") else None
        search_op = request.args.get("search_op") if request.args.get("search_op") else None
        search_val = request.args.get("search_val") if request.args.get("search_val") else None
        app.logger.info("Search - Column: {}, Operator: {}, Value: {} ({})".format(
            search_col,
            search_op,
            search_val,
            str(type(search_val))
        ))

        if search_col and search_op and search_val:
            table_details = audit_db.search_table_info(
                table_name, search_col, search_op, search_val, page_num, int(sct_ui_pagesize))
        else:
            table_details = db.get_table_info(table_name, page_num, int(sct_ui_pagesize))

        app.logger.debug("Table details: {}".format(table_details))

        current_pg = (page_num if 0 < page_num <= ceil(table_details["table_count"] / sct_ui_pagesize) else
                      1 if page_num < 1 else ceil(table_details["table_count"] / sct_ui_pagesize))
        app.logger.info("Current Page: {}".format(current_pg))

        audit_db.add_audit(sct_audit_db_table, user_name, "READ_TABLE", table_name, "SUCCESS", {
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
                               search_col=search_col,
                               search_op=search_op,
                               search_val=search_val,
                               logged_in_user=user_name,
                               logged_user_role=user_role,
                               current_server_time=datetime.now().strftime("%d %B, %Y %H:%M:%S (%A)")
                               )

    @app.route("/data/search", methods=["GET"])
    def search_data():
        """
        Search table data

        :return: Table Page <HTML>
        """
        app.logger.info("Function: search_data, user {}".format(current_user.get_id()))

        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_list = db.get_table_list(sct_table_table_blacklist, sct_db_schema)
        app.logger.debug("Table list: {}".format(table_list))

        table_name = request.args.get("table_name") if request.args.get("table_name") else table_list[0]
        page_num = int(request.args.get("page_num")) if request.args.get("page_num") else 1
        app.logger.info("Dataset - table_name = {}, page_num = {}".format(table_name, page_num))

        search_col = request.args.get("search_col") if request.args.get("search_col") else None
        search_op = request.args.get("search_op") if request.args.get("search_op") else None
        search_val = request.args.get("search_val") if request.args.get("search_val") else None
        app.logger.info("Search - Column: {}, Operator: {}, Value: {} ({})".format(
            search_col,
            search_op,
            search_val,
            str(type(search_val))
        ))

        audit_db.add_audit(sct_audit_db_table, user_name, "SEARCH_TABLE", table_name, "SUCCESS", {
            "Column": search_col,
            "Operator": search_op,
            "Value": search_val
        })
        return redirect(url_for(
            'data', table_name=table_name, search_col=search_col, search_op=search_op,
            search_val=search_val))

    @app.route("/audit", methods=["GET"])
    def audit():
        """
        Get Audits

        :return: Audit Page <HTML>
        """
        app.logger.info("Function: audit, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_list = db.get_table_list(sct_table_table_blacklist, sct_db_schema)
        app.logger.debug("Table list: {}".format(table_list))

        page_num = int(request.args.get("page_num")) if request.args.get("page_num") else 1
        app.logger.info("Dataset - table_name = {}, page_num = {}".format(sct_audit_db_table, page_num))

        audit_search_col = request.args.get("audit_search_col") if request.args.get("audit_search_col") else None
        audit_search_op = request.args.get("audit_search_op") if request.args.get("audit_search_op") else None
        audit_search_val = request.args.get("audit_search_val") if request.args.get("audit_search_val") else None
        app.logger.info("Search - Column: {}, Operator: {}, Value: {} ({})".format(
            audit_search_col,
            audit_search_op,
            audit_search_val,
            str(type(audit_search_val))
        ))

        if audit_search_col and audit_search_op and audit_search_val:
            audit_details = audit_db.search_audits(
                sct_audit_db_table, audit_search_col, audit_search_op, audit_search_val, page_num, sct_ui_pagesize)
        else:
            audit_details = audit_db.get_audits(sct_audit_db_table, page_num, sct_ui_pagesize)
        app.logger.debug("Audits: {}".format(audit_details))
        current_pg = (page_num if 0 < page_num <= ceil(audit_details["audits_count"] / sct_ui_pagesize) else
                      1 if page_num < 1 else ceil(audit_details["audits_count"] / sct_ui_pagesize))
        app.logger.info("Current Page: {}".format(current_pg))

        audit_db.add_audit(sct_audit_db_table, user_name, "READ_AUDIT", sct_audit_db_table, "SUCCESS", {
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
                               audit_search_col=audit_search_col,
                               audit_search_op=audit_search_op,
                               audit_search_val=audit_search_val,
                               logged_in_user=user_name,
                               logged_user_role=user_role,
                               current_server_time=datetime.now().strftime("%d %B, %Y %H:%M:%S (%A)")
                               )

    @app.route("/audit/search", methods=["GET"])
    def search_audit():
        """
        Get Audits

        :return: Audit Page <HTML>
        """
        app.logger.info("Function: search_audit, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_list = db.get_table_list(sct_table_table_blacklist, sct_db_schema)
        app.logger.debug("Table list: {}".format(table_list))

        page_num = int(request.args.get("page_num")) if request.args.get("page_num") else 1
        app.logger.info("Dataset - table_name = {}, page_num = {}".format(sct_audit_db_table, page_num))

        audit_search_col = request.args.get("audit_search_col") if request.args.get("audit_search_col") else None
        audit_search_op = request.args.get("audit_search_op") if request.args.get("audit_search_op") else None
        audit_search_val = request.args.get("audit_search_val") if request.args.get("audit_search_val") else None
        app.logger.info("Search - Column: {}, Operator: {}, Value: {}".format(
            audit_search_col,
            audit_search_op,
            audit_search_val
        ))

        audit_db.add_audit(sct_audit_db_table, user_name, "SEARCH_AUDIT", sct_audit_db_table, "SUCCESS", {
            "Column": audit_search_col,
            "Operator": audit_search_op,
            "Value": audit_search_val
        })
        return redirect(url_for(
            'audit', audit_search_col=audit_search_col, audit_search_op=audit_search_op,
            audit_search_val=audit_search_val))

    @app.route("/api/add", methods=["POST"])
    def api_add():
        """
        Add record API

        :return: Table Page <HTML>
        """
        app.logger.info("Function: api_add, user {}".format(current_user.get_id()))
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

        audit_db.add_audit(sct_audit_db_table, user_name, "ADD_ROW", table_name, "SUCCESS", {
            "record_detail": parm_dict
        })
        return redirect(url_for('data', table_name=table_name))

    @app.route("/api/drop", methods=["POST"])
    def api_drop():
        """
        Drop record API

        :return: Table Page <HTML>
        """
        app.logger.info("Function: api_drop, user {}".format(current_user.get_id()))
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
        search_col = request.args.get("search_col") if request.args.get("search_col") else None
        search_op = request.args.get("search_op") if request.args.get("search_op") else None
        search_val = request.args.get("search_val") if request.args.get("search_val") else None
        app.logger.info("Search - Column: {}, Operator: {}, Value: {} ({})".format(
            search_col,
            search_op,
            search_val,
            str(type(search_val))
        ))

        if search_col and search_op and search_val:
            table_details = audit_db.search_table_info(
                table_name, search_col, search_op, search_val, page_num, int(sct_ui_pagesize))
        else:
            table_details = db.get_table_info(table_name, page_num, int(sct_ui_pagesize))
        app.logger.debug("Table details: {}".format(table_details))

        rec_to_delete = table_details["table_data"][element_id]
        app.logger.info("Deleted record: {}".format(rec_to_delete))

        db.drop_table_record(table_name, **rec_to_delete)
        app.logger.info("Successfully deleted record.")

        audit_db.add_audit(sct_audit_db_table, user_name, "DELETE_ROW", table_name, "SUCCESS", {
            "record_deleted": rec_to_delete
        })
        return redirect(url_for('data', table_name=table_name))

    @app.route("/api/edit", methods=["POST"])
    def api_edit():
        """
        Update record API

        :return: Table Page <HTML>
        """
        app.logger.info("Function: api_edit, user {}".format(current_user.get_id()))
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

        search_col = request.args.get("search_col") if request.args.get("search_col") else None
        search_op = request.args.get("search_op") if request.args.get("search_op") else None
        search_val = request.args.get("search_val") if request.args.get("search_val") else None
        app.logger.info("Search - Column: {}, Operator: {}, Value: {} ({})".format(
            search_col,
            search_op,
            search_val,
            str(type(search_val))
        ))

        if search_col and search_op and search_val:
            table_details = audit_db.search_table_info(
                table_name, search_col, search_op, search_val, page_num, int(sct_ui_pagesize))
        else:
            table_details = db.get_table_info(table_name, page_num, int(sct_ui_pagesize))
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

        audit_db.add_audit(sct_audit_db_table, user_name, "UPDATE_ROW", table_name, "SUCCESS", {
            "record_before": rec_to_edit,
            "record_after": parm_dict
        })
        return redirect(url_for('data', table_name=table_name))

    @app.route("/api/upload", methods=["POST"])
    def api_upload():
        """
        Upload data file API

        :return: Table Page <HTML>
        """
        app.logger.info("Function: api_upload, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_name = request.args.get("table_name")
        app.logger.info("Table to fetch data {}".format(table_name))

        # Upload file in server
        file_name_raw = "{} {} {} {} {} {}".format(user_name,
                                                   sct_db_name,
                                                   sct_db_schema,
                                                   table_name,
                                                   datetime.now().strftime("%Y%m%d:%H:%M:%S:%f"),
                                                   random.randint(1, 10000))
        file_name = "{}.csv".format(abs(hash(file_name_raw)))
        uploads.save(request.files["file"], name=file_name)
        app.logger.info("Uploaded file saved as {}".format(file_name))

        audit_db.add_audit(sct_audit_db_table, user_name, "BULK_UPLOAD", table_name, "UPLOADED", {
            "file_name": file_name
        })
        return redirect(url_for('data', table_name=table_name))

    @app.route("/api/download", methods=["GET"])
    def api_download():
        """
        Download data as CSV

        :return: Table Page <HTML>
        """
        app.logger.info("Downloading data as CSV, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        table_name = request.args.get("table_name")
        with_data = int(request.args.get("with_data")) if request.args.get("with_data") else 1
        app.logger.info("Table to fetch data {}, with data {}".format(table_name, with_data))

        table_col_details = db.get_table_columns(table_name, False)
        app.logger.debug("Table columns details: {}".format(table_col_details))

        if with_data:
            op_type = "DOWNLOAD_DATA"
            table_data = db.get_table_data(table_name,
                                           table_col_details["view"].keys(),
                                           table_col_details["pk_columns"],
                                           sct_ui_download_size)
            app.logger.debug("Table data: {}".format(table_data))

            download_data = [table_col_details["view"].keys()]
            for rw in table_data:
                download_data.append(list(rw))
        else:
            op_type = "DOWNLOAD_TEMPLATE"
            download_data = [table_col_details["insert"].keys()]
        app.logger.debug("Download data: {}".format(download_data))

        file_name = "{}_{}_{}_{}.csv".format(sct_db_name,
                                             sct_db_schema,
                                             table_name,
                                             datetime.now().strftime("%Y%m%d_%H%M"))
        app.logger.info("Downloaded file name {}".format(file_name))
        audit_db.add_audit(sct_audit_db_table, user_name, op_type, table_name, "SUCCESS", {
            "file_name": file_name,
            "total_rows": len(download_data)
        })
        return flask_excel.make_response_from_array(download_data, file_type="csv", status=200, file_name=file_name)

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
