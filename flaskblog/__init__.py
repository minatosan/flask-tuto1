# __init__.py
import os
from os.path import join, dirname
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint
from dotenv import load_dotenv

login_manager = LoginManager()
login_manager.login_view = 'app.view'
login_manager.login_message = 'ログインしてください'

basedir = os.path.abspath(os.path.dirname(__name__))
db = SQLAlchemy()
migrate = Migrate()
app = Flask(__name__)

load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

google_blueprint = make_google_blueprint(
    client_id=os.environ.get("GOOGLE_ID"),
    client_secret=os.environ.get("GOOGLE_KEY"),
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    redirect_to='app.google_login'
)


def create_app():
    
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql+psycopg2://test01:test01@db:5432/test01'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = './static/uploads'
   
    from flaskblog.views import user_view, article_view, uploads
    app.register_blueprint(user_view)
    app.register_blueprint(article_view)
    app.register_blueprint(uploads)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    return app