from flask import (
    Blueprint, request, render_template,
    redirect, url_for, session, jsonify, flash
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
    # 自分の作成した記事一覧を抽出
    articles = Article.query.filter_by(user_id=current_user.id).all()
    return render_template('user/home.html', articles=articles)


@user_view.route('login/')
def login():
    # ログイン用のフォームを呼び出す
    form = LoginForm(request.form)
    return render_template('user/login.html', form=form)


@user_view.route('user_login/', methods=["POST"])
def user_login():
    # ログイン用のフォームを呼び出す
    form = LoginForm(request.form)
    if form.validate_on_submit():
        # formに送信されてきたemailからuserを探す
        user = User.select_email(form.email.data)
        # userが存在しているandパスワードが正しい場合に処理を行う
        if user and user.check_password(form.password.data):
            # ログイン処理
            login_user(user)
            # ログインができたらホーム画面に移行
            flash('ログインしました')
            return redirect(url_for('user.home'))
        else:
            # 処理ができなかった場合は再度、login画面を表示
            flash('メールアドレスとパスワードの組み合わせが誤っています')
            return render_template('user/login.html', form=form)
    else:
        # 処理ができなかった場合は再度、login画面を表示
        return render_template('user/login.html', form=form)


def allwed_file(filename):
    # ファイル軽視の確認,拡張子
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_view.route('register/')
def register():
    # 登録用フォームを呼び出す
    form = RegisterForm(request.form)
    return render_template("user/register.html", form=form)


@user_view.route('create/', methods=["POST"])
def user_create():
    # 登録用フォームを呼び出す
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # Userのインスタンスを作成
        user = User(
                    name=form.name.data,
                    email=form.email.data,
                    password=form.password.data,
                    avatar=None
            )
        # requestの中にavatarが存在しているandファイルの拡張子に問題がない場合
        if request.files['avatar'] and allwed_file(request.files['avatar'].filename):
            file = request.files['avatar']
            # ファイルを英語に変換
            ascii_filename = Kakashi.japanese_to_ascii(file.filename)
            # ファイル名のチェック
            filename = secure_filename(ascii_filename)
            # ファイルの保存
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            # user.avatarの中にfilenameを代入
            user.avatar = filename
        with db.session.begin(subtransactions=True):
            # DBにデータを追加する
            db.session.add(user)
        # DBにデータを反映させる
        db.session.commit()
        return redirect(url_for('user.login'))
    else:
        return render_template("user/register.html", form=form)


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
    # ユーザー編集フォームを呼び出す
    form = UserEditForm(request.form)
    avatar_path = 'uploads/' + current_user.avatar
    return render_template('user/user_edit.html', form=form, avatar_path=avatar_path)


@login_required
@user_view.route('update/<int:user_id>', methods=["POST"])
def user_update(user_id):
    # ユーザー編集フォームを呼び出す
    form = UserEditForm(request.form)
    if form.validate_on_submit():
        # current_user.idからuser_idを取得
        user_id = current_user.get_id()
        # Userテーブルから該当データを取得
        user = User.query.get(user_id)
        with db.session.begin(subtransactions=True):
            # userの名前をformから送られてきたデータに変更
            user.name = form.name.data
            user.file = request.files['avatar'].filename
            # requestの中にアバターがあるandファイルの形式に問題がない場合
            if user.file is not None and allwed_file(user.file):
                # requestのavatarを代入
                file = request.files['avatar']
                # ファイル名を英語に変更
                ascii_filename = Kakashi.japanese_to_ascii(file.filename)
                # ファイル名に問題がないか確認
                filename = secure_filename(ascii_filename)
                # ファイルの保存
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                # userのavatarにファイルを代入
                user.avatar = filename
        # dbに内容を反映
        db.session.commit()
    return redirect(url_for('user.home'))


@user_view.route('search/')
@login_required
def user_search():
    # 検索フォームを呼び出す
    form = UserSearchForm(request.form)
    return render_template('user/search.html', form=form)


@user_view.route('result/', methods=["POST"])
def result():
    # ajaxで送信されてきたjsonデータを取得
    users = request.json["keyword"]
    # 該当のデータをUserテーブルから取り出す
    datas = User.query.filter(User.id != current_user.id, User.name.like(f"%{users}%")).all()
    # datatime型がJSONでは対応していないので名前だけ抽出 user_idも同時に取得→フォローに必要
    # ここでフォローしているか否かの判定も行う
    data = [(user.name, user.id) for user in datas]
    return jsonify(data)


@user_view.route('follow/<int:user_id>')
@login_required
def follow(user_id):

    return render_template("user/home.html")


# テスト用に作成
@user_view.route('delete/')
@login_required
def user_delete():
    # current_userのidを検索
    user = User.query.filter_by(id=current_user.get_id()).first()
    with db.session.begin(subtransactions=True):
        # DBからデータを削除
        db.session.delete(user)
    # DBに変更を反映させる
    db.session.commit()
    return redirect(url_for('user.login'))


# 新規投稿用のルーティング
@article_view.route('article_new/')
def article_new():
    # 新着記事投稿フォームを呼び出す
    form = ArticleNewForm(request.form)
    return render_template('article/article_new.html', form=form)


@article_view.route('article_create', methods=["POST"])
def article_create():
    # 新着記事投稿フォームを呼び出す
    form = ArticleNewForm(request.form)
    # Articleモデルのインスタンスを作成
    article = Article(
        title=form.title.data,
        text=form.text.data,
        picture=request.files['picture'].filename,
        user_id=current_user.id
      ) 
    # リクエストの中にpictureがあるandファイルが正しい拡張子であることを確認
    if request.files['picture'] and allwed_file(request.files['picture'].filename):
        # fileにrequestの内容を代入
        file = request.files['picture']
        # 日本語のファイルなら英語に変換
        ascii_filename = Kakashi.japanese_to_ascii(file.filename)
        # ファイル名の確認
        filename = secure_filename(ascii_filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        # articleのpictureにfileを代入
        article.picture = filename
    with db.session.begin(subtransactions=True):
        # DBに新規記事を追加
        db.session.add(article)
    # DBに変更を反映
    db.session.commit()
    return redirect(url_for('article.article_index'))


@article_view.route('article_index/')
def article_index():
    # 記事一覧をallで取得
    articles = Article.query.all()
    return render_template('article/article_index.html', articles=articles)


@article_view.route('article/<int:article_id>')
def article_show(article_id):
    # article_idから該当記事を取得
    article = Article.query.get(article_id)
    # 記事を削除するフォームを呼び出す
    form = ArticleDeleteForm(request.form)
    return render_template('article/article_show.html', article=article, form=form)


@article_view.route('article_edit/<int:article_id>')
def article_edit(article_id):
    # 新規記事投稿用のフォームを呼び出す(編集にも併用)
    form = ArticleNewForm(request.form)
    article = Article.query.get(article_id)
    # 執筆者がログイン中のユーザーなのか確認
    if article.user_id != current_user.id:
        return redirect(url_for('article.article_show', article_id=article_id))
    return render_template('article/article_edit.html', form=form, article=article)


@article_view.route('article_update/<int:article_id>', methods=["POST"])
def article_update(article_id):
    # 新規記事作成フォームから引用 
    form = ArticleNewForm(request.form)
    # 該当の記事を引っ張ってくる
    article = Article.query.get(article_id)
    if form.validate_on_submit():
        # 執筆者がログイン中のユーザーなのか確認
        if article.user_id == current_user.id:
            with db.session.begin(subtransactions=True):
                article.title = form.title.data
                article.text = form.text.data
                article.file = request.files['picture'].filename
                print(article.file)
                if article.file is not None and allwed_file(article.file):
                    file = request.files['picture']
                    ascii_filename = Kakashi.japanese_to_ascii(file.filename)
                    filename = secure_filename(ascii_filename)
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    article.picture = filename
            db.session.commit()
    else:
        #  バリデーションに失敗したらedit画面をrender
        return render_template('article/article_edit.html', form=form, article=article)
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
