from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash,session
)
from flask_login import login_user, login_required, logout_user,current_user
from flaskblog.models import (
    User,Article
)
from flaskblog.forms import LoginForm,RegisterForm,ArticleNewForm

from flaskblog import db,app

from PIL import Image

from werkzeug.utils import secure_filename

import os

import pykakasi

UPLOAD_FOLDER = './flaskblog/static/uploads'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif'])

class Kakashi:

    kakashi = pykakasi.kakasi()
    kakashi.setMode('H', 'a')
    kakashi.setMode('K', 'a')
    kakashi.setMode('J', 'a')
    conv = kakashi.getConverter()

    @classmethod
    def japanese_to_ascii(cls, japanese):
        return cls.conv.do(japanese)


user_view = Blueprint('user', __name__, url_prefix='/user')
article_view=Blueprint('article',__name__,url_prefix='/article')

@login_required
@user_view.route('home/')
def home():
  avatar_path= 'uploads/' + current_user.avatar
  return render_template('user/home.html',avatar_path = avatar_path)

@user_view.route('login/',methods=["GET","POST"])
def login():
  form = LoginForm(request.form)
  if request.method == "POST" and form.validate():
    user = User.select_email(form.email.data)
    if user and user.check_password(form.password.data):
      login_user(user)
      return redirect(url_for('user.home'))
  else:
    flash('メールアドレスとパスワードの組み合わせが誤っています')
  return render_template('user/login.html',form=form)


@user_view.route('register/',methods=["GET","POST"])
def register():
  form=RegisterForm(request.form)
  def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  if request.method == "POST" and form.validate():
    user = User(
            name = form.name.data,
            email = form.email.data,
            password = form.password.data,
            avatar = request.files['avatar'].filename
        )
    if request.files['avatar'] and allwed_file(request.files['avatar'].filename):
       file = request.files['avatar']
       ascii_filename = Kakashi.japanese_to_ascii(file.filename)
       filename = secure_filename(ascii_filename)
            # ファイルの保存
       file.save(os.path.join(UPLOAD_FOLDER,filename))
       #user.avatar= file
       user.avatar = filename
       print(user)
       print(request.files['avatar'].filename)
    with db.session.begin(subtransactions=True):
        db.session.add(user)
    db.session.commit()
    print(user)
    print(user.avatar)
    return redirect(url_for('user.login'))
  return render_template("user/register.html",form=form)

@user_view.route('logout/')
def logout():
  logout_user()
  return redirect(url_for('user.home'))

@user_view.route('edit/')
def user_edit():
  return render_template('user/user_edit.html')

@article_view.route('article_new/',methods=["POST","GET"])
def article_new():
  form=ArticleNewForm(request.form)
  if request.method=="POST" and form.validate():
    article=Article(
      title = form.title.data,
      text = form.text.data,
      picture = form.picture.data
    )
    with db.session.begin(subtransactions=True):
       db.session.add(article)
    db.session.commit()
    return redirect(url_for('article/article.article_index'))
  return render_template('article/article_new.html',form=form)


@article_view.route('article_index/')
def article_index():
  articles= Article.query.all()
  return render_template('article/article_index.html',articles=articles)