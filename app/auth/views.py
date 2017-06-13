# -*- coding: utf-8 -*- 

from flask import render_template, redirect, request, url_for, flash
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
                   PasswordResetForm, PasswordResetRequestForm, ChangeEmailForm
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User
from .. import db
from ..email import send_email
from flask.helpers import url_for
from flask.templating import render_template
from app.auth.forms import ChangePasswordForm


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)#fetch cookie to client.
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("无效的用户名或密码.")
    return render_template("auth/login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("你已顺利退出.")
    return redirect(url_for("main.index"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, 
                    username = form.username.data, 
                    password = form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, "确认您的账户", "auth/email/confirm", user = user,
                                                                   token = token)
        flash("一封确认邮件已发送至您的邮箱，請查收！")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)

"""Confirm in client_email."""
@auth.route("/confirm/<token>")
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("您现在已经确认了账户, 谢谢!")
    else:
        flash("确认链接无效或已过期.")
    return redirect(url_for("main.index"))

"""Confirm in flask forum unconfirmed web page"""
@auth.route("/confirm")
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, "确认你的账户", "auth/email/confirm", 
                                    user = current_user, token = token)
    flash("一封新的确认邮件已发送至您的邮箱, 請查收.")
    return redirect(url_for("main.index"))

@auth.route("/unconfirmed")
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for("main.index"))
    return render_template("auth/unconfirmed.html")

"""Change password support"""
@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            if form.old_password.data == form.password2.data:
                flash("旧密码不能和新密码相同!")
                return render_template("auth/change_password.html", form = form)
            current_user.password = form.password2.data
            db.session.add(current_user)
            logout_user()
            flash("你已成功修改了密码,请重新登陆.")
            return redirect(url_for("auth.login"))
        else:
            flash("旧密码输入错误.")
    return render_template("auth/change_password.html", form = form)

"""Reset password support"""
@auth.route("/reset_password", methods=["GET", "POST"])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, "密码重置", "auth/email/reset_password", 
                       user = user, token = token, next = request.args.get("next"))
        flash("重置密码邮件已发送至您的邮箱，請查收.")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form = form)

@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is None:
            flash("未知邮箱地址")
            return redirect(url_for("main.index"))
        if user.reset_password(token, form.password2.data):
            flash("你的密码已被成功重置")
            return redirect(url_for("auth.login"))
        else:
            flash("密码修改失败")
            return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form = form)

"""Change email address support"""
@auth.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, "验证您的邮件地址", "auth/email/change_email", 
                                                    user = current_user, token = token)
            flash("一封确认新邮箱地址的邮件已发送至您的邮箱, 請查收.")
            return redirect(url_for("main.index"))
        else:
            flash("无效的邮箱或密码！")
    return render_template("auth/change_email.html", form = form)

@auth.route("/change_email/<token>")
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash("你的邮件地址已成功修改")
    else:
        flash("无效请求.")
    return redirect(url_for("main.index"))    
    


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:5] != "auth." \
                and request.endpoint != "static":
            return redirect(url_for("auth.unconfirmed"))
    """
    if current_user.is_anonymous \
            and request.endpoint \
            and request.endpoint[:5] == "main.":
        flash("请先登陆再继续！")
        return redirect(url_for("auth.login"))
    """

