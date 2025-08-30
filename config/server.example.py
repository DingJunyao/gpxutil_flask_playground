from urllib.parse import quote_plus as urlquote


class FlaskPlaygroundConfig:
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:{urlquote('I386i_Re45742@5')}@127.0.0.1:3306/flask?charset=utf8mb4"
    HOST = '0.0.0.0'
    JWT_SECRET_KEY = 'wfejioiuogasdfuierghaghujioaefrwawsefgijo'
    CELERY = dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        task_ignore_result=False,
    )
    REDIS_URL = "redis://localhost:6379/0"