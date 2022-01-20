from flaskblog import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
    

# ユーザー用のモデルクラス
class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, default="名無し")
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128))
    avatar = db.Column(db.Text)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)
    # 記事用にrelationshipを定義 →user1:article多
    articles = db.relationship("Article", backref="user")
    
    # userクラスのインスタンスを定義
    def __init__(self, name, email, password, avatar):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password).decode('utf-8')
        self.avatar = avatar

    # パスワードチェックの関数    
    def check_password(self, password):
        return check_password_hash(self.password, password)

    # Userクラスをメールで検索
    @classmethod
    def select_email(cls, email):
        return cls.query.filter_by(email=email).first()

    # Userクラスを名前から取得
    @classmethod
    def select_name(cls, name):
        return cls.query.filter_by(name=name).all()


# 記事作成用のモデル
class Article(db.Model):

    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, default="無題")
    text = db.Column(db.Text, nullable=False)
    picture = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    def __init__(self, title, text, picture, user_id):
        self.title = title
        self.text = text
        self.picture = picture
        self.user_id = user_id


class Follow(db.Model):

    __tablename__ = 'friends'

    id = db.Column(db.Integer, primary_key=True)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    def __init__(self, from_user_id, to_user_id):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id

    @classmethod
    def following(cls):
        cls.query.filter_by(from_user_id=current_user.id)