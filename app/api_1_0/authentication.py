# -*- coding: utf-8 -*- 

from flask import jsonify, g
from flask_httpauth import HTTPBasicAuth
from ..models import AnonymousUser, User
from . import api
from .errors import forbidden, unauthorized

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == "":
        g.current_user = AnonymousUser()
        return True
    if password == "":
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email = email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@auth.error_handler #auth is instance of HTTPBasicAuth()
def auth_error():
    return unauthorized("认证失败")

@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden("帐号未确认")
        
@api.route("/token")
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized("认证失败")
    return jsonify({"token": g.current_user.generate_auth_token(
                  expiration = 3600), "expiration": 3600})

