# __init__.py
import os
from os.path import join, dirname
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint
from dotenv import load_dotenv


# Flask-loginの中核であるLoginManagerのインスタンスを作成
login_manager = LoginManager()
login_manager.login_view = 'app.view'
login_manager.login_message = 'ログインしてください'

basedir = os.path.abspath(os.path.dirname(__name__))
# SQLAlchemyのインスタンスを作成
# Migrateのインスタンスを作成
db = SQLAlchemy()
migrate = Migrate()
app = Flask(__name__)


load_dotenv(verbose=True)
# .envファイルのパスを指定
dotenv_path = join(dirname(__file__), '.env')
# dotenvをロード
load_dotenv(dotenv_path)


# google_oauthのblueprintを作成
google_blueprint = make_google_blueprint(
    # GCPのIDを指定
    client_id=os.environ.get("GOOGLE_ID"),
    # GCPのシークレットキーを指定
    client_secret=os.environ.get("GOOGLE_KEY"),
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    redirect_to='app.google_login'
)


# manage.pyから下記メソッドが呼び出される
def create_app():
    # Flaskのsessionで使用する秘密鍵を指定
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    # 今回はポートフォリオなのでdatabaseのURIをdotenvに含めず
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql+psycopg2://test01:test01@db:5432/test01'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # uploadのパスを指定
    app.config['UPLOAD_FOLDER'] = './static/uploads'
   
    from flaskblog.views import user_view, article_view, uploads
    # user関連のblueprintを設定
    app.register_blueprint(user_view)
    # Article関連のblueprintを指定
    app.register_blueprint(article_view)
    # uploadファイルのblueprintを指定
    app.register_blueprint(uploads)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    return app