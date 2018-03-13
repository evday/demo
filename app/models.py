import hashlib
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from . import db,login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    avatar_hash = db.Column(db.String(32))
    # 与博客建立一对一关系
    blog = db.relationship('Blog',backref = 'users',lazy='dynamic',uselist=False)


    @staticmethod
    def insert_admin(email,username,password):
        '''插入用户'''
        user = User(email=email,username=username,password=password)
        db.session.add(user)
        db.session.commit()
    @property
    def password(self):
        raise AttributeError("密码不能读取")

    @password.setter
    def password(self,password):
        '''设置密码'''
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        '''检查密码'''
        return check_password_hash(self.password_hash, password)

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    def gravatar(self,size = 40,default = 'identicon',rating='g'):

        url = 'http://gravatar.duoshuo.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url,hash=hash,size=size,default=default,rating=rating)

class Blog(db.Model):
    '''个人站点'''
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    signature = db.Column(db.Text)
    navbar = db.Column(db.String(64))
    user = db.Column(db.Integer,db.ForeignKey("users.id"))
    article = db.relationship("Article",backref = 'article',lazy='dynamic')

    @staticmethod
    def insert_blog_info():
        blog_mini_info = Blog(title="xxx报障系统",
                                  signature='高效解决问题',
                                  navbar='inverse')
        db.session.add(blog_mini_info)
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Article(db.Model):
    '''文章表'''
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    content = db.Column(db.Text)
    summary = db.Column(db.Text)
    create_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    num_of_view = db.Column(db.Integer, default=0)
    blog = db.Column(db.Integer,db.ForeignKey("blogs.id"))
    comments = db.relationship('Comment', backref='article', lazy='dynamic')

    @staticmethod
    def add_view(article, db):
        article.num_of_view += 1
        db.session.add(article)
        db.session.commit()

    def __repr__(self):
        return '<Article %r>' % self.title

class Follow(db.Model):
    '''关注'''
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('comments.id'),
                           primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('comments.id'),
                         primary_key=True)

class Comment(db.Model):
    '''评论表'''
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_name = db.Column(db.String(64))
    author_email = db.Column(db.String(64))
    avatar_hash = db.Column(db.String(32))
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'))
    disabled = db.Column(db.Boolean, default=False)
    reply_to = db.Column(db.String(128), default='notReply')


    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                               foreign_keys=[Follow.followed_id],
                               backref=db.backref('followed', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super(Comment, self).__init__(**kwargs)
        if self.author_email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                    self.author_email.encode('utf-8')).hexdigest()

    def gravatar(self, size=40, default='identicon', rating='g'):
        # if request.is_secure:
        #     url = 'https://secure.gravatar.com/avatar'
        # else:
        #     url = 'http://www.gravatar.com/avatar'
        url = 'http://gravatar.duoshuo.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.author_email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def is_reply(self):
        if self.followed.count() == 0:
            return False
        else:
            return True

    # 确认评论是否回复
    def followed_name(self):
        if self.is_reply():
            return self.followed.first().followed.author_name