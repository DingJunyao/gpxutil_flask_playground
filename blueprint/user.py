from datetime import datetime

from flask import Blueprint, request

from entity.user import UserEntity
from ext import db
from vo import Response

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/', methods=['PUT'])
def create_user():
    username = request.json.get('username')
    password_req = request.json.get('password')
    nickname = request.json.get('nickname')
    email = request.json.get('email')
    phone_region = request.json.get('phone_region')
    phone = request.json.get('phone')
    password_hash = UserEntity.generate_password(password_req)
    user = UserEntity(username=username, password=password_hash, nickname=nickname, email=email, phone_region=phone_region, phone=phone)
    db.session.add(user)
    db.session.commit()
    # json
    response = Response(code=200, message='success', data={'id': user.id})
    return response.to_json()

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id: int):
    user = UserEntity.query.filter_by(id=user_id, is_deleted=False).first()
    if user:
        response = Response(code=200, message='success', data=user.to_json())
    else:
        response = Response(code=404, message='user not found')
    return response.to_json()

@user_bp.route('/<int:user_id>', methods=['POST'])
def update_user(user_id: int):
    user = UserEntity.query.filter_by(id=user_id, is_deleted=False).first()
    if user:
        user.nickname = request.json.get('nickname')
        user.email = request.json.get('email')
        user.phone_region = request.json.get('phone_region')
        user.phone = request.json.get('phone')
        user.update_time = datetime.now()
        db.session.commit()
        response = Response(code=200, message='success', data={'id': user.id})
    else:
        response = Response(code=404, message='user not found', http_code=404)
    return response.to_resp()

@user_bp.route('/<int:user_id>/password', methods=['POST'])
def update_user_password(user_id: int):
    user = UserEntity.query.filter_by(id=user_id, is_deleted=False).first()
    if user:
        user.update_time = datetime.now()
        original_password_from_api = UserEntity.generate_password(request.json.get('original_password'))
        original_password_from_db = user.password
        if original_password_from_api == original_password_from_db:
            new_password = UserEntity.generate_password(request.json.get('new_password'))
            user.password = new_password
            user.update_time = datetime.now()
            db.session.commit()
            response = Response(code=200, message='success', data={'id': user.id})
        else:
            response = Response(code=403, message='original password incorrect', http_code=403)
    else:
        response = Response(code=404, message='user not found', http_code=404)
    return response.to_resp()


@user_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id: int):
    user = UserEntity.query.filter_by(id=user_id, is_deleted=False).first()
    if user:
        user.update_time = datetime.now()
        user.is_deleted = True
        db.session.commit()
        response = Response(code=200, message='success', data={'id': user.id})
    else:
        response = Response(code=404, message='user not found', http_code=404)
    return response.to_resp()