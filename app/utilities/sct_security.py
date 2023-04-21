import logging
import base64
import hashlib
import requests
import secrets
from flask_login import (
    login_user,
    logout_user,
)
from flask import request, session, redirect, url_for
from app.utilities.sct_user import User
from app.utilities.sct_env import *


def define_security(app, login_manager):
    """
    Application Security

    :param app: Flask application object
    :param login_manager: Database Interface Object <DbBackEnd>
    :return: None
    """

    config = {
        "auth_uri": "https://{}/oauth2/default/v1/authorize".format(sct_auth_okta_domain),
        "client_id": sct_auth_okta_client_id,
        "client_secret": sct_auth_okta_client_secret,
        "redirect_uri": "http://localhost:5000/authorization-code/callback",
        "issuer": "https://{}/oauth2/default".format(sct_auth_okta_domain),
        "token_uri": "https://{}/oauth2/default/v1/token".format(sct_auth_okta_domain),
        "userinfo_uri": "https://{}/oauth2/default/v1/userinfo".format(sct_auth_okta_domain)
    }

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    @app.route("/login")
    def login():
        # store app state and code verifier in session
        session['app_state'] = secrets.token_urlsafe(64)
        session['code_verifier'] = secrets.token_urlsafe(64)

        # calculate code challenge
        hashed = hashlib.sha256(session['code_verifier'].encode('ascii')).digest()
        encoded = base64.urlsafe_b64encode(hashed)
        code_challenge = encoded.decode('ascii').strip('=')

        # get request params
        query_params = {'client_id': config["client_id"],
                        'redirect_uri': config["redirect_uri"],
                        'scope': "openid email profile",
                        'state': session['app_state'],
                        'code_challenge': code_challenge,
                        'code_challenge_method': 'S256',
                        'response_type': 'code',
                        'response_mode': 'query'}

        # build request_uri
        request_uri = "{base_url}?{query_params}".format(
            base_url=config["auth_uri"],
            query_params=requests.compat.urlencode(query_params)
        )

        return redirect(request_uri)

    @app.route("/authorization-code/callback")
    def callback():
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        code = request.args.get("code")
        app_state = request.args.get("state")
        if app_state != session['app_state']:
            return "The app state does not match"
        if not code:
            return "The code was not returned or is not accessible", 403
        query_params = {'grant_type': 'authorization_code',
                        'code': code,
                        'redirect_uri': request.base_url,
                        'code_verifier': session['code_verifier'],
                        }
        query_params = requests.compat.urlencode(query_params)
        exchange = requests.post(
            config["token_uri"],
            headers=headers,
            data=query_params,
            auth=(config["client_id"], config["client_secret"]),
        ).json()

        # Get tokens and validate
        if not exchange.get("token_type"):
            return "Unsupported token type. Should be 'Bearer'.", 403
        access_token = exchange["access_token"]
        id_token = exchange["id_token"]

        # Authorization flow successful, get userinfo and login user
        userinfo_response = requests.get(config["userinfo_uri"],
                                         headers={'Authorization': f'Bearer {access_token}'}).json()

        unique_id = userinfo_response["sub"]
        user_email = userinfo_response["email"]
        user_name = userinfo_response["given_name"]

        user = User(
            id_=unique_id, name=user_name, email=user_email
        )

        if not User.get(unique_id):
            User.create(unique_id, user_name, user_email)

        login_user(user)

        return redirect(url_for("data"))

    @app.route("/logout", methods=["GET", "POST"])
    def logout():
        logout_user()
        return redirect(url_for("login"))


def get_user_role(user):
    """
    Return the role for a given user

    :param user: User email
    :return: Role
    """
    logging.info("User: {}".format(user))
    if not user:
        return sct_access_anonymous
    else:
        if "*" in sct_access_admin or user in sct_access_admin.split(","):
            return "ADMIN"
        elif "*" in sct_access_operator or user in sct_access_operator.split(","):
            return "OPERATOR"
        elif "*" in sct_access_viewer or user in sct_access_viewer.split(","):
            return "VIEWER"
        else:
            return "NONE"

