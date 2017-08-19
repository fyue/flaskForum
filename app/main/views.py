# -*- coding: utf-8 -*- 

from flask import render_template, abort, flash, redirect, url_for, \
                  request, current_app, make_response, jsonify
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, \
                   CommentForm
from flask_login import login_required, current_user
from ..models import User, Role, Post, Permissions, Comment
from ..decorators import admin_required, permission_required
from flask_sqlalchemy import get_debug_queries
from .. import db
from . import main

@main.route("/", methods=["GET", "POST"])
def index():
    form = PostForm()
    if request.method == "POST" and not current_user.can(Permissions.WRITE_ARTICLES):
        flash("请您先登录！")
        return redirect(url_for("auth.login"))
    if current_user.can(Permissions.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body = form.body.data, 
                    author = current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get("show_followed", ""))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(page,
                 per_page = current_app.config["FLASKY_POSTS_PER_PAGE"], 
                 error_out = False)
    posts = pagination.items
    return render_template("index.html", form = form, posts = posts,
                           pagination = pagination, show_followed = show_followed)

@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    page = request.args.get("page", 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(page,
                 per_page = current_app.config["FLASKY_POSTS_PER_PAGE"], 
                 error_out = False)
    posts = pagination.items
    return render_template("user.html",posts = posts, user=user, 
                           pagination = pagination)

@main.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.about_me = form.about_me.data
        current_user.location = form.location.data
        db.session.add(current_user)
        flash("信息已修改.")
        return redirect(url_for(".user", username = current_user.username))
    form.name.data = current_user.name
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    return render_template("edit_profile.html", form = form)

@main.route("/edit-profile/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash("用户信息已被您修改")
        return redirect(url_for(".user", username = user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template("edit_profile.html", form = form, user = user)

@main.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permissions.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash("文章已修改.")
        return redirect(url_for(".post", id = post.id))
    form.body.data = post.body
    return render_template("edit_post.html", form = form)
    
@main.route("/post/<int:id>", methods=["GET", "POST"])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body = form.body.data,
                          post = post,
                          author = current_user._get_current_object())
        db.session.add(comment)
        flash("您的评论已发布")
        return redirect(url_for(".post", id = post.id, page = -1))
    page = request.args.get("page", 1, type = int)
    if page == -1:
        page = (post.comments.count() - 1) // \
                current_app.config["FLASKY_COMMENTS_PER_PAGE"] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
                 page, per_page = current_app.config["FLASKY_COMMENTS_PER_PAGE"],
                 error_out = False)
    comments = pagination.items
    return render_template("post.html", posts=[post], form =form,
                           comments = comments, pagination = pagination)


@main.route("/follow/<username>")
@login_required
@permission_required(Permissions.FOLLOW)
def follow(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash("未知用户！")
        return redirect(url_for(".index"))
    if current_user.is_following(user):
        flash("您已经关注TA了")
        return redirect(url_for(".user", username = username))
    current_user.follow(user)
    flash("您现在关注了 %s." %(username))
    return redirect(url_for(".user", username = username))

@main.route("/unfollow/<username>")
@login_required
@permission_required(Permissions.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash("未知用户！")
        return redirect(url_for(".index"))
    if not current_user.is_following(user):
        flash("您没有关注该用户！")
        return redirect(url_for(".user", username = username))
    current_user.unfollow(user)
    flash("您已不再关注 %s." %(username))
    return redirect(url_for(".user", username = username))

@main.route("/followers/<username>")
def followers(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash("用户不存在！")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type = int)
    pagination = user.followers.paginate(
         page,
         per_page = current_app.config["FLASKY_FOLLOWERS_PER_PAGE"],
         error_out = False)
    follows = [{"user":item.follower, "timestamp": item.timestamp}
               for item in pagination.items if item.follower != user]
    return render_template("followers.html",
                           user = user,
                           title = "的粉丝",
                           endpoint = ".followers",
                           pagination = pagination,
                           follows = follows)
@main.route("/followed-by/<username>")
def followed_by(username):
    user = User.query.filter_by(username = username).first()
    if user is None:
        flash("用户不存在！")
        return redirect(url_for("main.index"))
    page = request.args.get("page", 1, type = int)
    pagination = user.followed.paginate(
         page,
         per_page = current_app.config["FLASKY_FOLLOWERS_PER_PAGE"],
         error_out = False)
    follows = [{"user": item.followed, "timestamp": item.timestamp}
               for item in pagination.items if item.followed != user]
    return render_template("followers.html",
                           user = user,
                           title = "关注的人",
                           endpoint = ".followed_by",
                           pagination = pagination,
                           follows = follows)
    
@main.route("/thumbpost/<int:postId>")    
@login_required
def thumbPost(postId):
    post = Post.query.get_or_404(postId)
    if current_user.is_thumbing_post(post):
        return jsonify({"wrong": "has_thumbed"})
    current_user.thumb_post(post)
    return jsonify({"thumbCounts": post.usersthumb.count()})
    
@main.route("/cancelthumb/<int:postId>")
@login_required
def cancelThumb(postId):
    post = Post.query.get_or_404(postId)
    if not current_user.is_thumbing_post(post):
        return jsonify({"wrong": "has_not_thumbed"})
    current_user.cancel_thumb_post(post)
    return jsonify({"thumbCounts": post.usersthumb.count()})
    
@main.route("/moderate")
@login_required
@permission_required(Permissions.MODERATE_COMMENTS)
def moderate():
    page = request.args.get("page", 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page = current_app.config["FLASKY_COMMENTS_PER_PAGE"],
        error_out = False)
    comments = pagination.items
    return render_template("moderate.html", comments = comments,
                           pagination = pagination, page = page)
    
@main.route("/moderate/show_forbidden")
@login_required
@permission_required(Permissions.MODERATE_COMMENTS)
def show_forbidden():
    page = request.args.get("page", 1, type=int)
    pagination = Comment.query.filter_by(disabled = True).order_by(
                 Comment.timestamp.desc()).paginate(
        page, per_page = current_app.config["FLASKY_COMMENTS_PER_PAGE"],
        error_out = False)
    comments = pagination.items
    return render_template("moderate.html", comments = comments,
                           pagination = pagination, page = page)
    
@main.route("/moderate/enable/<int:id>")
@login_required
@permission_required(Permissions.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for(".moderate", page=request.args.get("page", 1, type=int)))

@main.route("/moderate/disable/<int:id>")
@login_required
@permission_required(Permissions.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for(".moderate", page=request.args.get("page", 1, type=int)))
    
"""query all posts"""
@main.route("/all")
@login_required
def show_all():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "", max_age = 30*24*60*60)
    return resp

@main.route("/followed")
@login_required
def show_followed():
    resp = make_response(redirect(url_for(".index")))
    resp.set_cookie("show_followed", "1", max_age = 30*24*60*60)
    return resp

@main.route("/shutdown")
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get("werkzeug.server.shutdown")
    if not shutdown:
        abort(500)
    shutdown()
    return "shutting down ..."
    
@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config["FLASKY_SLOW_DB_QUERY_TIME"]:
            current_app.logger.warning(
                "Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n"
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response

@main.route("/demo1_candys")
def demo1():
    return render_template("demo1_candys.html")