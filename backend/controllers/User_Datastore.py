

from flask_security import SQLAlchemyUserDatastore
from data.models import User, Role, db

user_datastore = SQLAlchemyUserDatastore(db, User, Role)

