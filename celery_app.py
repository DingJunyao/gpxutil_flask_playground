from app import app

# 执行命令： celery -A celery_app.celery_app worker --loglevel=INFO  --pool=solo

# 从 Flask 应用获取 Celery 实例
celery_app = app.extensions['celery']

if __name__ == '__main__':
    celery_app.start()