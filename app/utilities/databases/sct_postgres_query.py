"""
    sct_postgres_query.py
    -------
    This module consists of Postgres Queries
"""

SCT_QUERY_GET_TABLE_LIST = """
SELECT table_name FROM information_schema.tables WHERE table_schema = '{}'
"""

SCT_QUERY_GET_PAGINATE_DATA = """
SELECT {} FROM {} ORDER BY {} OFFSET {} LIMIT {}
"""

SCT_QUERY_GET_COLUMN_DETAIL = """
select st.relname as TableName, c.column_name, pgd.description, c.data_type, 
            c.character_maximum_length, c.column_default
            from pg_catalog.pg_statio_all_tables as st
            inner join information_schema.columns c
            on c.table_schema = st.schemaname
            and c.table_name = st.relname
            left join pg_catalog.pg_description pgd
            on pgd.objoid=st.relid
            and pgd.objsubid=c.ordinal_position
            where st.relname = '{}'
"""

SCT_QUERY_GET_PK_DETAIL = """
SELECT c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
            JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
              AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
            WHERE constraint_type = 'PRIMARY KEY' and tc.table_name = '{}'
"""

SCT_QUERY_GET_FK_DETAIL = """
            WITH unnested_confkey AS (
              SELECT oid, unnest(confkey) as confkey
              FROM pg_constraint
            ),
            unnested_conkey AS (
              SELECT oid, unnest(conkey) as conkey
              FROM pg_constraint
            )
            select
              c.conname                   AS constraint_name,
              c.contype                   AS constraint_type,
              tbl.relname                 AS constraint_table,
              col.attname                 AS constraint_column,
              referenced_tbl.relname      AS referenced_table,
              referenced_field.attname    AS referenced_column,
              pg_get_constraintdef(c.oid) AS definition
            FROM pg_constraint c
            LEFT JOIN unnested_conkey con ON c.oid = con.oid
            LEFT JOIN pg_class tbl ON tbl.oid = c.conrelid
            LEFT JOIN pg_attribute col ON (col.attrelid = tbl.oid AND col.attnum = con.conkey)
            LEFT JOIN pg_class referenced_tbl ON c.confrelid = referenced_tbl.oid
            LEFT JOIN unnested_confkey conf ON c.oid = conf.oid
            LEFT JOIN pg_attribute referenced_field ON (referenced_field.attrelid = c.confrelid 
            AND referenced_field.attnum = conf.confkey)
            WHERE c.contype = 'f';
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

SCT_QUERY_AUDIT_TABLE_CREATION = """
create table {} (
    audit_id serial PRIMARY KEY,
    audit_user VARCHAR (100) not null,
    audit_time timestamp NOT NULL DEFAULT NOW(),
    operation_performed VARCHAR (100) not null,
    table_name VARCHAR (100) not null,
    operation_status VARCHAR (15) not null,
    operation_metadata VARCHAR (5000)
)
"""

SCT_QUERY_AUDIT_GET = """
SELECT audit_user, audit_time, operation_performed, table_name, operation_status, operation_metadata FROM {}
ORDER BY audit_id OFFSET {} LIMIT {}
"""

SCT_QUERY_AUDIT_PUT = """
INSERT INTO {0}(operation_performed, table_name, operation_status, audit_user, operation_metadata) VALUES (
    '{1}', '{2}', '{3}', '{4}', '{5}'
)
"""

SCT_QUERY_AUDIT_BULK_LOAD = """
SELECT table_name, operation_status, operation_metadata FROM {} WHERE operation_performed = 'BULK_UPLOAD'
"""