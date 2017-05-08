from flask import render_template, redirect, request, url_for, flash
from . import auth
from .forms import LoginForm, RegistrationForm, ChangePasswordForm
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
                    password=form.password.data)
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
            current_user.password = form.password2.data
            db.session.add(current_user)
            flash("你已成功修改了密码！")
            return redirect(url_for("main.index"))
        else:
            flash("旧密码错误")
    return render_template("auth/change_password.html", form = form)





@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != "auth." \
            and request.endpoint != "static":
        return redirect(url_for("auth.unconfirmed"))




