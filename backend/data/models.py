from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_security import UserMixin, RoleMixin
from sqlalchemy import Enum
import uuid
from datetime import datetime

db = SQLAlchemy()


# USER & ROLE MODELS

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<Role {self.name}>"


# Association table for Flask-Security
class UserRole(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f"<UserRole user_id={self.user_id} role_id={self.role_id}>"


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    model = db.Column(db.String(100))  # Car model
    password = db.Column(db.String(255), nullable=False)
    # 👇 Required by Flask-Security 4.x
        # Required by Flask-Security
    active = db.Column(db.Boolean, default=True)

    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Relationships
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    reservations = db.relationship('ReserveParking', backref='user', cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return f"<User {self.username}>"



# PARKING MODELS

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'

    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    max_spot = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # One-to-Many: ParkingLot → ParkingSpot
    spots = db.relationship('ParkingSpot', backref='lot', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return f"<ParkingLot {self.prime_location_name}>"


class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id', ondelete='CASCADE'), nullable=False)
    spot_number = db.Column(db.Integer, nullable=False)   
    status = db.Column(db.String(1), default='A', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    entry_time = db.Column(db.DateTime)
    exit_time = db.Column(db.DateTime)
    def __repr__(self):
        return f"<ParkingSpot id={self.id} lot_id={self.lot_id} status={self.status}>"



class ReserveParking(db.Model):
    __tablename__ = 'reserve_parking'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Float, nullable=True)  # Calculated when released

    def __repr__(self):
        return f"<ReserveParking id={self.id} user_id={self.user_id} spot_id={self.spot_id}>"
