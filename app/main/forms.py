# -*- coding: utf-8 -*- 

from flask_wtf import FlaskForm # The class Form has been renamed with FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Email, Regexp
from flask_pagedown.fields import PageDownField
from ..models import User, Role


class NameForm(FlaskForm):
    name = StringField("你的名字:", validators=[Required()])
    submit = SubmitField("提交")
    
class PostForm(FlaskForm):
    body = PageDownField("Share your thoughts here!(请使用markdown语法)", validators=[Required("您什么都没写呢？")])
    submit = SubmitField("提交")
    
class CommentForm(FlaskForm):
    body = StringField("", validators = [Required()])
    submit = SubmitField("提交")
    
class EditProfileForm(FlaskForm):
    name = StringField("真实姓名", validators=[Length(0, 64)])
    location = StringField("所在地", validators=[Length(0, 64)])
    about_me = TextAreaField("个人介绍")
    submit = SubmitField("提交")
    
class EditProfileAdminForm(FlaskForm):
    email = StringField("邮箱", validators=[Required(), Length(1, 64), Email()])
    username = StringField("用户名", validators=[Required(), Length(1, 64), Regexp(
                                                 "^[A-Za-z][A-Za-z0-9_.]*$", 0, 
                                                 "用户名必须仅由字母、数字、点或下划线" 
                                                 "组成，且由字母开头")])
    confirmed = BooleanField("已确认")
    role = SelectField("用户角色", coerce = int)
    name = StringField("真实姓名", validators=[Length(0, 64)])
    location = StringField("所在地", validators=[Length(0, 64)])
    about_me = TextAreaField("个人介绍")
    submit = SubmitField("提交")
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) 
                             for role in Role.query.order_by(Role.name).all()]
    
        self.user = user
    
    def validate_email(self, field):
        if field.data != self.user.email and \
             User.query.filter_by(email = field.data).first():
            raise ValidationError("邮箱已被注册")
        
    def validate_username(self, field):
        if field.data != self.user.username and \
             User.query.filter_by(username = field.data).first():
            raise ValidationError("用户名已存在")
        
    
    
    
    
    
    
    
    
    
    