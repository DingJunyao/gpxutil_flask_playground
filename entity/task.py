from datetime import datetime

from ext import db


class TaskEntity(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    create_user = db.Column(db.Integer, default=0)
    update_user = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    task_type = db.Column(db.String(50))
    ref_type = db.Column(db.String(50))
    ref_id = db.Column(db.Integer)
    # 0: pending, 1: completed, -1: failed
    status = db.Column(db.Integer, default=0)
    result = db.Column(db.Text)

class SubTaskEntity(db.Model):
    __tablename__ = 'sub_tasks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now)
    create_user = db.Column(db.Integer, default=0)
    update_user = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    celery_task_id = db.Column(db.String(100))
    ref_type = db.Column(db.String(50))
    ref_id = db.Column(db.Integer)
    # 0: pending, 1: completed, -1: failed
    status = db.Column(db.Integer, default=0)
    result = db.Column(db.Text)

    parent_task = db.relationship('TaskEntity', backref=db.backref('sub_tasks'))