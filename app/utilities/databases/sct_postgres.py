"""
    sct_db.py
    -------
    This module controls SCT Tool specific database interaction
"""
import json
import csv
import psycopg2
from math import ceil
from app.utilities.sct_utils import tuple_to_dict, tuple_to_list
from app.utilities.databases.sct_postgres_query import (
    SCT_QUERY_POSTGRES_GET_FK_DETAIL,
    SCT_QUERY_POSTGRES_GET_FK_LOOKUP,
    SCT_QUERY_POSTGRES_GET_COLMN_DETAIL,
    SCT_QUERY_POSTGRES_GET_PK_DETAIL,
    SCT_QUERY_POSTGRES_INSERT_ROW,
    SCT_QUERY_POSTGRES_DROP_ROW,
    SCT_QUERY_POSTGRES_UPDATE_ROW,
    SCT_QUERY_POSTGRES_AUDIT_GET,
    SCT_QUERY_POSTGRES_AUDIT_PUT,
    SCT_QUERY_POSTGRES_AUDIT_BULK_LOAD
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
                 user: str = "postgres",
                 password: str = "postgres",
                 host: str = "localhost",
                 port: str = "5432"):
        """
        DbBackEnd constructor

        :param database: DB name
        :param schema: DB Schema
        :param user: DB User
        :param password: DB User Password
        :param host: DB Hostname
        :param port: DB Port
        """
        self._con = psycopg2.connect(database=database,
                                     user=user,
                                     password=password,
                                     host=host,
                                     port=port,
                                     options="-c search_path={}".format(schema))

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
        curs.execute(
            """
            SELECT table_name FROM information_schema.tables WHERE table_schema = '{}'
            """.format(schema)
        )
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
        curs.execute(
            """
            SELECT {} FROM {} ORDER BY {} OFFSET {} LIMIT {}
            """.format(
                ",".join(project_list),
                table,
                ",".join(order_list),
                offset,
                limit
            )
        )
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
        curs = self.get_cursor

        # Get Table Primary Keys
        curs.execute(
            SCT_QUERY_POSTGRES_GET_PK_DETAIL.format(table)
        )
        meta_dict["pk_columns"] = [cd[0] for cd in curs.fetchall()]

        # Get Column List
        curs.execute(
            SCT_QUERY_POSTGRES_GET_COLMN_DETAIL.format(table)
        )
        for cd in curs.fetchall():
            col_nm = cd[1]
            meta_dict["view"][col_nm] = {
                "type": cd[3],
                "description": cd[2],
                "length": cd[4]
            }
            if col_nm in meta_dict["pk_columns"] and cd[5] and "nextval" in cd[5]:
                # print("Primary key auto-generate column {}".format(col_nm))
                pass
            elif cd[2] and "not updatable" in (cd[2]).lower():
                # print("Non updatable column {}".format(col_nm))
                pass
            else:
                meta_dict["insert"][col_nm] = {
                    "type": cd[3],
                    "description": cd[2],
                    "length": cd[4]
                }

            # Get Table Foreign Keys
            curs.execute(SCT_QUERY_POSTGRES_GET_FK_DETAIL)
            for fkd in curs.fetchall():
                if fkd[2] == table:
                    meta_dict["fk_columns"][fkd[3]] = {
                        "table": fkd[4],
                        "column": fkd[5],
                        "data": []
                    }
            if load_fk_data:
                for fk in meta_dict["fk_columns"]:
                    curs.execute(
                        SCT_QUERY_POSTGRES_GET_FK_LOOKUP.format(
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
                                         (batch_num - 1) * page_size)
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
        insert_qry = SCT_QUERY_POSTGRES_INSERT_ROW.format(
            table,
            ",".join(table_details["insert"].keys()),
            ",".join(qry_args)
        )
        print(insert_qry)

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
                if (("int" in table_details["view"][col_nm]["type"] and
                     "point" not in table_details["view"][col_nm]["type"]) or
                        ("double" in table_details["view"][col_nm]["type"] or
                         "numeric" in table_details["view"][col_nm]["type"])):
                    qry_args.append("{}={}".format(col_nm, kwargs[col_nm]))
                else:
                    qry_args.append("{}='{}'".format(col_nm, kwargs[col_nm]))
        else:
            for col_nm in table_details["view"].keys():
                if (("int" in table_details["view"][col_nm]["type"] and
                     "point" not in table_details["view"][col_nm]["type"]) or
                        ("double" in table_details["view"][col_nm]["type"] or
                         "numeric" in table_details["view"][col_nm]["type"])):
                    qry_args.append("{}={}".format(col_nm, kwargs[col_nm]))
                else:
                    qry_args.append("{}='{}'".format(col_nm, kwargs[col_nm]))

        drop_qry = SCT_QUERY_POSTGRES_DROP_ROW.format(
            table,
            " and ".join(qry_args)
        )
        print(drop_qry)

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

        edit_qry = SCT_QUERY_POSTGRES_UPDATE_ROW.format(
            table,
            ", ".join(set_args),
            " and ".join(qry_args)
        )
        print(edit_qry)

        # Trigger insert
        curs = self.get_cursor
        curs.execute(edit_qry)
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

        adt_qry = SCT_QUERY_POSTGRES_AUDIT_GET.format(audit_table, (batch_num - 1) * page_size, page_size)
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
        query_str = SCT_QUERY_POSTGRES_AUDIT_PUT.format(
                audit_table,
                audit_user if audit_user else "ANONYMOUS",
                operation_performed,
                table_name,
                status,
                json.dumps(operation_metadata)
            )
        print(query_str)
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
            SCT_QUERY_POSTGRES_AUDIT_BULK_LOAD.format(
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
        with open(file_path, mode='r')as file:
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
                    insert_qry = SCT_QUERY_POSTGRES_INSERT_ROW.format(
                        table,
                        ",".join(column_list),
                        ",".join(qry_args)
                    )
                    print(insert_qry)
                    curs.execute(insert_qry)
                    total_rec = total_rec + 1

        self.db_connection.commit()
        return total_rec
