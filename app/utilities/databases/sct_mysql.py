"""
    sct_db.py
    -------
    This module controls SCT Tool specific database interaction
"""
import json
import csv
import mysql.connector
from math import ceil
from app.utilities.sct_utils import tuple_to_dict, tuple_to_list
from app.utilities.databases.sct_mysql_query import (
    SCT_QUERY_MYSQL_GET_FK_DETAIL,
    SCT_QUERY_MYSQL_GET_FK_LOOKUP,
    SCT_QUERY_MYSQL_GET_COLMN_DETAIL,
    SCT_QUERY_MYSQL_INSERT_ROW,
    SCT_QUERY_MYSQL_DROP_ROW,
    SCT_QUERY_MYSQL_UPDATE_ROW,
    SCT_QUERY_MYSQL_AUDIT_GET,
    SCT_QUERY_MYSQL_AUDIT_PUT,
    SCT_QUERY_MYSQL_AUDIT_BULK_LOAD,
    SCT_QUERY_MYSQL_AUDIT_TABLE_CREATION,
    SCT_QUERY_MYSQL_AUDIT_SEARCH
)


class DbBackEnd:
    """
        Backend Database Interface.
        .. admonition:: Note
            Defines all DB Communication codes.
    """

    def __init__(self,
                 database: str = "default",
                 schema=None,
                 user: str = "mysql",
                 password: str = "mysql",
                 host: str = "localhost",
                 port: str = "3306"):
        """
        DbBackEnd constructor

        :param database: DB name
        :param schema: DB Schema
        :param user: DB User
        :param password: DB User Password
        :param host: DB Hostname
        :param port: DB Port
        """
        self._con = mysql.connector.connect(database=database,
                                            user=user,
                                            password=password,
                                            host=host,
                                            port=port)

    def finalize(self, e=None):
        """
        Closes a DbBackEnd

        :return: None
        """
        print("Closing DB Connection.")
        if self.db_connection:
            self.db_connection.close()

    @property
    def db_connection(self):
        """
        DB Connection

        :return: Postgres DB API Connection
        """
        return self._con

    @property
    def get_cursor(self):
        """
        DB Cursor

        :return: Postgres DB API Cursor from connection
        """
        return self.db_connection.cursor()

    def get_table_list(self, blk_listed_table: str = "", schema: str = "public") -> list:
        """
        Return list of table name in DB

        :param blk_listed_table: Black Listed Table
        :param schema: DB Schema
        :return: List of Tables
        """
        black_listed = set()
        curs = self.get_cursor
        curs.execute("show tables")
        table_list = set(tuple_to_list(curs.fetchall()))
        for tbl in table_list:
            for blk_tbl in blk_listed_table.split(","):
                if len(blk_tbl.strip()) and blk_tbl in tbl:
                    black_listed.add(tbl)

        return list(table_list.difference(black_listed))

    def get_table_data(self, table: str, project_list: list, order_list: list, limit: int, offset: int = 0):
        """
        Fetch data for a table

        :param table: Table name
        :param project_list: List of columns to project
        :param order_list: List of columns to order data by
        :param limit: Max rows fetched
        :param offset: Row batch, where each batch will be of size 50 at least
        :return: List of rows
        """
        curs = self.get_cursor
        sql_qry = """
            SELECT {} FROM {} ORDER BY {} LIMIT {} OFFSET {}
            """.format(
                ",".join(project_list),
                table,
                ",".join(order_list),
                limit,
                offset
            )

        curs.execute(sql_qry)
        return curs.fetchall()

    def search_table_data(self, table: str, project_list: list, order_list: list,
                          search_con, limit: int, offset: int = 0):
        """
        Search data for a table

        :param table: Table name
        :param project_list: List of columns to project
        :param order_list: List of columns to order data by
        :param search_con: Searched Condition
        :param limit: Max rows fetched
        :param offset: Row batch, where each batch will be of size 50 at least
        :return: List of rows
        """
        curs = self.get_cursor
        sql_qry = """
            SELECT {} FROM {} WHERE {} ORDER BY {} LIMIT {} OFFSET {}
            """.format(
            ",".join(project_list),
            table,
            search_con,
            ",".join(order_list),
            limit,
            offset
        )

        curs.execute(sql_qry)
        return curs.fetchall()

    def get_table_columns(self, table: str, load_fk_data: bool = False) -> dict:
        """
        Column list for a table

        :param table: Table name
        :param load_fk_data: Whether to load FK column data for lookup
        :return: Metadata dictionary
        """
        meta_dict = dict()
        meta_dict["view"] = dict()
        meta_dict["insert"] = dict()
        meta_dict["fk_columns"] = dict()
        meta_dict["pk_columns"] = []
        curs = self.get_cursor

        # Get Column List
        curs.execute(
            SCT_QUERY_MYSQL_GET_COLMN_DETAIL.format(table)
        )
        for cd in curs.fetchall():
            col_nm = cd[0]
            meta_dict["view"][col_nm] = {
                "type": cd[1],
                "description": cd[8],
                "length": 0
            }
            if "PRI" in cd[4]:
                meta_dict["pk_columns"].append(col_nm)
            if "PRI" in cd[4] and cd[6] and "auto_increment" in cd[6]:
                pass
            elif cd[8] and "not updatable" in (str(cd[8])).lower():
                pass
            else:
                meta_dict["insert"][col_nm] = {
                    "type": cd[3],
                    "description": cd[2],
                    "length": cd[4]
                }

            # Get Table Foreign Keys
            curs.execute(SCT_QUERY_MYSQL_GET_FK_DETAIL.format(table))
            for fkd in curs.fetchall():
                meta_dict["fk_columns"][fkd[1]] = {
                    "table": fkd[3],
                    "column": fkd[4],
                    "data": []
                }

            if load_fk_data:
                for fk in meta_dict["fk_columns"]:
                    curs.execute(
                        SCT_QUERY_MYSQL_GET_FK_LOOKUP.format(
                            meta_dict["fk_columns"][fk].get("column"),
                            meta_dict["fk_columns"][fk].get("table")
                        )
                    )
                    meta_dict["fk_columns"][fk]["data"] = tuple_to_list(curs.fetchall())
        return meta_dict

    def get_table_info(self, table: str, batch: int = 1, page_size: int = 3) -> dict:
        """
        Table metadata

        :param table: Table name
        :param batch: Row batch, where each batch will be of size 50 at least
        :param page_size: Max record per page
        :return: Metadata dictionary
        """
        meta_dict = dict()
        curs = self.get_cursor

        # Get Column Details
        column_detail = self.get_table_columns(table, True)
        meta_dict["view_columns"] = column_detail["view"]
        meta_dict["insert_columns"] = column_detail["insert"]
        meta_dict["pk_columns"] = column_detail["pk_columns"]
        meta_dict["fk_columns"] = column_detail["fk_columns"]

        # Get Table Count
        curs.execute(
            """
            SELECT count(*) FROM {}
            """.format(table)
        )
        meta_dict["table_count"] = int(curs.fetchone()[0])

        # Get rows in batches of 50 records
        batch_num = (batch if 0 < batch < ceil(meta_dict["table_count"] / page_size) else
                     1 if batch < 1 else ceil(meta_dict["table_count"] / page_size))

        # Get table data
        table_data = self.get_table_data(table,
                                         meta_dict["view_columns"].keys(),
                                         meta_dict["pk_columns"],
                                         page_size,
                                         page_size * (batch_num - 1))
        meta_dict["table_data"] = tuple_to_dict([k for k in meta_dict["view_columns"].keys()], table_data)

        return meta_dict

    def search_table_info(self, table: str,
                          search_col, search_op, search_val, batch: int = 1, page_size: int = 3) -> dict:
        """
        Search metadata

        :param table: Table name
        :param search_col: Searched Table Column
        :param search_op: Search Operation
        :param search_val: Search Value
        :param batch: Row batch, where each batch will be of size 50 at least
        :param page_size: Max record per page
        :return: Metadata dictionary
        """
        meta_dict = dict()
        curs = self.get_cursor

        # Get Column Details
        column_detail = self.get_table_columns(table, True)
        meta_dict["view_columns"] = column_detail["view"]
        meta_dict["insert_columns"] = column_detail["insert"]
        meta_dict["pk_columns"] = column_detail["pk_columns"]
        meta_dict["fk_columns"] = column_detail["fk_columns"]

        # Search condition
        col_type = (str(meta_dict["view_columns"][search_col].get("type"))).lower()
        if search_op == 'like':
            if ("int" in col_type and "point" not in col_type) or ("double" in col_type or "numeric" in col_type):
                search_cond = "{} = {}".format(search_col, search_val)
            else:
                search_cond = "{} {} '%{}%'".format(search_col, search_op, search_val)
        else:
            if ("int" in col_type and "point" not in col_type) or ("double" in col_type or "numeric" in col_type):
                search_cond = "{} {} {}".format(search_col, search_op, search_val)
            else:
                search_cond = "{} {} '{}'".format(search_col, search_op, search_val)

        # Get Table Count
        if len(search_cond):
            search_qry = "SELECT count(*) FROM {} WHERE {}".format(table, search_cond)
        else:
            search_qry = "SELECT count(*) FROM {}".format(table)
        curs.execute(search_qry)
        meta_dict["table_count"] = int(curs.fetchone()[0])

        # Get rows in batches of 50 records
        batch_num = (batch if 0 < batch < ceil(meta_dict["table_count"] / page_size) else
                     1 if batch < 1 else ceil(meta_dict["table_count"] / page_size))

        # Get table data
        table_data = self.search_table_data(table,
                                            meta_dict["view_columns"].keys(),
                                            meta_dict["pk_columns"],
                                            search_cond,
                                            page_size,
                                            page_size * (batch_num - 1))
        meta_dict["table_data"] = tuple_to_dict([k for k in meta_dict["view_columns"].keys()], table_data)

        return meta_dict

    def add_table_record(self, table: str, **kwargs):
        """
        Add row to table

        :param table: Table name
        :param kwargs: List of column values of new record
        :return: None
        """
        # Query preparation
        table_details = self.get_table_columns(table)
        qry_args = []
        for col in table_details["insert"].keys():
            if (("int" in table_details["insert"][col]["type"] and
                 "point" not in table_details["insert"][col]["type"]) or
                    ("double" in table_details["insert"][col]["type"] or
                     "numeric" in table_details["insert"][col]["type"])):
                qry_args.append("{}".format(kwargs[col]))
            else:
                qry_args.append("'{}'".format(kwargs[col]))
        insert_qry = SCT_QUERY_MYSQL_INSERT_ROW.format(
            table,
            ",".join(table_details["insert"].keys()),
            ",".join(qry_args)
        )

        # Trigger insert
        curs = self.get_cursor
        curs.execute(insert_qry)
        self.db_connection.commit()

    def drop_table_record(self, table: str, **kwargs):
        """
        Drop row from table

        :param table: Table name
        :param kwargs: List of column values of new record
        :return: None
        """
        # Query preparation
        table_details = self.get_table_columns(table)
        qry_args = []

        if len(table_details["pk_columns"]):
            for col_nm in table_details["pk_columns"]:
                col_type = str(table_details["view"][col_nm]["type"])
                if (("int" in col_type and
                     "point" not in col_type) or
                        ("double" in col_type or
                         "numeric" in col_type)):
                    qry_args.append("{}={}".format(col_nm, kwargs[col_nm]))
                else:
                    qry_args.append("{}='{}'".format(col_nm, kwargs[col_nm]))
        else:
            for col_nm in table_details["view"].keys():
                col_type = str(table_details["view"][col_nm]["type"])
                if (("int" in col_type and
                     "point" not in col_type) or
                        ("double" in col_type or
                         "numeric" in col_type)):
                    qry_args.append("{}={}".format(col_nm, kwargs[col_nm]))
                else:
                    qry_args.append("{}='{}'".format(col_nm, kwargs[col_nm]))

        drop_qry = SCT_QUERY_MYSQL_DROP_ROW.format(
            table,
            " and ".join(qry_args)
        )

        # Trigger insert
        curs = self.get_cursor
        curs.execute(drop_qry)
        self.db_connection.commit()

    def edit_table_record(self, table: str, **kwargs):
        """
        Edit row to table

        :param table: Table name
        :param kwargs: List of column values of new record
        :return: None
        """
        # Query preparation
        table_details = self.get_table_columns(table)

        # Where Clause
        qry_args = []
        if len(table_details["pk_columns"]):
            for col_nm in table_details["pk_columns"]:
                if (("int" in table_details["view"][col_nm]["type"] and
                     "point" not in table_details["view"][col_nm]["type"]) or
                        ("double" in table_details["view"][col_nm]["type"] or
                         "numeric" in table_details["view"][col_nm]["type"])):
                    qry_args.append("{}={}".format(col_nm, kwargs[col_nm]))
                else:
                    qry_args.append("{}='{}'".format(col_nm, kwargs[col_nm]))
        else:
            return

        # Set Directive
        set_args = []
        for col in table_details["insert"].keys():
            if col not in table_details["pk_columns"]:
                if (("int" in table_details["insert"][col]["type"] and
                     "point" not in table_details["insert"][col]["type"]) or
                        ("double" in table_details["insert"][col]["type"] or
                         "numeric" in table_details["insert"][col]["type"])):
                    set_args.append("{}={}".format(col, kwargs[col]))
                else:
                    set_args.append("{}='{}'".format(col, kwargs[col]))

        edit_qry = SCT_QUERY_MYSQL_UPDATE_ROW.format(
            table,
            ", ".join(set_args),
            " and ".join(qry_args)
        )

        # Trigger insert
        curs = self.get_cursor
        curs.execute(edit_qry)
        self.db_connection.commit()

    def create_audit_table(self, audit_table: str):
        """
        Create a Audit table

        :param audit_table: Audit table name
        :return: None
        """
        curs = self.get_cursor
        query_str = SCT_QUERY_MYSQL_AUDIT_TABLE_CREATION.format(
            audit_table
        )

        curs.execute(query_str)
        self.db_connection.commit()

    def get_audits(self, audit_table: str, batch: int = 1, page_size: int = 3) -> dict:
        """
        Get Audits

        :param audit_table: Audit table name
        :param batch: Row batch, where each batch will be of size 50 at least
        :param page_size: Max record per page
        :return: Audit data
        """
        curs = self.get_cursor
        meta_dict = dict()

        # Get Table Count
        curs.execute(
            """
            SELECT count(*) FROM {}
            """.format(audit_table)
        )
        meta_dict["audits_count"] = int(curs.fetchone()[0])

        # Get rows in batches of 50 records
        batch_num = (batch if 0 < batch < ceil(meta_dict["audits_count"] / page_size) else
                     1 if batch < 1 else ceil(meta_dict["audits_count"] / page_size))

        adt_qry = SCT_QUERY_MYSQL_AUDIT_GET.format(audit_table, page_size, (batch_num - 1) * page_size)
        curs.execute(adt_qry)

        audit_columns = ["audit_user", "audit_time", "operation_performed",
                         "table_name", "operation_status", "operation_metadata"]
        meta_dict["audits_data"] = tuple_to_dict(audit_columns, curs.fetchall())

        return meta_dict

    def search_audits(self, audit_table: str, audit_search_col: str, audit_search_op: str, audit_search_val: str,
                      batch: int = 1, page_size: int = 3) -> dict:
        """
        Search Audits

        :param audit_table: Audit table name
        :param audit_search_col: Audit table search column name
        :param audit_search_op: Audit table search operator
        :param audit_search_val: Audit table search value
        :param batch: Row batch, where each batch will be of size 50 at least
        :param page_size: Max record per page
        :return: Audit data
        """
        curs = self.get_cursor
        meta_dict = dict()

        # Search condition
        if audit_search_op == 'like':
            if audit_search_col in ["audit_id"]:
                search_cond = "{} = {}".format(audit_search_col, audit_search_val)
            else:
                search_cond = "{} {} '%{}%'".format(audit_search_col, audit_search_op, audit_search_val)
        else:
            if audit_search_col in ["audit_id"]:
                search_cond = "{} {} {}".format(audit_search_col, audit_search_op, audit_search_val)
            else:
                search_cond = "{} {} '{}'".format(audit_search_col, audit_search_op, audit_search_val)

        # Get Table Count
        if len(search_cond):
            search_qry = "SELECT count(*) FROM {} WHERE {}".format(audit_table, search_cond)
        else:
            search_qry = "SELECT count(*) FROM {}".format(audit_table)
        curs.execute(search_qry)
        meta_dict["audits_count"] = int(curs.fetchone()[0])

        # Get rows in batches of 50 records
        batch_num = (batch if 0 < batch < ceil(meta_dict["audits_count"] / page_size) else
                     1 if batch < 1 else ceil(meta_dict["audits_count"] / page_size))

        if len(search_cond):
            adt_qry = SCT_QUERY_MYSQL_AUDIT_SEARCH.format(
                audit_table, search_cond, page_size, (batch_num - 1) * page_size)
        else:
            adt_qry = SCT_QUERY_MYSQL_AUDIT_GET.format(audit_table, page_size, (batch_num - 1) * page_size)
        curs.execute(adt_qry)

        audit_columns = ["audit_user", "audit_time", "operation_performed",
                         "table_name", "operation_status", "operation_metadata"]
        meta_dict["audits_data"] = tuple_to_dict(audit_columns, curs.fetchall())

        return meta_dict

    def add_audit(self, audit_table: str, status: str, audit_user: str, operation_performed: str,
                  table_name: str, operation_metadata: str):
        """
        Insert a Audit record

        :param audit_table: Audit table name
        :param status: Audit operation status
        :param audit_user: Audit user
        :param operation_performed: Audit operation
        :param table_name: Table impacted
        :param operation_metadata: Operation detail
        :return: None
        """
        curs = self.get_cursor
        query_str = SCT_QUERY_MYSQL_AUDIT_PUT.format(
            audit_table,
            audit_user if audit_user else "ANONYMOUS",
            operation_performed,
            table_name,
            status,
            json.dumps(operation_metadata)
        )

        curs.execute(query_str)
        self.db_connection.commit()

    def get_pending_bulk_loading(self, audit_table, max_failure):
        """
        List of files pending for processing

        :param audit_table: Audit table name
        :param max_failure: Max number of failure before we discard a file
        :return: dictionary with keys for table name and file to load
        """
        # Fetch data
        curs = self.get_cursor
        curs.execute(
            SCT_QUERY_MYSQL_AUDIT_BULK_LOAD.format(
                audit_table
            )
        )

        # Group data
        all_records = dict()
        for rec in curs.fetchall():
            table_name, file_name, action_name = (rec[0], json.loads(rec[2])["file_name"], rec[1])
            if table_name not in all_records:
                all_records[table_name] = dict()
            if file_name not in all_records[table_name]:
                all_records[table_name][file_name] = []
            (all_records[table_name][file_name]).append(action_name)

        # Filter out files that need to be considered
        result_dict = dict()
        for tbl in all_records.keys():
            for fl in all_records[tbl]:
                if ("SUCCESS" not in all_records[tbl][fl] and
                        len([st for st in all_records[tbl][fl] if st == "FAILED"]) <= int(max_failure)):
                    if tbl not in result_dict:
                        result_dict[tbl] = [fl]
                    else:
                        result_dict[tbl].append(fl)

        return result_dict

    def bulk_load_table_records(self, table: str, file_path: str):
        """
        Add row to table

        :param table: Table name
        :param file_path: File name to load table from
        :return: None
        """
        total_rec = 0
        curs = self.get_cursor
        table_details = self.get_table_columns(table)

        # Read in CSV
        with open(file_path, mode='r') as file:
            csv_file = csv.reader(file)
            column_list = []
            for i, row in enumerate(csv_file):
                if not i:
                    column_list = row
                else:
                    qry_args = []
                    for c, col in enumerate(column_list):
                        if (("int" in table_details["insert"][col]["type"] and
                             "point" not in table_details["insert"][col]["type"]) or
                                ("double" in table_details["insert"][col]["type"] or
                                 "numeric" in table_details["insert"][col]["type"])):
                            qry_args.append("{}".format(row[c]))
                        else:
                            qry_args.append("'{}'".format(row[c]))
                    insert_qry = SCT_QUERY_MYSQL_INSERT_ROW.format(
                        table,
                        ",".join(column_list),
                        ",".join(qry_args)
                    )

                    curs.execute(insert_qry)
                    total_rec = total_rec + 1

        self.db_connection.commit()
        return total_rec
