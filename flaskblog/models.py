from flaskblog import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin,current_user
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
    



class User(UserMixin, db.Model):

  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), index=True,default="名無し")
  email = db.Column(db.String(64), unique=True, index=True)
  password = db.Column(db.String(128))
  avatar = db.Column(db.Text)
  create_at = db.Column(db.DateTime, default=datetime.now)
  update_at = db.Column(db.DateTime, default=datetime.now)
  
  articles = db.relationship("Article", backref="user")
  

  def __init__(self, name, email,password,avatar):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.avatar = avatar
        
  #def set_password(self,password):
      #self.pw_hash = generate_password_hash(password)
  
  def check_password(self,password):
      return check_password_hash(self.password,password)


  @classmethod
  def select_email(cls, email):
      return cls.query.filter_by(email=email).first()
   
  @classmethod
  def select_name(cls,name):
    return cls.query.filter_by(name=name).all()

  

  
#pictureを外部キーにする
#pictureを多
class Article(db.Model):

  __tablename__ = 'articles'
  id = db.Column(db.Integer,primary_key=True)
  title=db.Column(db.String(64),index=True,default="無題")
  text= db.Column(db.Text)
  picture=db.Column(db.String(128))
  user_id=db.Column(db.Integer,db.ForeignKey('users.id'),index=True)

  def __init__(self,title,text,picture,user_id):
    self.title = title
    self.text = text
    self.picture = picture
    self.user_id = user_id

class Friend(db.Model):

  __tablename__='friends'

  id=db.Column(db.Integer,primary_key=True)
  is_activate=db.Column(db.Boolean,default=False,unique=False)
  to_user_id=db.Column(db.Integer,db.ForeignKey('users.id'),index=True)
  from_user_id=db.Column(db.Integer,db.ForeignKey('users.id'),index=True)

  def __init__(self,from_user_id,to_user_id):
    self.from_user_id = from_user_id
    self.to_user_id = to_user_id