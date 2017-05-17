from . import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from datetime import datetime
from random import choice, seed
from markdown import markdown
import bleach
import hashlib

class Permissions:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True)
    #def backref relationship
    users = db.relationship("User", backref = "role", lazy="dynamic")
    default = db.Column(db.Boolean, default = False, index = True)
    permissions = db.Column(db.Integer)
    
    """create role in db with program"""
    @staticmethod
    def insert_roles():
        roles = {
            "User":(Permissions.FOLLOW |
                    Permissions.COMMENT |
                    Permissions.WRITE_ARTICLES, True),
            "Moderator":(Permissions.FOLLOW |
                         Permissions.COMMENT |
                         Permissions.WRITE_ARTICLES |
                         Permissions.MODERATE_COMMENTS, False),
            "Administrator":(0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name = r).first()
            if role is None:
                role = Role(name = r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role %r>" %(self.name)


class Follow(db.Model):
    __tablename__ = "follows"
    follower_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                            primary_key = True)
    followed_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                            primary_key = True)
    timestamp = db.Column(db.DateTime, default = datetime.utcnow)


class User(UserMixin, db.Model):
    __tablename__ = "users"            
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, index = True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique = True, index = True)
    confirmed = db.Column(db.Boolean, default = False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default = datetime.utcnow)#register date
    last_seen = db.Column(db.DateTime(), default = datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship("Post", backref = "author", lazy = "dynamic")
    followed = db.relationship("Follow",
                               foreign_keys = [Follow.follower_id],
                               backref = db.backref("follower", lazy = "joined"),
                               lazy = "dynamic",
                               cascade = "all, delete-orphan")
    followers = db.relationship("Follow",
                                foreign_keys = [Follow.followed_id],
                                backref = db.backref("followed", lazy = "joined"),
                                lazy = "dynamic",
                                cascade = "all, delete-orphan")
        
    """init Role for users"""
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config["FLASKY_ADMIN"]:
                self.role = Role.query.filter_by(permissions = 0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default = True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()
        self.follow(self)
    """Password and Verify"""
    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    """Confirmed and Signatures"""
    def generate_confirmation_token(self, expiration = 3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"confirm": self.id})
    
    def confirm(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("confirm") != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
    """Reset password and Signatures"""
    def generate_reset_token(self, expiration = 3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"reset": self.id})
    
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("reset") != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True
    
    """email_change"""
    def generate_email_change_token(self, new_email, expiration = 3600):
        s = Serializer(current_app.config["SECRET_KEY"], expiration)
        return s.dumps({"change_email":self.id, "new_email":new_email})
    
    def change_email(self, token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get("change_email") != self.id:
            return False
        new_email = data.get("new_email")
        if new_email is None:
            return False
        if self.query.filter_by(email = new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode("utf-8")).hexdigest()
        db.session.add(self)
        return True
    
    """check users' permissions """
    def can(self, permissions):
        return self.role is not None and \
              (self.role.permissions & permissions) == permissions
    
    def is_administrator(self):
        return self.can(Permissions.ADMINISTER)
    
    """syn last seen date"""
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size = 100, rating = "g"):
        if request.is_secure:
            url = "https://secure.gravatar.com/avatar"
        else:
            url = "http://www.gravatar.com/avatar"
        hash = self.avatar_hash or hashlib.md5(self.email.encode("utf-8")).hexdigest()
        seed(self.id)
        default = choice(["identicon", "mm", "wavatar", "retro", "monsterid"])
        return "{url}/{hash}?s={size}&d={default}&r={rating}".format(url = url,
                 hash = hash, size = size, default = default, rating = rating)
    
    """user follow user"""
    def is_following(self, user):
        return self.followed.filter_by(followed_id = user.id).first() is not None
    
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower = self, followed = user)
            db.session.add(f)
            
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id = user.id).first()
        if f:
            db.session.delete(f)
    
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id = user.id).first() is not None
    
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
                         .filter(Follow.follower_id == self.id)
    
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        
        seed()
        for i in range(count):
            u = User(email = forgery_py.internet.email_address(),
                     username = forgery_py.internet.user_name(True),
                     password = forgery_py.lorem_ipsum.word(),
                     confirmed = True,
                     name = forgery_py.name.full_name(),
                     location = forgery_py.address.city(),
                     member_since = forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()    

    def __repr__(self):
        return "<User %r>" %(self.username)
    
    
"""coordinate consideration"""
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False
    
    def is_administrator(self):
        return False
login_manager.anonymous_user = AnonymousUser


class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key = True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index = True, default = datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    body_html = db.Column(db.Text)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", "code",
                        "em", "i", "li", "ol", "pre", "strong", "ul",
                        "h1", "h2", "h3", "p"]
        target.body_html = bleach.linkify(bleach.clean(
             markdown(value, output_format="html"),
             tags = allowed_tags, strip = True))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body = forgery_py.lorem_ipsum.sentences(randint(1,3)),
                     timestamp = forgery_py.date.date(True),author = u)
            db.session.add(p)
            db.session.commit()
       
                
db.event.listen(Post.body, "set", Post.on_changed_body)
    
"""the callable func to load user"""
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

    
    
