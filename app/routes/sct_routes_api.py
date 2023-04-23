"""
    sct_routes_api.py
    -------
    This module consists of application api
"""
import flask_excel
from flask import request, jsonify
from datetime import datetime
import random
from flask_login import current_user

from app.utilities.sct_env import *
from app.utilities.sct_security import get_user_role


def define_routes_api(app):
    """
    Application Routes

    :param app: Flask application object
    :return: None
    """

    db = app.config["SCT_DATA_DB"]
    uploads = app.config["SCT_UPLOAD_HANDLER"]

    @app.route("/api/table/<str: table_name>/<str: page_size>/<str: batch_num>", methods=["GET"])
    def api_table_data(table_name, page_size, batch_num):
        """
        Get table data

        :return: Table data dictionary, HTTP Status

        Example::

            { "data": [ {"col-1": "some", "col-2": 3}, ... ] }
        """
        app.logger.info("Table list, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = {"data": []}

        if user_role in ["ADMIN", "OPERATOR", "VIEWER"]:
            pass

    @app.route("/api/tables", methods=["GET"])
    def api_tables():
        """
        List of tables in DB

        :return: List of tables, HTTP Status

        Example::

            { "tables": [ "table_01", "table_02" ] }
        """
        app.logger.info("Table list, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = {"tables": []}

        if user_role in ["ADMIN", "OPERATOR", "VIEWER"]:
            try:
                table_list = db.get_table_list(sct_db_schema)
                app.logger.debug("Table list: {}".format(table_list))
                result["tables"] = table_list
                http_status = 200
            except Exception as e:
                app.logger.error("Exception received fetching table list: \n{}".format(e))
                result["message"] = "Function: api_tables, Exception: {}".format(e.args)
                http_status = 500
        else:
            http_status = 403

        return jsonify(result), http_status

    @app.route("/api/table_columns/<str: table_name>", methods=["GET"])
    def api_table_columns(table_name):
        """
        Column details for a table

        :return: Column dictionary, HTTP Status

        Example::

            { "columns": {"column_01": { "type": "integer", "description": "Some", "length": "25" }, ... } }
        """
        app.logger.info("Table columns, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = dict()

        if user_role in ["ADMIN", "OPERATOR", "VIEWER"]:
            try:
                result["columns"] = db.get_table_columns(table_name)
                app.logger.debug("Table columns: {}".format(result))
                http_status = 200
            except Exception as e:
                app.logger.error("Exception received while getting table columns: \n{}".format(e))
                result["message"] = "Function: api_table_columns, Exception: {}".format(e.args)
                http_status = 500
        else:
            http_status = 403

        return jsonify(result), http_status

    @app.route("/api/table_pk/<str: table_name>", methods=["GET"])
    def api_table_pk(table_name):
        """
        List of Primary Key columns

        :return: Column name list, HTTP Status

        Example::

            { "columns": [ "col-1", "col-2" ] }
        """
        app.logger.info("Primary key columns, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = {"columns": []}

        if user_role in ["ADMIN", "OPERATOR", "VIEWER"]:
            try:
                result["columns"] = db.get_table_pk(table_name)
                app.logger.debug("Table primary key columns: {}".format(result["columns"]))
                http_status = 200
            except Exception as e:
                app.logger.error("Exception received while getting table primary key columns: \n{}".format(e))
                result["message"] = "Function: api_table_pk, Exception: {}".format(e.args)
                http_status = 500
        else:
            http_status = 403

        return jsonify(result), http_status

    @app.route("/api/table_fk/<str: table_name>", methods=["GET"])
    def api_table_fk(table_name):
        """
        List of foreign key columns

        :return: Column name list, HTTP Status

        Example::

            { "columns": [ "col-1", "col-2" ] }
        """
        app.logger.info("Foreign key columns, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = {"columns": []}

        if user_role in ["ADMIN", "OPERATOR", "VIEWER"]:
            try:
                result["columns"] = db.get_table_fk(table_name)
                app.logger.debug("Table foreign key columns: {}".format(result["columns"]))
                http_status = 200
            except Exception as e:
                app.logger.error("Exception received while getting table foreign key columns: \n{}".format(e))
                result["message"] = "Function: api_table_fk, Exception: {}".format(e.args)
                http_status = 500
        else:
            http_status = 403

        return jsonify(result), http_status

    @app.route("/api/table_insert_columns/<str: table_name>", methods=["GET"])
    def api_table_insert_columns(table_name):
        """
        List of columns used for insert operation

        :return: Column name list, HTTP Status

        Example::

            { "columns": [ "col-1", "col-2" ] }
        """
        app.logger.info("Columns used for insert operation, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = {"columns": []}

        if user_role in ["ADMIN", "OPERATOR", "VIEWER"]:
            try:
                result["columns"] = db.get_table_insert_columns(table_name)
                app.logger.debug("Table columns used for insert operation: {}".format(result["columns"]))
                http_status = 200
            except Exception as e:
                app.logger.error("Exception received while getting columns used for insert operation: \n{}".format(e))
                result["message"] = "Function: api_table_insert_columns, Exception: {}".format(e.args)
                http_status = 500
        else:
            http_status = 403

        return jsonify(result), http_status

    @app.route("/api/create_row/<str: table_name>", methods=["GET"])
    def api_table_create_row(table_name):
        """
        Create a row

        :return: Row detail of the row, HTTP Status

        Example::

            { "record": {"col-1": 122, "col-2": "dummy"} }
        """
        app.logger.info("Adding record to table, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = dict()

        if user_role in ["ADMIN", "OPERATOR"]:
            try:
                parm_dict = dict()
                for column_name in api_table_insert_columns(table_name).get_json()["columns"]:
                    parm_dict[column_name] = request.args.get(column_name)
                app.logger.info("Insert row detail: {}".format(parm_dict))
                db.add_table_row(table_name, **parm_dict)
                result["record"] = parm_dict
                http_status = 200
            except Exception as e:
                app.logger.error("Exception received while creating record: \n{}".format(e))
                result["message"] = "Function: api_table_create_row, Exception: {}".format(e.args)
                http_status = 500
        else:
            http_status = 403

        return jsonify(result), http_status

    @app.route("/api/delete_row/<str: table_name>/<int: page_number>/<int: element_id>", methods=["GET"])
    def api_table_delete_row(table_name, page_number, element_id):
        """
        Delete a row

        :return: Row detail of the row, HTTP Status

        Example::

            { "record": {"col-1": 122, "col-2": "dummy"} }
        """
        app.logger.info("Delete record in table, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = dict()

        if user_role in ["ADMIN", "OPERATOR"]:
            try:
                app.logger.info("Dropping row from table {} from page {} element {}".format(
                    table_name, page_number, element_id))
                result["record"] = db.drop_table_row(table_name, page_number, element_id)
                http_status = 200
            except Exception as e:
                app.logger.error("Exception received while dropping record: \n{}".format(e))
                result["message"] = "Function: api_table_delete_row, Exception: {}".format(e.args)
                http_status = 500
        else:
            http_status = 403

        return jsonify(result), http_status

    @app.route("/api/edit_row/<str: table_name>/<int: page_number>/<int: element_id>", methods=["GET"])
    def api_table_edit_row(table_name, page_number, element_id):
        """
        Delete a row

        :return: Row detail of the row, HTTP Status

        Example::

            { "record": {"col-1": 122, "col-2": "dummy"} }
        """
        app.logger.info("Adding record to table, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = dict()

        if user_role in ["ADMIN", "OPERATOR"]:
            try:
                app.logger.info("Edit row in table {} from page {} element {}".format(
                    table_name, page_number, element_id))
                edit_row = db.drop_table_row(table_name, page_number, element_id)
                http_response = api_table_pk(table_name)
                if http_response.status == 200:
                    pk_columns = http_response.get_json()["columns"]
                else:
                    raise Exception("Execution in getting primary key for table {}".format(table_name))
                http_response = api_table_insert_columns(table_name)
                if http_response.status == 200:
                    insert_columns = http_response.get_json()["columns"]
                else:
                    raise Exception("Execution in getting table({}) columns for insert".format(table_name))
                parm_dict = dict()
                for column_name in insert_columns:
                    if column_name not in pk_columns and len(request.args.get(column_name)):
                        parm_dict[column_name] = request.args.get(column_name)
                    else:
                        parm_dict[column_name] = edit_row(column_name)
                app.logger.info("Edit row detail: {}".format(parm_dict))
                db.edit_table_row(table_name, **parm_dict)
                result["record"] = parm_dict
                http_status = 200
            except Exception as e:
                app.logger.error("Exception received while edit record: \n{}".format(e))
                result["message"] = "Function: api_table_edit_row, Exception: {}".format(e.args)
                http_status = 500
        else:
            http_status = 403

        return jsonify(result), http_status

    @app.route("/api/upload/<str: table_name>/<str: file_name>", methods=["GET"])
    def api_upload(table_name, file_name):
        """
        Upload data file API

        :return: Uploaded file name, HTTP Status
        """
        app.logger.info("Uploading file to server, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))
        result = dict()

        if user_role in ["ADMIN", "OPERATOR"]:
            try:
                app.logger.info("Upload file {} for table {}".format(
                    file_name, table_name))
                server_file_name_str = "{} {} {} {}".format(
                    user_name, table_name, datetime.now().strftime("%Y%m%d:%H:%M:%S:%f"), random.randint(1, 10000))

                server_file_name = "{}.csv".format(abs(hash(server_file_name_str)))
                app.logger.info("File name string {}, file name {}".format(server_file_name_str, server_file_name))
                uploads.save(file_name, name=server_file_name)
                result["file"] = server_file_name
                http_status = 200
            except Exception as e:
                app.logger.error("Exception received while uploading: \n{}".format(e))
                result["message"] = "Function: api_upload, Exception: {}".format(e.args)
                http_status = 500
        else:
            http_status = 403

        return jsonify(result), http_status

    @app.route("/api/download/<str: table_name>", methods=["GET"])
    def api_download(table_name):
        """
        Download data as CSV

        :return: None
        """
        app.logger.info("Downloading data as CSV, user {}".format(current_user.get_id()))
        if current_user.get_id():
            user_name = current_user.email
            app.logger.info("Email: {}".format(user_name))
        else:
            user_name = None
        user_role = get_user_role(user_name)
        app.logger.info("User {} has assigned role {}".format(user_name, user_role))

        if user_role in ["ADMIN", "OPERATOR", "VIEWER"]:
            with_data = int(request.args.get("with_data")) if request.args.get("with_data") else 1
            batch_num = int(request.args.get("batch_num")) if request.args.get("with_data") else 1
            app.logger.info("Table to fetch data {} of batch {}, with data {}".format(table_name, batch_num, with_data))

            if with_data:
                http_response = api_table_data(table_name, sct_ui_download_size, batch_num)
                if http_response.status == 200:
                    table_data = http_response.get_json()["data"]
                else:
                    raise Exception("Execution in getting data for table {}".format(table_name))
                app.logger.debug("Table data: {}".format(table_data))

                data_columns = table_data[0].keys()
                download_data = [data_columns]
                for row in table_data:
                    download_data.append(
                        [row[column_name] for column_name in data_columns]
                    )
            else:
                http_response = api_table_insert_columns(table_name)
                if http_response.status == 200:
                    table_cols = http_response.get_json()["columns"]
                else:
                    raise Exception("Execution in getting columns for table {}".format(table_name))

                app.logger.debug("Table columns details: {}".format(table_cols))
                download_data = [table_cols]

            app.logger.debug("Download data: {}".format(download_data))

            file_name = "{}_{}.csv".format(
                table_name, datetime.now().strftime("%Y%m%d_%H%M"))
            app.logger.info("Downloaded file name {}".format(file_name))
            return flask_excel.make_response_from_array(download_data, file_type="csv", status=200, file_name=file_name)
