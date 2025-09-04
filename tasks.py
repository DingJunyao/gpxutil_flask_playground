from datetime import datetime

from celery import shared_task

from blueprint.user import create_user
from dto.route import RoutePoint
from entity.route import RoutePointEntity
from entity.task import TaskEntity, SubTaskEntity
from ext import db
from gpxutil.utils.gdf_handler import GDFListHandler

def add_set_route_points_area_task(point_entities: list[RoutePointEntity], current_user_id: int):
    if not point_entities:
        return None
    task_entity = TaskEntity(
        create_user=current_user_id, update_user=current_user_id, task_type='set_route_points_area', ref_id=point_entities[0].route_id,
        ref_type='route'
    )
    db.session.add(task_entity)
    db.session.flush()
    for i in point_entities:
        result = set_route_point_area_task.delay(i.id)
        sub_task_entity = SubTaskEntity(
            create_user=current_user_id, update_user=current_user_id, task_id=task_entity.id,
            celery_task_id=result.id, ref_type='route_point', ref_id=i.id
        )
        db.session.add(sub_task_entity)
    db.session.commit()
    return task_entity.id


@shared_task(ignore_result=False)
def set_route_point_area_task(route_point_id: int):
    point_entity = db.session.query(RoutePointEntity).filter(RoutePointEntity.id == route_point_id, RoutePointEntity.is_deleted == False).first()
    sub_task_entity = (db.session.query(SubTaskEntity)
                       .join(TaskEntity, SubTaskEntity.task_id == TaskEntity.id)
                       .filter(
                            SubTaskEntity.ref_id == route_point_id,
                            SubTaskEntity.ref_type == 'route_point',
                            TaskEntity.task_type == 'set_route_points_area',
                            TaskEntity.is_deleted == False,
                            SubTaskEntity.is_deleted == False,
                        )
                       .first())
    if not sub_task_entity:
        return
    point_dto: RoutePoint = point_entity.to_dto()
    try:
        point_dto.set_area(GDFListHandler().list, True)
        point_entity.province = point_dto.province
        point_entity.city = point_dto.city
        point_entity.area = point_dto.area
        point_entity.update_time = datetime.now()
        sub_task_entity.status = 1
    except Exception as e:
        sub_task_entity.status = 2
        sub_task_entity.result = str(e)
    # point_entity.province_en = point_dto.province_en
    # point_entity.city_en = point_dto.city_en
    # point_entity.area_en = point_dto.area_en
    db.session.commit()
