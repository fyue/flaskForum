# -*- coding: utf-8 -*- 

from flask_wtf import FlaskForm
from flask import session
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
                    ValidationError
from wtforms.validators import Length, Email, Regexp, EqualTo, DataRequired
from ..models import User

class LoginForm(FlaskForm):
    email = StringField("邮箱:", validators = [DataRequired("邮箱不能为空！"),
                                              Length(1, 64), Email("邮箱地址不正确")])
    password = PasswordField("密码:", validators = [DataRequired("请输入密码!")])
    remember_me = BooleanField("保持登陆")
    verification_code = StringField("验证码：", validators = [DataRequired("请输入验证码！")])
    submit = SubmitField("提交")
    
    def validate_verification_code(self, field):
        if field.data.upper() != session.get("verificationCode"):
            raise ValidationError("验证码输入错误！")
    
class RegistrationForm(FlaskForm):
    email = StringField("邮箱：", validators=[DataRequired("邮箱不能为空！"), Length(1, 64), Email()])  
    username = StringField("用户名：", validators=[DataRequired("用户名不能为空！"), Length(1, 64), \
                Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "用户名必须只由字母、数字、点或"
                                                      "下划线组成")])
    password = PasswordField("密码：", validators=[DataRequired("密码不能为空！")])
    password2 = PasswordField("再次输入密码:", validators=[DataRequired("密码不能为空！"), \
                                            EqualTo("password", "两次密码需要一致！")])
    verification_code = StringField("请输入验证码：", validators = [DataRequired("验证码不能为空！")])
    submit = SubmitField("注册")
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已被注册，請尝试其他邮箱")
        
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("用户名已被使用，請尝试其他用户名")
        
    def validate_verification_code(self, field):
        if field.data.upper() != session.get("verificationCode"):
            raise ValidationError("验证码输入错误！")
        
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("請输入旧密码：", validators=[DataRequired("密码不能为空")])
    password = PasswordField("請输入新密码", validators=[DataRequired("密码不能为空")])
    password2 = PasswordField("請再一次输入新密码", validators=[DataRequired("密码不能为空"), 
                             EqualTo("password", message = "两次密码需要一致!")])
    verification_code = StringField("验证码：", validators = [DataRequired("请输入验证码！")])
    submit = SubmitField("修改密码")
    
    def validate_verification_code(self, field):
        if field.data.upper() != session.get("verificationCode"):
            raise ValidationError("验证码输入错误！")
        
"""Reset passwd begin"""
class PasswordResetRequestForm(FlaskForm):
    email = StringField("請输入需要重置密码的邮箱：", validators=[DataRequired("无效邮箱地址！"), 
                                                 Length(1, 64), Email("邮箱格式不正确!")])
    verification_code = StringField("验证码：", validators = [DataRequired("请输入验证码！")])
    submit = SubmitField("重置密码")
    
    def validate_verification_code(self, field):
        if field.data.upper() != session.get("verificationCode"):
            raise ValidationError("验证码输入错误！")

class PasswordResetForm(FlaskForm):
    email = StringField("請输入需要重置密码的邮箱：", validators=[DataRequired("邮箱地址不能为空！"), 
                                                 Length(1, 64), Email("邮箱格式不正确!")])
    password = PasswordField("請输入新密码", validators=[DataRequired("密码不能为空")])
    password2 = PasswordField("請再一次输入密码", validators=[DataRequired("密码不能为空!"), 
                            EqualTo("password", message = "两次密码需要一致!")])
    submit = SubmitField("重置密码")
    
    def validate_email(self, field):
        if User.query.filter_by(email = field.data).first() is None:
            raise ValidationError("未知邮箱地址！")
"""Reset passwd end"""
        
        
"""Reset Email begin"""        
class ChangeEmailForm(FlaskForm):
    email = StringField("新邮箱：", validators=[DataRequired("请输入邮箱地址!"),
                                               Length(1, 64), Email("邮箱地址不正确!")])
    password = PasswordField("密码：", validators=[DataRequired("请输入密码!")])
    verification_code = StringField("验证码：", validators = [DataRequired("请输入验证码！")])
    submit = SubmitField("修改邮箱地址")
    
    def validate_email(self, field):
        if User.query.filter_by(email = field.data).first():
            raise ValidationError("邮箱地址已存在.")
        
    def validate_verification_code(self, field):
        if field.data.upper() != session.get("verificationCode"):
            raise ValidationError("验证码输入错误！")
        