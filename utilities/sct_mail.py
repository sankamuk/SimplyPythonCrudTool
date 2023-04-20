"""
    sct_mail.py
    -------
    This module consists of mail utilities
"""
from flask_mail import Mail, Message
from jinja2 import Environment

from utilities.sct_env import *

SCT_EMAIL_TEMPLATE_REGISTER = """
<body>
    <h2><center><b>Simple Python CRUD Tool (SCT) Notification</b></center></h2>
    <br/>
    <table style="width:80%"  border="0"  align="center"><tr><th align="left">Details</th></tr></table>
    <br/>
    <table style="width:80%"  border="1" align="center">
        <tr>
            <th colspan="3" align="center" bgcolor="AFBCBE">Action</th><td>Register New User</td>
        </tr>
        <tr style="border: 1px solid black; border-collapse: collapse;">
            <th colspan="3" align="center" bgcolor="AFBCBE">User</th><td>{{ user_name }}</td>
        </tr>
        <tr>
            <th colspan="3" align="center" bgcolor="AFBCBE">Email</th><td>{{ user_email }}</td>
        </tr>
        <tr>
            <th colspan="3" align="center" bgcolor="AFBCBE">Access</th><td>{{ user_permission }}</td>
        </tr>
    </table>
    <br/>
    <table style="width:80%"  border="0"  align="center"><tr><th align="left">Thanks, SCT Admin</th></tr></table>  
    <br/>
    <p><center><small>This is a system generated email, please do not respond.</small></center></p>
</body>
"""

SCT_EMAIL_TEMPLATE_SUCCESS = """
<body>
    <h2><center><b>Simple Python CRUD Tool (SCT) Notification</b></center></h2>
    <br/>
    <table style="width:80%"  border="0"  align="center"><tr><th align="left">Details</th></tr></table>
    <br/>
    <table style="width:80%"  border="1" align="center">
        <tr>
            <th colspan="3" align="center" bgcolor="AFBCBE">Action</th><td>{{ job_type }}</td>
        </tr>
        <tr style="border: 1px solid black; border-collapse: collapse;">
            <th colspan="3" align="center" bgcolor="AFBCBE">Status</th><td>{{ job_status }}</td>
        </tr>
        <tr>
            <th colspan="3" align="center" bgcolor="AFBCBE">Table</th><td>{{ job_table }}</td>
        </tr>
        <tr>
            <th colspan="3" align="center" bgcolor="AFBCBE">Time</th><td>{{ job_time }}</td>
        </tr>
        <tr>
            <th colspan="3" align="center" bgcolor="AFBCBE">User</th><td>{{ job_user }}</td>
        </tr>
        <tr>
            <th colspan="3" align="center" bgcolor="AFBCBE">Metadata</th><td>{{ job_meta }}</td>
        </tr>
    </table>
    <br/>
    <table style="width:80%"  border="0"  align="center"><tr><th align="left">Thanks, SCT Admin</th></tr></table>  
    <br/>
    <p><center><small>This is a system generated email, please do not respond.</small></center></p>
</body>
"""

SCT_EMAIL_TEMPLATE_FAILURE = SCT_EMAIL_TEMPLATE_SUCCESS


def enable_email_support(app):
    """
    Mail support

    :param app: Application instance
    :return: None
    """
    app.config["MAIL_SERVER"] = sct_mail_server
    app.config["MAIL_PORT"] = sct_mail_port
    app.config["MAIL_USE_TLS"] = bool(sct_mail_use_tls)
    app.config["MAIL_USE_SSL"] = bool(sct_mail_use_ssl)
    app.config["MAIL_USERNAME"] = sct_mail_user
    app.config["MAIL_PASSWORD"] = sct_mail_password
    app.config["MAIL_DEFAULT_SENDER"] = sct_mail_user
    mail = Mail(app)
    app.config["SCT_MAIL"] = mail


def send_mail(app, **kwargs):
    """
    Send email

    :param app: Application instance
    :param kwargs: Mail argument
    :return: None
    """
    if bool(sct_mail_enabled):
        env = Environment()
        if kwargs["mail_type"] == "job":
            mssg = Message("SCT - Notification - {}".format(kwargs["operation_status"]),
                           recipients=sct_mail_recipients.split(","))
            template = env.from_string(SCT_EMAIL_TEMPLATE_SUCCESS)
            mssg.html = template.render(
                job_type=kwargs["operation_performed"],
                job_table=kwargs["table_name"],
                job_user=kwargs["audit_user"],
                job_time=kwargs["audit_time"],
                job_status=kwargs["operation_status"],
                job_meta=kwargs["operation_metadata"]
            )
            (app.config["SCT_MAIL"]).send(mssg)
        elif kwargs["mail_type"] == "register":
            recipients_list = sct_mail_recipients.split(",")
            recipients_list.append(kwargs["user_email"])
            mssg = Message("SCT - Notification - Registration",
                           recipients=recipients_list)
            template = env.from_string(SCT_EMAIL_TEMPLATE_REGISTER)
            mssg.html = template.render(
                user_name=kwargs["user_name"],
                user_email=kwargs["user_email"],
                user_permission=kwargs["user_permission"],
            )
            (app.config["SCT_MAIL"]).send(mssg)
        else:
            app.log.warn("Unknown mail type.")
    else:
        app.log.warn("Mail not enabled thus no action will be taken.")
