from flask import Flask, render_template, abort, jsonify, request, redirect, url_for
from math import ceil
from sct_db import DbBackEnd

app = Flask(__name__)
db = DbBackEnd("employee", "postgres", "admin", "192.168.56.101", "5432")


@app.route("/data")
def data():
    table_list = db.get_table_list()
    table_name = request.args.get("table_name") if request.args.get("table_name") else table_list[0]
    page_num = int(request.args.get("page_num")) if request.args.get("page_num") else 1
    table_details = db.get_table_info(table_name, page_num)
    current_pg = (page_num if 0 < page_num <= ceil(table_details["table_count"] / 3) else
                  1 if page_num < 1 else ceil(table_details["table_count"] / 3))

    return render_template("index.html",
                           record_count=3,
                           page_num=current_pg,
                           total_page=ceil(table_details["table_count"] / 3),
                           table_name=table_name,
                           table_list=table_list,
                           table_count=table_details["table_count"],
                           view_column_list=(table_details["view_columns"]).keys(),
                           insert_column_list=table_details["insert_columns"],
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
    table_details = db.get_table_info(table_name, page_num)
    db.drop_table_record(table_name, **table_details["table_data"][element_id])
    return redirect(url_for('data', table_name=table_name))


if __name__ == '__main__':
    app.run()