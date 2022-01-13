# __init__.py
import os
from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
#from flaskblog.models import UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.login_view = 'app.view'
login_manager.login_message = 'ログインしてください'

basedir = os.path.abspath(os.path.dirname(__name__))
db = SQLAlchemy()
migrate = Migrate()
app = Flask(__name__)


def create_app():
   
    app.config['SECRET_KEY'] = 'mysite'
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = './static/uploads'
   
    from flaskblog.views import user_view,article_view,uploads
    app.register_blueprint(user_view)
    app.register_blueprint(article_view)
    app.register_blueprint(uploads)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    return app