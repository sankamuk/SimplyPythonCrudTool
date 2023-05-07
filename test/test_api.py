import os
import pytest

from app.sct_app import init_sct_app
from app.utilities.sct_utils import tuple_to_list


class TestSCTAPI(object):
    """Test SCT API Module"""
    app = None
    client = None

    def setup_class(self):
        self.app = init_sct_app()
        curs = (self.app.config["SCT_DATA_DB"]).get_cursor
        with open("employee_setup_script_sqlite.sql") as sc:
            sql_sc = sc.read()
        curs.executescript(sql_sc)
        (self.app.config["SCT_DATA_DB"]).db_connection.commit()
        self.client = self.app.test_client()

    def teardown_class(self):
        (self.app.config["SCT_DATA_DB"]).finalize()
        (self.app.config["SCT_AUDIT_DB"]).finalize()

    @pytest.mark.skip
    def test_table_list(self):
        res = self.client.get('/api/tables')
        assert sorted(res.get_json()["tables"]) == ['companies', 'departments', 'employees']

    @pytest.mark.skip
    def test_table_columns(self):
        res = self.client.get('/api/table_columns/departments')
        assert sorted(list(res.get_json()["columns"].keys())) == ['department_id', 'department_type']

    @pytest.mark.skip
    def test_table_pk(self):
        res = self.client.get('/api/table_pk/departments')
        assert sorted(res.get_json()["columns"]) == ['department_id']

    @pytest.mark.skip
    def test_table_fk(self):
        res = self.client.get('/api/table_fk/employees')
        assert sorted(list(res.get_json()["columns"].keys())) == ['company', 'department']

    @pytest.mark.skip
    def test_table_insert_columns(self):
        res = self.client.get('/api/table_insert_columns/departments')
        assert sorted(res.get_json()["columns"]) == ['department_id', 'department_type']

    @pytest.mark.skip
    def test_table_create_row(self):
        res = self.client.get('/api/create_row/departments?department_id=IT_WK&department_type=Work%20Place')

        # Verify API response
        assert res.get_json()["record"] == {'department_id': 'IT_WK', 'department_type': 'Work Place'}
        # Verify from DB
        dpt_id_list = tuple_to_list(
            (self.app.config["SCT_DATA_DB"]).get_table_data("departments", ["department_id"], ["department_id"], 5, 0))
        assert "IT_WK" in dpt_id_list

    @pytest.mark.skip
    def test_table_delete_row(self):
        res = self.client.get('/api/delete_row/departments/1/1')

        # Verify API response
        assert res.get_json()["record"] == {'department_id': 'ENG_SW', 'department_type': 'Software Engineering'}
        # Verify from DB
        dpt_id_list = tuple_to_list(
            (self.app.config["SCT_DATA_DB"]).get_table_data("departments", ["department_id"], ["department_id"], 9, 0))
        assert "ENG_SW" not in dpt_id_list

    @pytest.mark.skip
    def test_table_edit_row(self):
        res = self.client.get('/api/edit_row/departments/1/2?department_type=Support')

        # Verify API response
        assert res.get_json()["record"] == {'department_id': 'IT_WK', 'department_type': 'Support'}
        # Verify from DB
        dpt_list = tuple_to_list(
            (self.app.config["SCT_DATA_DB"]).get_table_data("departments",
                                                            ["department_type"],
                                                            ["department_id"], 9, 0))
        assert "Support" in dpt_list
