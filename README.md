# GPXUtil Flask Playground

Web API backend for GPXUtil. Just a simple Flask app to serve the unfinished GPXUtil API.

## Preparation

MySQL and Redis are required.

Copy `config.example.yaml` to `config.yaml`, `server.example.py` to `server.py` and edit the config file.

Install dependencies:

```bash
pip install -r requirements.txt
```

See https://github.com/DingJunyao/gpxutil for more preparation.

## Run

```bash
flask --app server run
```

```bash
celery -A celery_app.celery_app worker --loglevel=INFO
# in Windows
celery -A celery_app.celery_app worker --loglevel=INFO  --pool=solo
# You can open many workers
```

## Thanks to

https://github.com/SoufSilence/coordTransform_py