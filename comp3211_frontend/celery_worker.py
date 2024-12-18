from flask import Flask
from app import create_app
from extensions import celery
import tasks  

flask_app = create_app()

def make_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

make_celery(flask_app)