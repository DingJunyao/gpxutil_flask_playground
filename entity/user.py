import hashlib
from datetime import datetime

from ext import db


class UserEntity(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    create_user = db.Column(db.Integer, default=0)
    update_user = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(20), unique=True)
    nickname = db.Column(db.String(20), nullable=False, default='Default Nickname')
    password = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(100))
    phone_region = db.Column(db.String(6))
    phone = db.Column(db.String(20))

    @staticmethod
    def generate_password(password):
        # SHA256
        return hashlib.sha256(password.encode()).hexdigest()

    def to_json(self):
        json_user = {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'email': self.email,
            'phone_region': self.phone_region,
            'phone': self.phone
        }
        return json_user
