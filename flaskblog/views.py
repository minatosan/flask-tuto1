from flask import (
    Blueprint, abort, request, render_template,
    redirect, url_for, flash,session,jsonify
)
from flask_login import login_user, login_required, logout_user,current_user
from flaskblog.models import (
    User,Article
)
from flaskblog.forms import LoginForm,RegisterForm,ArticleNewForm,UserEditForm,ArticleDeleteForm,UserSearchForm

from flaskblog import db,app

from PIL import Image

from IPython import embed

from werkzeug.utils import secure_filename

import os

import pykakasi

UPLOAD_FOLDER = './flaskblog/static/uploads'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif','jpeg'])

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
#静的画像ファイルのURLを追加
uploads=Blueprint('uploads',__name__,static_url_path='/static/uploads',static_folder='./static/uploads')

#flask_loginのtest
def test_view():
  print(session)
  #sessionの値は_user_idから取得している
  session["_user_id"]=2


@login_required
@user_view.route('home/')
def home():
  articles=Article.query.filter_by(user_id=current_user.id).all()
  return render_template('user/home.html',articles=articles)

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


def allwed_file(filename):
    # .があるかどうかのチェックと、拡張子の確認
    # OKなら１、だめなら0
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@user_view.route('register/',methods=["GET","POST"])
def register():
  form=RegisterForm(request.form)
  if request.method == "POST" and form.validate():
    user = User(
            name = form.name.data,
            email = form.email.data,
            password = form.password.data,
            avatar = None
        )
    if request.files['avatar'] and allwed_file(request.files['avatar'].filename):
       file = request.files['avatar']
       ascii_filename = Kakashi.japanese_to_ascii(file.filename)
       filename = secure_filename(ascii_filename)
            # ファイルの保存
       file.save(os.path.join(UPLOAD_FOLDER,filename))
       #user.avatar= file
       user.avatar = filename
    with db.session.begin(subtransactions=True):
        db.session.add(user)
    db.session.commit()
    return redirect(url_for('user.login'))
  return render_template("user/register.html",form=form)

@user_view.route('logout/')
def logout():
  logout_user()
  return redirect(url_for('user.login'))

@login_required
@user_view.route('edit/<int:user_id>',methods=["GET","POST"])
def user_edit(user_id):
  if user_id != current_user.id:
    return redirect(url_for('user.home'))
  if user_id != current_user.get_id():
    print(type(current_user.get_id()))
  form = UserEditForm(request.form)
  avatar_path= 'uploads/' + current_user.avatar
  if request.method =="POST" and form.validate():
    user_id = current_user.get_id()
    user = User.query.get(user_id)
    with db.session.begin(subtransactions=True):
      user.name = form.name.data
      user.file=request.files['avatar'].filename
      if user.file != None and allwed_file(user.file):
        file = request.files['avatar']
        ascii_filename = Kakashi.japanese_to_ascii(file.filename)
        filename = secure_filename(ascii_filename)
        # ファイルの保存
        file.save(os.path.join(UPLOAD_FOLDER,filename))
        user.avatar= file
        user.avatar = filename
    db.session.commit()
    return redirect(url_for('user.home'))
  return render_template('user/user_edit.html',form=form,avatar_path=avatar_path)

@user_view.route('search/')
@login_required
def user_search():
  form=UserSearchForm(request.form)
  
  return render_template('user/search.html',form=form)
  
@user_view.route('result/',methods=["POST"])
def result():
  users= request.json["keyword"]
  datas = User.query.filter(User.name.like(f"%{users}%")).all()
  data=[]
  #datatime型がJSONでは対応していないので名前だけ抽出
  for user in datas:
    data.append(user.name)
  return jsonify(data)

##テスト用に作成
@user_view.route('delete/')
@login_required
def user_delete():
    user=User.query.filter_by(id=current_user.get_id()).first()
    with db.session.begin(subtransactions=True):
        db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user.login'))

@article_view.route('article_new/',methods=["POST","GET"])
def article_new():
  form=ArticleNewForm(request.form)
  if request.method=="POST" and form.validate():
    article=Article(
      title = form.title.data,
      text = form.text.data,
      picture = request.files['picture'].filename,
      user_id = current_user.id
    )
    if request.files['picture'] and allwed_file(request.files['picture'].filename):
       file = request.files['picture']
       ascii_filename = Kakashi.japanese_to_ascii(file.filename)
       filename = secure_filename(ascii_filename)
       file.save(os.path.join(UPLOAD_FOLDER,filename))
       article.picture = filename
    with db.session.begin(subtransactions=True):
       db.session.add(article)
    db.session.commit()
    return redirect(url_for('article.article_index'))
  return render_template('article/article_new.html',form=form)


@article_view.route('article_index/')
def article_index():
  articles= Article.query.all()
  return render_template('article/article_index.html',articles=articles)

@article_view.route('article/<int:article_id>')
def article_show(article_id):
  article=Article.query.get(article_id)
  form=ArticleDeleteForm(request.form)
  return render_template('article/article_show.html',article=article,form=form)

@article_view.route('article_edit/<int:article_id>',methods=["GET","POST"])
def article_edit(article_id):
  form=ArticleNewForm(request.form)
  article=Article.query.get(article_id)
  if article.user_id != current_user.id:
    return redirect(url_for('article.article_show',article_id=article_id))
  if request.method =="POST" and form.validate():
    with db.session.begin(subtransactions=True):
      article.title=form.title.data
      article.text=form.text.data
      article.file=request.files['picture'].filename
      if article.file != None and allwed_file(article.file):
        file = request.files['picture']
        ascii_filename = Kakashi.japanese_to_ascii(file.filename)
        filename = secure_filename(ascii_filename)
        file.save(os.path.join(UPLOAD_FOLDER,filename))
        article.picture = filename
    db.session.commit()
    return redirect(url_for('article.article_index'))
  return render_template('article/article_edit.html',form=form,article=article)

@article_view.route('article/delete/<int:article_id>',methods=["GET","POST"])
def article_delete(article_id):
  article=Article.query.get(article_id)
  if request.method=="POST":
    if article.user_id == current_user.id:
      with db.session.begin(subtransactions=True):
        db.session.delete(article)
      db.session.commit()
  return redirect(url_for('article.article_index'))