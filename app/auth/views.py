from flask import render_template, redirect, request, url_for, flash
from . import auth
from .forms import LoginForm, RegistrationForm
from flask_login import login_user, login_required, logout_user, current_user
from ..models import User
from .. import db
from ..email import send_email


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
        flash("您已成功注册.")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)



