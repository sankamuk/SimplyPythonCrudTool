"""
    sct_db.py
    -------
    This module controls backend database interaction
"""
import psycopg2
from math import ceil
from sct_utils import tuple_to_dict, tuple_to_list
from sct_query import (
    SCT_QUERY_POSTGRES_GET_FK_DETAIL,
    SCT_QUERY_POSTGRES_GET_FK_LOOKUP,
    SCT_QUERY_POSTGRES_GET_COLMN_DETAIL,
    SCT_QUERY_POSTGRES_GET_PK_DETAIL,
    SCT_QUERY_POSTGRES_INSERT_ROW,
    SCT_QUERY_POSTGRES_DROP_ROW
)


class DbBackEnd:
    """
        Backend Database Interface.
        .. admonition:: Note
            Defines all DB Communication codes.
    """

    def __init__(self,
                 database: str = "default",
                 user: str = "postgres",
                 password: str = "postgres",
                 host: str = "localhost",
                 port: str = "5432"):
        """
        DbBackEnd constructor

        :param database: DB name
        :param user: DB User
        :param password: DB User Password
        :param host: DB Hostname
        :param port: DB Port
        """
        self._con = psycopg2.connect(database=database,
                                     user=user,
                                     password=password,
                                     host=host,
                                     port=port)

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

    def get_table_list(self) -> list:
        """
        Return list of table name in DB

        :return: List of Tables
        """
        curs = self.get_cursor
        curs.execute(
            """
            SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
            """
        )
        return tuple_to_list(curs.fetchall())

    def get_table_columns(self, table: str) -> dict:
        """
        Column list for a table

        :param table: Table name
        :return: Metadata dictionary
        """
        meta_dict = dict()
        meta_dict["view"] = dict()
        meta_dict["insert"] = dict()
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
                print("Primary key auto-generate column {}".format(col_nm))
            elif cd[2] and "not updatable" in cd[2]:
                print("Non updatable column {}".format(col_nm))
            else:
                meta_dict["insert"][col_nm] = {
                    "type": cd[3],
                    "description": cd[2],
                    "length": cd[4]
                }
        return meta_dict

    def get_table_info(self, table: str, batch: int = 1) -> dict:
        """
        Table metadata

        :param table: Table name
        :param batch: Row batch, where each batch will be of size 50 at least
        :return: Metadata dictionary
        """
        meta_dict = dict()
        curs = self.get_cursor

        # Get Column Details
        column_detail = self.get_table_columns(table)
        meta_dict["view_columns"] = column_detail["view"]
        meta_dict["insert_columns"] = column_detail["insert"]
        meta_dict["pk_columns"] = column_detail["pk_columns"]

        # Get Table Count
        curs.execute(
            """
            SELECT count(*) FROM public.{}
            """.format(table)
        )
        meta_dict["table_count"] = int(curs.fetchone()[0])

        # Get rows in batches of 50 records
        batch_num = (batch if 0 < batch < ceil(meta_dict["table_count"] / 3) else
                     1 if batch < 1 else ceil(meta_dict["table_count"] / 3))

        curs.execute(
            """
            SELECT {} FROM public.{} ORDER BY {} OFFSET {} LIMIT {}
            """.format(
                ",".join(meta_dict["view_columns"].keys()),
                table,
                ",".join(meta_dict["pk_columns"]),
                (batch_num - 1) * 3,
                3
            )
        )
        meta_dict["table_data"] = tuple_to_dict([k for k in meta_dict["view_columns"].keys()], curs.fetchall())

        # Get Table Foreign Keys
        meta_dict["fk_columns"] = dict()
        curs.execute(SCT_QUERY_POSTGRES_GET_FK_DETAIL)
        for fkd in curs.fetchall():
            if fkd[2] == table:
                meta_dict["fk_columns"][fkd[3]] = {
                    "table": fkd[4],
                    "column": fkd[5],
                    "data": []
                }
        for fk in meta_dict["fk_columns"]:
            curs.execute(
                SCT_QUERY_POSTGRES_GET_FK_LOOKUP.format(
                    meta_dict["fk_columns"][fk].get("column"),
                    meta_dict["fk_columns"][fk].get("table")
                )
            )
            meta_dict["fk_columns"][fk]["data"] = tuple_to_list(curs.fetchall())

        return meta_dict

    def add_table_record(self, table: str, **kwargs):
        """
        Append to table

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
        Append to table

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

        # Trigger insert
        curs = self.get_cursor
        curs.execute(drop_qry)
        self.db_connection.commit()
