import os
from flask import Flask, render_template, abort, jsonify, request, redirect, url_for
from math import ceil
from sct_db import DbBackEnd

# Read Environment
# # Database Related
sct_db_name = os.environ.get("SCT_DB_NAME", "default")
sct_db_schema = os.environ.get("SCT_DB_SCHEMA", "public")
sct_db_user = os.environ.get("SCT_DB_USER", "postgres")
sct_db_host = os.environ.get("SCT_DB_HOST", "localhost")
sct_db_port = os.environ.get("SCT_DB_PORT", "5432")
sct_db_pwd = os.environ["SCT_DB_PWD"]

# # UI Related
sct_ui_pagesize = int(os.environ.get("SCT_UI_PAGESIZE", "3"))

# # Audit Related
sct_audit_type = os.environ.get("SCT_AUDIT_TYPE", "db")
sct_audit_container = os.environ.get("SCT_AUDIT_CONTAINER", "sct_audits")
sct_audit_schema = os.environ.get("SCT_AUDIT_SCHEMA", "public")


# Create Application
app = Flask(__name__)

# Init Database
db = DbBackEnd(sct_db_name, sct_db_schema, sct_db_user, sct_db_pwd, sct_db_host, sct_db_port)


@app.route("/")
def home():
    return redirect(url_for('data'))


@app.route("/data")
def data():
    table_list = db.get_table_list(sct_db_schema)
    table_name = request.args.get("table_name") if request.args.get("table_name") else table_list[0]
    page_num = int(request.args.get("page_num")) if request.args.get("page_num") else 1
    table_details = db.get_table_info(table_name, page_num, sct_ui_pagesize)
    current_pg = (page_num if 0 < page_num <= ceil(table_details["table_count"] / sct_ui_pagesize) else
                  1 if page_num < 1 else ceil(table_details["table_count"] / sct_ui_pagesize))

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
                           data_list=table_details["table_data"]
                           )


@app.route("/api/add", methods=["POST"])
def api_add():
    table_name = request.args.get("table_name")
    table_details = db.get_table_columns(table_name)
    parm_dict = dict()
    for col in table_details["insert"].keys():
        parm_dict[col] = request.form[col]
    db.add_table_record(table_name, **parm_dict)
    return redirect(url_for('data', table_name=table_name))


@app.route("/api/drop", methods=["POST"])
def api_drop():
    table_name = request.args.get("table_name")
    page_num = int(request.args.get("page_num"))
    element_id = int(request.form["id"])
    table_details = db.get_table_info(table_name, page_num, sct_ui_pagesize)
    db.drop_table_record(table_name, **table_details["table_data"][element_id])
    return redirect(url_for('data', table_name=table_name))


@app.route("/api/edit", methods=["POST"])
def api_edit():
    table_name = request.args.get("table_name")
    page_num = int(request.args.get("page_num"))
    element_id = int(request.form["id"])
    table_details = db.get_table_info(table_name, page_num, sct_ui_pagesize)
    rec_to_edit = table_details["table_data"][element_id]
    parm_dict = dict()
    for col in table_details["insert_columns"].keys():
        if len(request.form[col]):
            parm_dict[col] = request.form[col]
        else:
            parm_dict[col] = rec_to_edit[col]
    for col in table_details["pk_columns"]:
        parm_dict[col] = rec_to_edit[col]
    db.edit_table_record(table_name, **parm_dict)
    return redirect(url_for('data', table_name=table_name))


@app.route("/api/upload", methods=["POST"])
def api_upload():
    table_name = request.args.get("table_name")
    return redirect(url_for('data', table_name=table_name))


if __name__ == '__main__':
    app.run()
