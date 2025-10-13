

from celery import Celery
from settings import LocalDevelopmentConfig

celery = Celery("parking_app")


class ContextTask(celery.Task):
    """Task class that works with Flask app context."""
    def __call__(self, *args, **kwargs):
        from app import app
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask
