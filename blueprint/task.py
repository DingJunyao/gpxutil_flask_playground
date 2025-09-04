from functools import reduce

from celery.result import AsyncResult
from flask import Blueprint
import time

from loguru import logger

from entity.task import TaskEntity, SubTaskEntity
from ext import redis_client, db
from gpxutil.utils.process import threaded_map_list
from vo import Response

task_bp = Blueprint('task', __name__, url_prefix='/task')

@task_bp.route('/set_area/<int:route_id>', methods=['GET'])
def get_route_set_area_task_info(route_id: int):
    @threaded_map_list(desc="Load results", unit='point(s)')
    def load_result(point_id):
        result = AsyncResult(id=point_id)
        return result.ready(), result.successful()

    start_time = time.time()
    logger.info(f'START API')
    # set_area_task_id = f'route_set_area_{route_id}'
    # task_ids_text: bytes = redis_client.get(set_area_task_id)
    task_entity = db.session.query(TaskEntity).filter(TaskEntity.ref_id == route_id, TaskEntity.task_type == 'set_route_points_area', TaskEntity.is_deleted == False).first()
    # 查不到
    if not task_entity:
        resp = Response(code=404, message='Not found: maybe not started or finished', http_code=404)
        return resp.to_resp()

    # task_ids: list[str] = task_ids_text.decode('utf-8').split(',')
    # task_num = len(task_ids)
    # ready_num = 0
    # success_num = 0
    #
    # logger.info(f'BEFORE iter: {time.time() - start_time}')
    # results = load_result(task_ids)
    # ready_num = reduce(lambda x, y: x + 1 if y[0] else x, results, 0)
    # success_num = reduce(lambda x, y: x + 1 if y[1] else x, results, 0)
    # # for i in task_ids:
    # #     result = AsyncResult(i)
    # #     if result.ready():
    # #         ready_num += 1
    # #     if result.successful():
    # #         success_num += 1

    task_num = len(task_entity.sub_tasks)
    success_num = len([task for task in task_entity.sub_tasks if task.status == 1 and not task.is_deleted])
    error_sub_tasks = [task for task in task_entity.sub_tasks if task.status == 2 and not task.is_deleted]
    error_num = len(error_sub_tasks)
    if error_num > 0:
        error_info = [{'id': i.id, 'error_msg': i.result} for i in error_sub_tasks]
    else:
        error_info = []

    logger.info(f'END: {time.time() - start_time}')
    resp = Response(code=200, message='success', data={
        'task_num': task_num,
        'success_num': success_num,
        'error_num': error_num,
        'progress': (success_num + error_num) / task_num,
        'error_info': error_info
    })
    return resp.to_resp()