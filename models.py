from datetime import datetime

from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, AnonymousUserMixin

from init import db, admin, login_manager


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    text = db.Column(db.TEXT, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime(), default=datetime.utcnow, index=True)


admin.add_view(ModelView(Posts, db.session))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(100), nullable=False, unique=True)
    posts = db.relationship('Posts', cascade="all, delete", backref='user')

    def __repr__(self):
        return f"{self.id}:{self.login}"


admin.add_view(ModelView(User, db.session))


class Anonymous(AnonymousUserMixin):
    def __init__(self):
        self.id = '10000'


login_manager.anonymous_user = Anonymous
