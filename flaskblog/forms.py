from flask_wtf import FlaskForm
# from wtforms.form import Form
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import StringField,  FileField, PasswordField, SubmitField, TextAreaField, HiddenField, ValidationError


from flaskblog.models import User


class LoginForm(FlaskForm):
    email = StringField('メール: ', validators=[DataRequired()])
    password = PasswordField('パスワード: ', validators=[DataRequired()])
    submit = SubmitField('ログイン')
    
    def validate_email(self, email):
        if email.data == "":
            raise ValidationError("メールアドレスを入力してください")
        if not User.select_email(email.data):
            raise ValidationError('そのメールアドレスは登録されていません')


class RegisterForm(FlaskForm):
    email = StringField(
        'メール: ', validators=[DataRequired(), Email('メールアドレスが誤っています')]
    )
    name = StringField('名前: ', validators=[DataRequired()])
    password = PasswordField(
        'パスワード: ',
        validators=[DataRequired(),
                    EqualTo('confirm_password', message='パスワードが一致しません')])
    confirm_password = PasswordField('パスワード再入力: ')
    avatar = FileField('アバター:')
    submit = SubmitField('登録')
    
    def validate_email(self, email):
        if User.select_email(email.data):
            raise ValidationError('そのメールアドレスは既に登録されています')
   
    def validate_name(self, name):
        if name.data == "":
            raise ValidationError("名前を入力してください")
        if len(name.data) > 10:
            raise ValidationError("名前を１０文字以内で入力してください")
    

class UserEditForm(FlaskForm):

    name = StringField('名前: ', validators=[DataRequired(message="必須項目です")])
    avatar = FileField('アバター:')
    submit = SubmitField('更新')


class UserSearchForm(FlaskForm):

    name = StringField("ユーザー名:")
    submit = SubmitField('検索')


class ArticleNewForm(FlaskForm):

    title = StringField("題名:")
    text = TextAreaField("本文:", validators=[DataRequired(message="必須項目です")])
    picture = FileField("写真")
    user_id = HiddenField()
    submit = SubmitField('投稿')


class ArticleDeleteForm(FlaskForm):
    submit = SubmitField('削除')


class FollowForm(FlaskForm):
    submit = SubmitField('フォロー')