from flask import Flask, request
from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis

from sqlalchemy import text

from blueprint.auth import auth_bp
from blueprint.route import route_bp
from blueprint.task import task_bp
from blueprint.user import user_bp
from config.server import FlaskPlaygroundConfig
from entity.user import UserEntity
from ext import db, celery_init_app, redis_client
from gpxutil.utils.db_connect import AreaCodeConnectHandler
from gpxutil.utils.gdf_handler import GDFListHandler
from vo import Response

app = Flask(__name__)
app.config.from_object(FlaskPlaygroundConfig)
celery_app = celery_init_app(app)
jwt = JWTManager(app)

db.init_app(app)
redis_client.init_app(app)
with app.app_context():
    db.create_all()
    with db.engine.connect() as conn:
        result = conn.execute(text('select 1;'))
        print('Database connection successful: ', result.fetchone())
    GDFListHandler()

# user = UserEntity(username='admin2', password='admin', nickname='管理员')
# with app.app_context():
#     db.session.add(user)
#     db.session.commit()
#     print(user.id)

app.register_blueprint(user_bp)
app.register_blueprint(route_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(task_bp)


# Register a callback function that takes whatever object is passed in as the
# identity when creating JWTs and converts it to a JSON serializable format.
@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user.id)


# Register a callback function that loads a user from your database whenever
# a protected route is accessed. This should return any python object on a
# successful lookup, or None if the lookup failed for any reason (for example
# if the user has been deleted from the database).
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return UserEntity.query.filter_by(id=identity, is_deleted=False).one_or_none()

@app.errorhandler(Exception)
def handle_generic_error(error):
    resp = Response(code=500, message=str(error), http_code=500)
    return resp.to_resp()

@app.route('/<int:num>')
def hello_world(num: int):  # put application's code here
    pg = request.args.get('page')
    if not pg:
        pg = 114514
    return f'Hello World for {num} in page {pg}!'


if __name__ == '__main__':
    app.run()
