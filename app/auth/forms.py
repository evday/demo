from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,Length,Email


class LoginForm(FlaskForm):
    email = StringField("电子邮件",validators=[DataRequired(message="邮箱不能为空"),
                                           Length(1,64),Email(message="邮箱格式不正确")])
    password = PasswordField("密码",validators=[DataRequired("密码不能为空")])