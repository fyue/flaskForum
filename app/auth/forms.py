from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email

class LoginForm(FlaskForm):
    email = StringField("邮箱", validators = [Required(), Length(1, 64), Email()])
    password = PasswordField("密码", validators = [Required()])
    remember_me = BooleanField("保持登陆")
    submit = SubmitField("提交")