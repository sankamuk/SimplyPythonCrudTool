import pytest
import tempfile

from app.utilities.sct_utils import tuple_to_list
from app.utilities.databases.sct_sqlite import DbBackEnd
from app.utilities.sct_env import *
from app.utilities.databases.sct_sqlite_query import (
    SCT_QUERY_GET_TABLE_LIST
)


class TestSCTDB(object):
    """Test SCT DB Module"""
    db = None

    def setup_class(self):
        self.db = DbBackEnd(database=":memory:")
        curs = self.db.get_cursor
        with open("employee_setup_script_sqlite.sql") as sc:
            sql_sc = sc.read()
        curs.executescript(sql_sc)
        self.db.db_connection.commit()

    def teardown_class(self):
        self.db.finalize()

    @pytest.mark.skip
    def test_table_list(self):
        table_list = self.db.get_table_list(blk_listed_table=sct_table_table_blacklist)

        assert sorted(table_list) == ["companies", "departments", "employees"]

    @pytest.mark.skip
    def test_table_pk(self):
        assert self.db.get_table_pk("companies") == {'columns': ['company_id']}

    @pytest.mark.skip
    def test_table_fk(self):
        expected_result = {
            'columns': {'company': {'table': 'companies', 'column': 'company_id'},
                        'department': {'table': 'departments', 'column': 'department_id'}
                        }}
        assert self.db.get_table_fk("employees") == expected_result

    @pytest.mark.skip
    def test_table_columns(self):
        dept_col = self.db.get_table_columns("departments")["columns"]
        # assert list(dept_col.keys()) == ["department_id", "department_type"]

    @pytest.mark.skip
    def test_table_insert_columns(self):
        emp_col = self.db.get_table_insert_columns("employees")["columns"]
        assert sorted(emp_col) == ['birth_day', 'company', 'department', 'dob', 'email', 'name']

    @pytest.mark.skip
    def test_table_data(self):
        assert self.db.get_table_data("employees", ["employee_id", "name"], ["employee_id"], 1, 3) == [(4, 'dab')]

    @pytest.mark.skip
    def test_table_fk_lookup_data(self):
        lookup_data = self.db.get_fk_lookup_data("employees")
        assert lookup_data["columns"]["company"]["data"] == ['ACN_KOL', 'IBM_KOL', 'TCS_BNG']
        assert lookup_data["columns"]["department"]["data"] == ['ENG_HWD', 'ENG_SW', 'HR', 'MGMT']

    @pytest.mark.skip
    def test_add_table_record(self):
        record = {
            "department_id": "IT_WK",
            "department_type": "Work Place"
        }
        self.db.add_table_record("departments", **record)
        dpt_id_list = tuple_to_list(self.db.get_table_data("departments", ["department_id"], ["department_id"], 5, 0))

        assert "IT_WK" in dpt_id_list

    @pytest.mark.skip
    def test_drop_table_record(self):
        record = {
            "department_id": "HR"
        }
        self.db.drop_table_record("departments", **record)
        dpt_id_list = tuple_to_list(self.db.get_table_data("departments", ["department_id"], ["department_id"], 5, 0))

        assert "HR" not in dpt_id_list

    @pytest.mark.skip
    def test_edit_table_record(self):
        record = {
            "department_id": "MGMT",
            "department_type": "Management"
        }
        self.db.edit_table_record("departments", **record)
        dpt_list = tuple_to_list(self.db.get_table_data("departments", ["department_type"], ["department_id"], 5, 0))

        assert "Management" in dpt_list
        assert "Manager" not in dpt_list

    @pytest.mark.skip
    def test_audit_table_creation(self):
        self.db.create_audit_table(sct_audit_db_table)
        table_list = self.db.get_table_list(blk_listed_table="")

        assert sct_audit_db_table in table_list

    @pytest.mark.skip
    def test_audit_table_insert(self):

        self.db.add_audit(sct_audit_db_table, "DUMMY", "READ_TABLE", "departments", "SUCCESS", {})
        expected_result = [("SUCCESS", "DUMMY", "READ_TABLE", "departments")]

        assert self.db.get_table_data(sct_audit_db_table,
                                      ["operation_status", "audit_user", "operation_performed", "table_name"],
                                      ["audit_id"], 1, 0) == expected_result

    @pytest.mark.skip
    def test_audit_table_date(self):
        assert self.db.get_audits(sct_audit_db_table, 1, 5)["audits_count"] == 1

    @pytest.mark.skip
    def test_pending_bulk_loading(self):

        self.db.add_audit(sct_audit_db_table, "DUMMY", "BULK_UPLOAD", "departments", "UPLOADED",
                          {"file_name": "DUMMY"})
        result = self.db.get_pending_bulk_loading(sct_audit_db_table, 3)

        assert result["departments"] == ["DUMMY"]

    @pytest.mark.skip
    def test_bulk_load_table(self):
        temp_fl = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)

        with open(temp_fl.name, 'w') as f:
            f.write("department_id,department_type\n")
            f.write("NO_OP,No Operations")

        self.db.bulk_load_table_records("departments", temp_fl.name)

        dpt_id_list = tuple_to_list(self.db.get_table_data("departments", ["department_id"], ["department_id"], 5, 0))

        assert "NO_OP" in dpt_id_list

        temp_fl.close()
