from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum

from datetime import datetime
db = SQLAlchemy() 


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(200))
    model = db.Column(db.String(100))  # Car model
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'admin' or 'user'
    
    # One-to-Many: User → ReserveParking
    reservations = db.relationship('ReserveParking', backref='user', cascade="all, delete", passive_deletes=True)


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

from datetime import datetime

class ReserveParking(db.Model):
    __tablename__ = 'reserveparking'

    id = db.Column(db.Integer, primary_key=True)

    spot_id = db.Column(db.Integer, db.ForeignKey('parkingspot.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)

    parking_cost = db.Column(db.Float, nullable=True)  # cost is calculated after release
