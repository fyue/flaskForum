from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
                    ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from ..models import User

class LoginForm(FlaskForm):
    email = StringField("邮箱:", validators = [Required(), Length(1, 64), Email()])
    password = PasswordField("密码:", validators = [Required()])
    remember_me = BooleanField("保持登陆")
    submit = SubmitField("提交")
    
class RegistrationForm(FlaskForm):
    email = StringField("邮箱：", validators=[Required(), Length(1, 64), Email()])  
    username = StringField("用户名：", validators=[Required(), Length(1, 64), \
                Regexp("^[A-Za-z][A-Za-z0-9_.]*$", 0, "用户名必须只由字母、数字、点或"
                                                      "下划线组成")])
    password = PasswordField("密码：", validators=[Required()])
    password2 = PasswordField("再次输入密码", validators=[Required(), \
                                            EqualTo("password", "两次密码需要一致")])
    submit = SubmitField("注册")
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("邮箱已被注册，请尝试其他邮箱")
        
    def validate_username(self, field):
        if User.query.filter_by(username=field.data):
            raise ValidationError("用户名已被使用，请尝试其他用户名")
        
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("請输入旧密码：", validators=[Required()])
    password = PasswordField("请输入新密码", validators=[Required()])
    password2 = PasswordField("请再一次输入新密码", validators=[Required(), \
                             EqualTo("password", message = "密码需要一致")])
    submit = SubmitField("修改密码")
        
        
        
        
        
        
        