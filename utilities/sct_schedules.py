"""
    sct_schedules.py
    -------
    This module consists of schedule tasks
"""
import datetime
import json
import os
from utilities.sct_env import *
from utilities.sct_mail import send_mail


def sct_scheduled_bulk_loader(app, db):
    """
    SCT Tool Scheduled Tasks

    :param app: Application instance
    :param db: Database Interface Object <DbBackEnd>
    :return: None
    """
    app.logger.info("Scheduled Job (sct_scheduled_bulk_loader) started")
    pending_files = db.get_pending_bulk_loading(sct_audit_db_table, sct_scheduler_job_max_attempt)
    app.logger.info("List of pending files to be processed are - {}".format(pending_files))
    table_list = []
    metadata_dict = []
    for tb in pending_files.keys():
        for fl in pending_files[tb]:
            table_list.append(tb)
            app_root = os.path.dirname(app.instance_path)
            rec_inserted = db.bulk_load_table_records(tb, os.path.join(app_root, 'static', 'uploads', fl))
            app.logger.info("Total record inserted in {} table with file {} is {}".format(tb, fl, rec_inserted))
            db.add_audit(sct_audit_db_table, 'SYSTEM', "BULK_UPLOAD", tb, "SUCCESS", {
                "file_name": fl,
                "total_record_inserted": rec_inserted
            })
            metadata_dict.append({
                "table": tb,
                "file_name": fl,
                "total_record_inserted": rec_inserted
            })

    send_mail(app,
              operation_performed="BULK_UPLOAD",
              table_name=",".join(table_list),
              audit_user="SYSTEM",
              audit_time=datetime.datetime.now().strftime("%d %B, %Y %H:%M:%S (%A)"),
              operation_status="SUCCESS",
              operation_metadata=json.dumps(metadata_dict))
