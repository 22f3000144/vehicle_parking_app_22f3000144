import os
from datetime import timedelta

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
class Config:
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis and Celery Config
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    CELERY_TIMEZONE = "Asia/Kolkata"

    # Caching Config
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, 'data')
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "parking.db")
    SECRET_KEY = "errrtyshnab@%$#Y^rx4z567a8q2ik3edjhxgre34567"

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "#@ewe65reds56"

    # Flask-Security Config
    DEBUG = True
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_USERNAME_ENABLE = True
    SECURITY_USERNAME_REQUIRED = True
    SECURITY_UNAUTHORIZED_VIEW = None
    SECURITY_TRACKABLE = True
    SECURITY_RECOVERABLE = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False  # Keep False for local HTTP