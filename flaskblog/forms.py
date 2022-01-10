from wtforms.form import Form
from wtforms.fields import (
    StringField, FileField, PasswordField, SubmitField,TextAreaField,HiddenField
)
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import ValidationError

from flaskblog.models import User
from flask_login import current_user
from flask import flash

class LoginForm(Form):
    email = StringField(
        'メール: ', validators=[DataRequired(), Email()]
        )
    password = PasswordField('パスワード: ',validators=[DataRequired()]   )
    submit = SubmitField('ログイン')
  
class RegisterForm(Form):
    email = StringField(
        'メール: ', validators=[DataRequired(), Email('メールアドレスが誤っています')]
    )
    name = StringField('名前: ', validators=[DataRequired()])
    password = PasswordField(
        'パスワード: ',
        validators=[DataRequired(),
        EqualTo('confirm_password', message='パスワードが一致しません')]
    )
    confirm_password = PasswordField(
        'パスワード再入力: ', validators=[DataRequired()]
    )
    avatar= FileField('アバター:')
    submit = SubmitField('登録')

class ArticleNewForm(Form):
  title=StringField("題名:" )
  text=TextAreaField("本文:",validators=[DataRequired()])
  picture=FileField("写真")
  user_id=HiddenField()
  submit=SubmitField('投稿')