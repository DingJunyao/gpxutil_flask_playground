import time
from datetime import datetime

import gpxpy
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from loguru import logger
from sqlalchemy import insert

from ext import redis_client
from dto.route import Route
from entity.route import RouteEntity, RoutePointEntity
from ext import db
from gpxutil.models.enum_class import CoordinateType
from vo import Response
from tasks import set_route_point_area_task

route_bp = Blueprint('route', __name__, url_prefix='/route')


@route_bp.route('/', methods=['PUT'])
@jwt_required()
def create_route():
    user_id = current_user.id
    route_name = request.json.get('name')
    route_desc = request.json.get('description')
    route_coordinate_type = request.json.get('coordinate_type')
    route_transformed_coordinate_type = request.json.get('transformed_coordinate_type')
    route_entity = RouteEntity(create_user=user_id, update_user=user_id, name=route_name, description=route_desc, coordinate_type=route_coordinate_type, transformed_coordinate_type=route_transformed_coordinate_type)
    db.session.add(route_entity)
    db.session.commit()
    response = Response(code=200, message='success', data={'id': route_entity.id})
    return response.to_json()


@route_bp.route('/<int:route_id>', methods=['GET'])
def get_route(route_id: int):
    route = RouteEntity.query.filter_by(id=route_id, is_deleted=False).first()
    if route:
        response = Response(code=200, message='success', data=route.to_json())
    else:
        response = Response(code=404, message='route not found')
    return response.to_json()


@route_bp.route('/by/<int:user_id>', methods=['GET'])
def get_routes_by_user(user_id: int):
    routes = RouteEntity.query.filter_by(create_user=user_id, is_deleted=False).all()
    response = Response(code=200, message='success', data=[route.to_json() for route in routes])
    return response.to_json()


@route_bp.route('/<int:route_id>', methods=['POST'])
@jwt_required()
def update_route(route_id: int):
    user_id = current_user.id
    route = RouteEntity.query.filter_by(id=route_id, create_user=user_id, is_deleted=False).first()
    if route:
        route.update_time = datetime.now()
        route.update_user = user_id
        route.name = request.json.get('name')
        route.description = request.json.get('description')
        route.coordinate_type = request.json.get('coordinate_type')
        route.transformed_coordinate_type = request.json.get('transformed_coordinate_type')
        db.session.commit()
        response = Response(code=200, message='success', data={'id': route.id})
    else:
        response = Response(code=404, message='route not found')
    return response.to_json()


@route_bp.route('/<int:route_id>', methods=['DELETE'])
@jwt_required()
def delete_route(route_id: int):
    user_id = current_user.id
    route = RouteEntity.query.filter_by(id=route_id, create_user=user_id, is_deleted=False).first()
    if route:
        route.update_time = datetime.now()
        route.update_user = user_id
        route.is_deleted = True
        for point in route.points:
            point.update_time = datetime.now()
            point.update_user = user_id
            point.is_deleted = True
        db.session.commit()
        response = Response(code=200, message='success', data={'id': route.id})
    else:
        response = Response(code=404, message='route not found', http_code=404)
    return response.to_resp()


@route_bp.route('/<int:route_id>', methods=['PUT'])
@jwt_required()
def add_route_points(route_id: int):
    user_id = current_user.id
    route = RouteEntity.query.filter_by(id=route_id, create_user=user_id, is_deleted=False).first()
    if not route:
        response = Response(code=404, message='route not found')
        return response.to_json()
    point_idx = request.json.get('idx')
    point_time = datetime.strptime(request.json.get('time'), '%Y-%m-%d %H:%M:%S')
    point_elapsed_time = request.json.get('elapsed_time')
    point_longitude = request.json.get('longitude')
    point_latitude = request.json.get('latitude')
    point_longitude_transformed = request.json.get('longitude_transformed')
    point_latitude_transformed = request.json.get('latitude_transformed')
    point_elevation = request.json.get('elevation')
    point_distance = request.json.get('distance')
    point_course = request.json.get('course')
    point_speed = request.json.get('speed')
    point_province = request.json.get('province')
    point_city = request.json.get('city')
    point_area = request.json.get('area')
    point_province_en = request.json.get('province_en')
    point_city_en = request.json.get('city_en')
    point_area_en = request.json.get('area_en')
    point_road_num = request.json.get('road_num')
    point_road_name = request.json.get('road_name')
    point_road_name_en = request.json.get('road_name_en')
    point_memo = request.json.get('memo')
    point_entity = RoutePointEntity(
        idx = point_idx,
        create_user = user_id, update_user = user_id,
        route_id=route_id,
        time=point_time, elapsed_time=point_elapsed_time,
        longitude=point_longitude, latitude=point_latitude,
        longitude_transformed=point_longitude_transformed, latitude_transformed=point_latitude_transformed,
        elevation=point_elevation, distance=point_distance, course=point_course, speed=point_speed,
        province=point_province, city=point_city, area=point_area,
        province_en=point_province_en, city_en=point_city_en, area_en=point_area_en,
        road_num=point_road_num, road_name=point_road_name, road_name_en=point_road_name_en,
        memo=point_memo
    )
    db.session.add(point_entity)
    db.session.commit()
    response = Response(code=200, message='success', data={'id': point_entity.id})
    return response.to_resp()


@route_bp.route('/<int:route_id>/points', methods=['GET'])
def get_route_points(route_id: int):
    route = RouteEntity.query.filter_by(id=route_id, is_deleted=False).first()
    if route:
        points = route.points
        response = Response(code=200, message='success', data=[point.to_json() for point in points if not point.is_deleted])
    else:
        response = Response(code=404, message='route not found', http_code=404)
    return response.to_resp()


@route_bp.route('/point/<int:point_id>', methods=['GET'])
def get_route_point(point_id: int):
    point = RoutePointEntity.query.filter_by(id=point_id, is_deleted=False).first()
    if point:
        if point.parent_route and point.parent_route.is_deleted == False:
            response = Response(code=200, message='success', data=point.to_json())
        else:
            response = Response(code=404, message='route not found', http_code=404)
    else:
        response = Response(code=404, message='point not found', http_code=404)
    return response.to_resp()


@route_bp.route('/point/<point_id>', methods=['POST'])
@jwt_required()
def update_route_point(point_id: int):
    user_id = current_user.id
    point = RoutePointEntity.query.join(RouteEntity, RoutePointEntity.route_id == RouteEntity.id).filter(
        RoutePointEntity.id == point_id,
        RoutePointEntity.create_user == user_id,
        RouteEntity.create_user == user_id,
        RoutePointEntity.is_deleted == False,
        RouteEntity.is_deleted == False
    ).first()
    if point:
        point.update_time = datetime.now()
        point.update_user = user_id
        point.idx = request.json.get('idx')
        point.time = request.json.get('time')
        point.elapsed_time = request.json.get('elapsed_time')
        point.longitude = request.json.get('longitude')
        point.latitude = request.json.get('latitude')
        point.longitude_transformed = request.json.get('longitude_transformed')
        point.latitude_transformed = request.json.get('latitude_transformed')
        point.elevation = request.json.get('elevation')
        point.distance = request.json.get('distance')
        point.course = request.json.get('course')
        point.speed = request.json.get('speed')
        point.province = request.json.get('province')
        point.city = request.json.get('city')
        point.area = request.json.get('area')
        point.province_en = request.json.get('province_en')
        point.city_en = request.json.get('city_en')
        point.area_en = request.json.get('area_en')
        point.road_num = request.json.get('road_num')
        point.road_name = request.json.get('road_name')
        point.road_name_en = request.json.get('road_name_en')
        point.memo = request.json.get('memo')
        db.session.commit()
        response = Response(code=200, message='success', data={'id': point.id})
    else:
        response = Response(code=404, message='point not found', http_code=404)
    return response.to_resp()


@route_bp.route('/point/<int:point_id>', methods=['DELETE'])
@jwt_required()
def delete_point(point_id: int):
    user_id = current_user.id
    point = RoutePointEntity.query.join(RouteEntity, RoutePointEntity.route_id == RouteEntity.id).filter(
        RoutePointEntity.id == point_id,
        RoutePointEntity.create_user == user_id,
        RouteEntity.create_user == user_id,
        RoutePointEntity.is_deleted == False,
        RouteEntity.is_deleted == False
    ).first()
    if point:
        point.update_time = datetime.now()
        point.update_user = user_id
        point.is_deleted = True
        db.session.commit()
        response = Response(code=200, message='success', data={'id': point.id})
    else:
        response = Response(code=404, message='point not found', http_code=404)
    return response.to_resp()


@route_bp.route('/import', methods=['POST'])
@jwt_required()
def import_route():
    start_time = time.time()
    logger.info('API started')
    user_id = current_user.id
    gpx_file = request.files.get('gpx_file')
    name = request.form.get('name')
    description = request.form.get('description')
    track_index = int(request.form.get('track_index'))
    segment_index = int(request.form.get('segment_index'))
    transform_coordinate = bool(int(request.form.get('transform_coordinate')))
    coordinate_type = CoordinateType(request.form.get('coordinate_type'))
    transformed_coordinate_type = CoordinateType(request.form.get('transformed_coordinate_type'))
    set_area = bool(int(request.form.get('set_area')))
    gpx_content = gpx_file.stream.read()
    gpx = gpxpy.parse(gpx_content)

    route = Route.from_gpx_obj(
        gpx, track_index, segment_index, transform_coordinate=False, coordinate_type=coordinate_type.value,
        transformed_coordinate_type=transformed_coordinate_type.value, set_area=False
    )
    logger.info(f'BEFORE transform coordinate: {time.time() - start_time}')
    if transform_coordinate:
        route.transform_coordinate(True)
    logger.info(f'BEFORE entity: {time.time() - start_time}')
    route_entity = RouteEntity.from_dto(route, user_id, name, description)
    logger.info(f'BEFORE insert: {time.time() - start_time}')
    route_entity_bare = RouteEntity(
        name=name,
        description=description,
        coordinate_type=coordinate_type.value,
        transformed_coordinate_type=transformed_coordinate_type.value,
        create_user=user_id,
        update_user=user_id
    )
    db.session.add(route_entity_bare)
    db.session.flush()  # 获取route_entity的ID，但不提交事务
    for i in route_entity.points:
        i.route_id = route_entity.id
    # 下面不能使用 returning, mysql 不支持？
    db.session.execute(insert(RoutePointEntity), [i.to_bulk_insert_dict(route_entity_bare.id) for i in route_entity.points])
    db.session.flush()
    point_entities = db.session.query(RoutePointEntity).filter(RoutePointEntity.route_id == route_entity_bare.id, RoutePointEntity.is_deleted == False).all()
    # db.session.add(route_entity)
    db.session.commit()
    resp = Response(message="success", data={'id': route_entity_bare.id})
    if set_area:
        logger.info(f'BEFORE set_area: {time.time() - start_time}')
        # TODO 这条语句极为耗时
        task_results = [set_route_point_area_task.delay(i.id) for i in point_entities]
        logger.info(f'BEFORE task_results_ids: {time.time() - start_time}')
        task_results_ids = [i.id for i in task_results]
        logger.info(f'BEFORE set_area_task_id: {time.time() - start_time}')
        set_area_task_id = f'route_set_area_{route_entity_bare.id}'
        logger.info(f'BEFORE redis_client: {time.time() - start_time}')
        redis_client.set(set_area_task_id, ','.join(task_results_ids))
        logger.info(f'BEFORE resp.data: {time.time() - start_time}')
        resp.data['set_area_task_id'] = set_area_task_id
    logger.info(f'FINISH: {time.time() - start_time}')
    # resp = Response(message="success", data={'id': route_entity.id})
    return resp.to_resp()
    # points = route_entity.points
    # point_ids = [point.id for point in points]
    # route_entity.point_ids = point_ids
    # del route_entity._temp_points
    # await route_entity.create()
    # route_id = str(route_entity.id)
    # for point in points:
    #     point.route_id = route_id
    # tasks = [point.create() for point in points]
    # await asyncio.gather(*tasks)
    #
    # transform_coordinate_task_id = ''
    # set_area_task_id = ''
    #
    # if transform_coordinate:
    #     transform_coordinate_task_id = str(uuid.uuid4())
    #     # 异步执行父任务
    #     process_route_coordinate.delay(
    #         task_id=transform_coordinate_task_id,
    #         route_id=str(route_id)
    #     )
    # if set_area:
    #     set_area_task_id = str(uuid.uuid4())
    #     # 异步执行父任务
    #     process_route_area.delay(
    #         task_id=set_area_task_id,
    #         route_id=str(route_id)
    #     )
    # return BaseResponse(
    #     data={
    #         'route_id': str(route_entity.id),
    #         'tasks': {
    #             'transform_coordinate': transform_coordinate_task_id,
    #             'set_area': set_area_task_id
    #         }
    #     }
    #
    # )