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
    
    # Mail settings
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USER")
    MAIL_PASSWORD = os.getenv("MAIL_PASS")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USER")

    # Redis Cache
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "localhost"
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 1
    CACHE_REDIS_URL = "redis://localhost:6379/1"
    CACHE_DEFAULT_TIMEOUT = 60






class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, 'data')
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "parking.db")
    
    DEBUG = True
    SECRET_KEY = "errrtyshnab@%$#Y^rx4z567a8q2ik3edjhxgre34567"

    # JWT
    JWT_SECRET_KEY = SECRET_KEY
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_IDENTITY_CLAIM = "sub"
    JWT_ERROR_MESSAGE_KEY = "message"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

    # Flask-Security
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "#@ewe65reds56"
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = False
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_USERNAME_ENABLE = True
    SECURITY_USERNAME_REQUIRED = True
    SECURITY_UNAUTHORIZED_VIEW = None
    SECURITY_TRACKABLE = True
    SECURITY_RECOVERABLE = True

    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False

