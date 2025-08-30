from datetime import datetime

from celery import shared_task

from dto.route import RoutePoint
from entity.route import RoutePointEntity
from ext import db
from gpxutil.utils.gdf_handler import GDFListHandler


@shared_task(ignore_result=False)
def set_route_point_area_task(route_point_id: int):
    point_entity = db.session.query(RoutePointEntity).filter(RoutePointEntity.id == route_point_id, RoutePointEntity.is_deleted == False).first()
    point_dto: RoutePoint = point_entity.to_dto()
    point_dto.set_area(GDFListHandler().list, True)
    point_entity.province = point_dto.province
    point_entity.city = point_dto.city
    point_entity.area = point_dto.area
    # point_entity.province_en = point_dto.province_en
    # point_entity.city_en = point_dto.city_en
    # point_entity.area_en = point_dto.area_en
    point_entity.update_time = datetime.now()
    db.session.commit()