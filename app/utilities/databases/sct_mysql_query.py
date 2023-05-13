"""
    sct_mysql_query.py
    -------
    This module consists of MySQL Queries
"""

SCT_QUERY_MYSQL_GET_COLMN_DETAIL = """
SHOW FULL COLUMNS FROM {}
"""

SCT_QUERY_MYSQL_GET_PK_DETAIL = """
SHOW FULL COLUMNS FROM {}
"""

SCT_QUERY_MYSQL_GET_FK_DETAIL = """
SELECT
  TABLE_NAME,
  COLUMN_NAME,
  CONSTRAINT_NAME,
  REFERENCED_TABLE_NAME,
  REFERENCED_COLUMN_NAME
FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
WHERE
  TABLE_NAME = '{}' AND 
  REFERENCED_TABLE_NAME IS NOT NULL ;
"""

SCT_QUERY_MYSQL_GET_FK_LOOKUP = """
SELECT DISTINCT {} FROM {}
"""

SCT_QUERY_MYSQL_INSERT_ROW = """
INSERT INTO {}({}) VALUES({})
"""

SCT_QUERY_MYSQL_DROP_ROW = """
DELETE FROM {} WHERE {}
"""

SCT_QUERY_MYSQL_UPDATE_ROW = """
UPDATE {} SET {} WHERE {}
"""

SCT_QUERY_MYSQL_AUDIT_GET = """
SELECT audit_user, audit_time, operation_performed, table_name, operation_status, operation_metadata FROM {}
ORDER BY audit_id LIMIT {} OFFSET {}
"""

SCT_QUERY_MYSQL_AUDIT_PUT = """
INSERT INTO {0}(operation_performed, table_name, operation_status, audit_user, operation_metadata) VALUES (
    '{1}', '{2}', '{3}', '{4}', '{5}'
)
"""

SCT_QUERY_MYSQL_AUDIT_BULK_LOAD = """
SELECT table_name, operation_status, operation_metadata FROM {} WHERE operation_performed = 'BULK_UPLOAD'
"""

SCT_QUERY_MYSQL_AUDIT_TABLE_CREATION = """
create table if not exists sct_audits (
        audit_id int NOT NULL AUTO_INCREMENT primary key,
        audit_user VARCHAR (100) not null,
        audit_time timestamp NOT NULL DEFAULT NOW(),
        operation_performed VARCHAR (100) not null,
        table_name VARCHAR (100) not null,
        operation_status VARCHAR (15) not null,
        operation_metadata VARCHAR (5000)
);
"""

SCT_QUERY_MYSQL_AUDIT_SEARCH = """
SELECT audit_user, audit_time, operation_performed, table_name, operation_status, operation_metadata FROM {}
WHERE {}
ORDER BY audit_id LIMIT {} OFFSET {}
"""