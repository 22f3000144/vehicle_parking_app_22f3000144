from celery import Celery
from controllers.settings import LocalDevelopmentConfig

celery = Celery("parking_app")

celery.conf.update(
    broker_url=LocalDevelopmentConfig.CELERY_BROKER_URL,
    result_backend=LocalDevelopmentConfig.CELERY_RESULT_BACKEND,
    timezone="Asia/Kolkata",
    broker_connection_retry_on_startup=True
)

class ContextTask(celery.Task):
    """Task class that works with Flask app context."""
    def __call__(self, *args, **kwargs):
        from app import app
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask
