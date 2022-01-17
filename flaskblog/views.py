from flask import (
    Blueprint, request, render_template,
    redirect, url_for, flash, session, jsonify
)
from flask_login import login_user, login_required, logout_user, current_user

from flaskblog.models import User, Article

from flaskblog.forms import LoginForm, RegisterForm, ArticleNewForm, UserEditForm, ArticleDeleteForm, UserSearchForm

from flaskblog import db

from werkzeug.utils import secure_filename

import os

import pykakasi

UPLOAD_FOLDER = './flaskblog/static/uploads'
# アップロードされる拡張子の制限
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'gif', 'jpeg'])


# 画像ファイルが日本語の場合はローマ字に変換する
class Kakashi:
    # pykakasiのインスタンスを作成
    kakashi = pykakasi.kakasi()
    # ひらがなをローマ字に
    kakashi.setMode('H', 'a')
    # カタカナをローマ字に
    kakashi.setMode('K', 'a')
    # 漢字をローマ字に
    kakashi.setMode('J', 'a')
    # pykakasiの設定を反映
    conv = kakashi.getConverter()

    @classmethod
    def japanese_to_ascii(cls, japanese):
        return cls.conv.do(japanese)


# user用のblueprintを作成
user_view = Blueprint('user', __name__, url_prefix='/user')
# 記事用のblueprintを作成
article_view = Blueprint('article', __name__, url_prefix='/article')
# 静的画像ファイルのURLを追加
uploads = Blueprint('uploads', __name__, static_url_path='/static/uploads', static_folder='./static/uploads')


# flask_loginのtest用関数
def test_view():
    print(session)
    # sessionの値は_user_idから取得している
    session["_user_id"] = 2


@login_required
@user_view.route('home/')
def home():
    articles = Article.query.filter_by(user_id=current_user.id).all()
    return render_template('user/home.html', articles=articles)


@user_view.route('login/')
def login():
    form = LoginForm(request.form)
    return render_template('user/login.html', form=form)


@user_view.route('user_login/', methods=["POST"])
def user_login():
    form = LoginForm(request.form)
    user = User.select_email(form.email.data)
    if user and user.check_password(form.password.data):
        login_user(user)
        return redirect(url_for('user.home'))
    else:
        flash('メールアドレスとパスワードの組み合わせが誤っています')


def allwed_file(filename):
    # ファイル軽視の確認,拡張子
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_view.route('register/')
def register():
    form = RegisterForm(request.form)
    return render_template("user/register.html", form=form)


@user_view.route('create/', methods=["POST"])
def user_create():
    form = RegisterForm(request.form)
    user = User(
                name=form.name.data,
                email=form.email.data,
                password=form.password.data,
                avatar=None
          )
    if request.files['avatar'] and allwed_file(request.files['avatar'].filename):
        file = request.files['avatar']
        ascii_filename = Kakashi.japanese_to_ascii(file.filename)
        filename = secure_filename(ascii_filename)
        # ファイルの保存
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        user.avatar = filename
    with db.session.begin(subtransactions=True):
        db.session.add(user)
    db.session.commit()
    return redirect(url_for('user.login'))


@user_view.route('logout/')
def logout():
    # ユーザーをログアウト
    logout_user()
    return redirect(url_for('user.login'))


@login_required
@user_view.route('edit/<int:user_id>')
def user_edit(user_id):
    # ユーザーIDとログイン中のユーザーが別の場合はhome画面へ飛ばす
    if user_id != current_user.id:
        return redirect(url_for('user.home'))
    form = UserEditForm(request.form)
    avatar_path = 'uploads/' + current_user.avatar
    return render_template('user/user_edit.html', form=form, avatar_path=avatar_path)


@login_required
@user_view.route('update/<int:user_id>', methods=["POST"])
def user_update(user_id):
    form = UserEditForm(request.form)
    # current_user.idからuser_idを取得
    user_id = current_user.get_id()
    user = User.query.get(user_id)
    with db.session.begin(subtransactions=True):
        user.name = form.name.data
        user.file = request.files['avatar'].filename
        if user.file is not None and allwed_file(user.file):
            file = request.files['avatar']
            ascii_filename = Kakashi.japanese_to_ascii(file.filename)
            filename = secure_filename(ascii_filename)
            # ファイルの保存
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            user.avatar = file
            user.avatar = filename
    db.session.commit()
    return redirect(url_for('user.home'))


@user_view.route('search/')
@login_required
def user_search():
    form = UserSearchForm(request.form)
    return render_template('user/search.html', form=form)
  

@user_view.route('result/', methods=["POST"])
def result():
    users = request.json["keyword"]
    datas = User.query.filter(User.name.like(f"%{users}%")).all()
    # datatime型がJSONでは対応していないので名前だけ抽出
    data = [user.name for user in datas]
    return jsonify(data)


# テスト用に作成
@user_view.route('delete/')
@login_required
def user_delete():
    user = User.query.filter_by(id=current_user.get_id()).first()
    with db.session.begin(subtransactions=True):
        db.session.delete(user)
    db.session.commit()
    return redirect(url_for('user.login'))


@article_view.route('article_new/')
def article_new():
    form = ArticleNewForm(request.form)
    return render_template('article/article_new.html', form=form)


@article_view.route('article_create', methods=["POST"])
def article_create():
    form = ArticleNewForm(request.form)
    article = Article(
        title=form.title.data,
        text=form.text.data,
        picture=request.files['picture'].filename,
        user_id=current_user.id
      ) 
    if request.files['picture'] and allwed_file(request.files['picture'].filename):
        file = request.files['picture']
        ascii_filename = Kakashi.japanese_to_ascii(file.filename)
        filename = secure_filename(ascii_filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        article.picture = filename
    with db.session.begin(subtransactions=True):
        db.session.add(article)
    db.session.commit()
    return redirect(url_for('article.article_index'))


@article_view.route('article_index/')
def article_index():
    # 記事一覧をallで取得
    articles = Article.query.all()
    return render_template('article/article_index.html', articles=articles)


@article_view.route('article/<int:article_id>')
def article_show(article_id):
    article = Article.query.get(article_id)
    form = ArticleDeleteForm(request.form)
    return render_template('article/article_show.html', article=article, form=form)


@article_view.route('article_edit/<int:article_id>')
def article_edit(article_id):
    form = ArticleNewForm(request.form)
    article = Article.query.get(article_id)
    if article.user_id != current_user.id:
        return redirect(url_for('article.article_show', article_id=article_id))
    return render_template('article/article_edit.html', form=form, article=article)


@article_view.route('article_update/<int:article_id>', methods=["POST"])
def article_update(article_id):
    form = ArticleNewForm(request.form)
    article = Article.query.get(article_id)
    if article.user_id == current_user.id:
        with db.session.begin(subtransactions=True):
            article.title = form.title.data
            article.text = form.text.data
            article.file = request.files['picture'].filename
            if article.file is not None and allwed_file(article.file):
                file = request.files['picture']
                ascii_filename = Kakashi.japanese_to_ascii(file.filename)
                filename = secure_filename(ascii_filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
            article.picture = filename
        db.session.commit()
        return redirect(url_for('article.article_show', article_id=article_id))
  

@article_view.route('article/delete/<int:article_id>', methods=["POST"])
def article_delete(article_id):
    # URLからarticleのIDを取得し、該当articleを取得
    article = Article.query.get(article_id)
    # 記事の作成者以外は削除できない様に条件分岐
    if article.user_id == current_user.id:
        with db.session.begin(subtransactions=True):
            db.session.delete(article)
        db.session.commit()
        return redirect(url_for('article.article_index'))
    else:
        return redirect(url_for('user.home'))