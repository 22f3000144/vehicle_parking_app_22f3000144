from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_security import UserMixin, RoleMixin
from sqlalchemy import Enum
import uuid

db = SQLAlchemy()  



class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200))
    model = db.Column(db.String(100))  # Car model
    password = db.Column(db.String(255), nullable=False)

    unique_id = db.Column(db.String(250), unique=True, nullable=False)
    token_id = db.Column(db.String(250), unique=True, nullable=False)

    # 👇 Required by Flask-Security 4.x
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

    # Relationships
    reservations = db.relationship('ReserveParking', backref='user', cascade="all, delete", passive_deletes=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return f"<role {self.name}>"
    
class UserRole(db.Model):
    __tablename__ = 'userrole'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


    def __repr__(self):
        return f"<userrole user_id={self.user_id} role_id={self.role_id}>"



class ParkingLot(db.Model):
    __tablename__ = 'parkinglot'
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    max_spot = db.Column(db.Integer, nullable=False)

    # One-to-Many: ParkingLot → ParkingSpot
    spots = db.relationship('ParkingSpot', backref='lot', cascade='all, delete-orphan', passive_deletes=True)

class ParkingSpot(db.Model):
    __tablename__ = 'parkingspot'

    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(Enum('A', 'O', name='spot_status'), default='A', nullable=False)
    # One-to-Many: ParkingSpot → ReserveParking
    reservations = db.relationship('ReserveParking', backref='spot', cascade="all, delete", passive_deletes=True)



class ReserveParking(db.Model):
    __tablename__ = 'reserveparking'

    id = db.Column(db.Integer, primary_key=True)

    spot_id = db.Column(db.Integer, db.ForeignKey('parkingspot.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)

    parking_cost = db.Column(db.Float, nullable=True)  # cost is calculated after release

    def __repr__(self):
        return f"<ReserveParking id={self.id} user_id={self.user_id} spot_id={self.spot_id}>"