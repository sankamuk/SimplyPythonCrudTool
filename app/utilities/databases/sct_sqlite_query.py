"""
    sct_sqlite_query.py
    -------
    This module consists of SQLite Queries
"""

SCT_QUERY_GET_COLUMN_DETAIL = """
PRAGMA table_info({}); 
"""

SCT_QUERY_GET_AUTO_COLUMN_DETAIL = """
WITH RECURSIVE
  a AS (
    SELECT name, lower(replace(replace(sql, char(13), ' '), char(10), ' ')) AS sql
    FROM sqlite_master
    WHERE lower(sql) LIKE '%integer% autoincrement%'
  ),
  b AS (
    SELECT name, trim(substr(sql, instr(sql, '(') + 1)) AS sql
    FROM a
  ),
  c AS (
    SELECT b.name, sql, '' AS col
    FROM b
    UNION ALL
    SELECT 
      c.name, 
      trim(substr(c.sql, ifnull(nullif(instr(c.sql, ','), 0), instr(c.sql, ')')) + 1)) AS sql, 
      trim(substr(c.sql, 1, ifnull(nullif(instr(c.sql, ','), 0), instr(c.sql, ')')) - 1)) AS col
    FROM c JOIN b ON c.name = b.name
    WHERE c.sql != ''
  ),
  d AS (
    SELECT name, substr(col, 1, instr(col, ' ') - 1) AS col
    FROM c
    WHERE col LIKE '%autoincrement%'
  )
SELECT name, col  
FROM d
ORDER BY name, col;
"""

SCT_QUERY_GET_PK_DETAIL = """
PRAGMA table_info({}) 
"""

SCT_QUERY_GET_FK_DETAIL = """
PRAGMA foreign_key_list({});
"""

SCT_QUERY_GET_FK_LOOKUP = """
SELECT DISTINCT {} FROM {}
"""

SCT_QUERY_INSERT_ROW = """
INSERT INTO {}({}) VALUES({})
"""

SCT_QUERY_DROP_ROW = """
DELETE FROM {} WHERE {}
"""

SCT_QUERY_UPDATE_ROW = """
UPDATE {} SET {} WHERE {}
"""

SCT_QUERY_AUDIT_GET = """
SELECT audit_user, audit_time, operation_performed, table_name, operation_status, operation_metadata FROM {}
ORDER BY audit_id LIMIT {},{}
"""

SCT_QUERY_AUDIT_SEARCH = """
SELECT audit_user, audit_time, operation_performed, table_name, operation_status, operation_metadata FROM {}
WHERE {}
ORDER BY audit_id LIMIT {},{}
"""

SCT_QUERY_AUDIT_PUT = """
INSERT INTO {0}(operation_performed, table_name, operation_status, audit_user, operation_metadata) VALUES (
    '{1}', '{2}', '{3}', '{4}', '{5}'
)
"""

SCT_QUERY_AUDIT_BULK_LOAD = """
SELECT table_name, operation_status, operation_metadata FROM {} WHERE operation_performed = 'BULK_UPLOAD'
"""

SCT_QUERY_GET_PAGINATE_DATA = """
SELECT {} FROM {} ORDER BY {} LIMIT {},{}
"""

SCT_QUERY_GET_TABLE_LIST = """
SELECT name FROM sqlite_master WHERE type='table'
"""

SCT_QUERY_AUDIT_TABLE_CREATION = """
create table IF NOT EXISTS sct_audits (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    audit_user VARCHAR (100) not null,
    audit_time timestamp NOT NULL DEFAULT current_timestamp,
    operation_performed VARCHAR (100) not null,
    table_name VARCHAR (100) not null,
    operation_status VARCHAR (15) not null,
    operation_metadata VARCHAR (5000)
);
"""