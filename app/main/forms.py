from flask_wtf import FlaskForm # The class Form has been renamed with FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameForm(FlaskForm):
    name = StringField("你的名字:", validators=[Required()])
    submit = SubmitField("提交")