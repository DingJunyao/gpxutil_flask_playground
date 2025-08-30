from flask import Blueprint, request, session
from flask_jwt_extended import create_access_token

from blueprint import user
from entity.user import UserEntity
from ext import db
from vo import Response

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    return user.create_user()

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    user = db.session.query(UserEntity).filter(UserEntity.username == username).filter(UserEntity.password == UserEntity.generate_password(password)).first()
    if not user:
        return 'username or password error'
    # access_token = create_access_token(identity=str(user.id))
    access_token = create_access_token(identity=user)
    response = Response(message='success', data={'access_token': access_token})
    return response.to_resp()

