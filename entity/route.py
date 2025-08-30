from datetime import datetime

from dto.route import RoutePoint, Route
from ext import db


class RouteEntity(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    create_user = db.Column(db.Integer, db.ForeignKey('users.id'), default=0)
    update_user = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    coordinate_type = db.Column(db.String(10), default='wgs84')
    transformed_coordinate_type = db.Column(db.String(10), default='wgs84')

    user = db.relationship('UserEntity', backref=db.backref('routes'))

    def to_json_self(self):
        json_route = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'coordinate_type': self.coordinate_type,
            'transformed_coordinate_type': self.transformed_coordinate_type
        }
        return json_route

    def to_json(self):
        json_route = self.to_json_self()
        json_route['points'] = [point.to_json() for point in self.points if not point.is_deleted]
        return json_route

    @staticmethod
    def from_dto(route_dto: Route, user_id: int, name: str, description: str):
        route_points = [RoutePointEntity.from_dto(point, user_id) for point in route_dto.points]
        return RouteEntity(
            name=name,
            description=description,
            points=route_points,
            create_user=user_id,
            update_user=user_id
        )


class RoutePointEntity(db.Model):
    __tablename__ = 'route_points'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    create_user = db.Column(db.Integer, default=0)
    update_user = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    idx = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    elapsed_time = db.Column(db.Numeric(10, 3), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude_transformed = db.Column(db.Numeric(10, 7))
    latitude_transformed = db.Column(db.Numeric(10, 7))
    elevation = db.Column(db.Numeric(10, 3))
    distance = db.Column(db.Numeric(10, 3))
    course = db.Column(db.Numeric(6, 3))
    speed = db.Column(db.Numeric(6, 3))
    province = db.Column(db.String(20))
    city = db.Column(db.String(20))
    area = db.Column(db.String(20))
    province_en = db.Column(db.String(50))
    city_en = db.Column(db.String(50))
    area_en = db.Column(db.String(50))
    road_num = db.Column(db.String(20))
    road_name = db.Column(db.String(20))
    road_name_en = db.Column(db.String(50))
    memo = db.Column(db.Text)

    parent_route = db.relationship('RouteEntity', backref=db.backref('points'))

    def to_json(self):
        return {
            'id': self.id,
            'idx': self.idx,
            'time': self.time.strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed_time': self.elapsed_time,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'longitude_transformed': self.longitude_transformed,
            'latitude_transformed': self.latitude_transformed,
            'elevation': self.elevation,
            'distance': self.distance,
            'course': self.course,
            'speed': self.speed,
            'province': self.province,
            'city': self.city,
            'area': self.area,
            'province_en': self.province_en,
            'city_en': self.city_en,
            'area_en': self.area_en,
            'road_num': self.road_num,
            'road_name': self.road_name,
            'road_name_en': self.road_name_en,
            'memo': self.memo
        }

    def to_bulk_insert_dict(self, route_id: int):
        return {
            'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'create_user': self.create_user,
            'update_user': self.update_user,
            'route_id': route_id,
            'idx': self.idx,
            'time': self.time.strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed_time': self.elapsed_time,
            'longitude': self.longitude,
            'latitude': self.latitude,
            'longitude_transformed': self.longitude_transformed,
            'latitude_transformed': self.latitude_transformed,
            'elevation': self.elevation,
            'distance': self.distance,
            'course': self.course,
            'speed': self.speed,
            'province': self.province,
            'city': self.city,
            'area': self.area,
            'province_en': self.province_en,
            'city_en': self.city_en,
            'area_en': self.area_en,
            'road_num': self.road_num,
            'road_name': self.road_name,
            'road_name_en': self.road_name_en,
            'memo': self.memo
        }

    @staticmethod
    def from_dto(dto: RoutePoint, user_id: int):
        return RoutePointEntity(
            create_user = user_id,
            update_user = user_id,
            idx=dto.idx,
            time=dto.time,
            elapsed_time=dto.elapsed_time,
            longitude=dto.longitude,
            latitude=dto.latitude,
            longitude_transformed=dto.longitude_transformed,
            latitude_transformed=dto.latitude_transformed,
            elevation=dto.elevation,
            distance=dto.distance,
            course=dto.course,
            speed=dto.speed,
            province=dto.province,
            city=dto.city,
            area=dto.area,
            province_en=dto.province_en,
            city_en=dto.city_en,
            area_en=dto.area_en,
            road_num=dto.road_num,
            road_name=dto.road_name,
            road_name_en=dto.road_name_en,
            memo = dto.memo
        )
    def to_dto(self) -> RoutePoint:
        return RoutePoint(
            idx=self.idx,
            time=self.time,
            elapsed_time=self.elapsed_time,
            longitude=self.longitude,
            latitude=self.latitude,
            longitude_transformed=self.longitude_transformed,
            latitude_transformed=self.latitude_transformed,
            elevation=self.elevation,
            distance=self.distance,
            course=self.course,
            speed=self.speed,
            province=self.province,
            city=self.city,
            area=self.area,
            province_en=self.province_en,
            city_en=self.city_en,
            area_en=self.area_en,
            road_num=self.road_num,
            road_name=self.road_name,
            road_name_en=self.road_name_en,
            memo=self.memo
        )