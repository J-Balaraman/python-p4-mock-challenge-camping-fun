from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    serialize_only = ('id', 'name', 'difficulty')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)

    signups = db.relationship('Signup', back_populates='activity', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Activity {self.id}: {self.name}>'


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'
    __table_args__ = (
        db.CheckConstraint('(age >= 8) and (age <= 18)', name='age_check'),
    )

    serialize_only = ('id', 'name', 'age')

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)

    signups = db.relationship('Signup', back_populates='camper', lazy=True, cascade="all, delete-orphan")

    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError("Camper must have a name.")
        return name
    
    @validates('age')
    def validate_age(self, key, age):
        if age < 8 or age > 18:
            raise ValueError('Please select an authorized age')
        return age
        
    
    def __repr__(self):
        return f'<Camper {self.id}: {self.name}>'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'
    __table_args__ = (
        db.CheckConstraint('(time >= 0) and (time <= 23)', name='time_check'),
    )
    
    serialize_only = ('id', 'time', 'camper_id', 'activity_id', 'activity', 'camper')

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), nullable=False)

    activity = db.relationship('Activity', back_populates='signups')
    camper = db.relationship('Camper', back_populates='signups')

    @validates('time')
    def validate_time(self, key, time):
        if time > 23 or time < 0:
            raise ValueError("Signup must have a proper time.")
        return time
    
    def __repr__(self):
        return f'<Signup {self.id}>'


# add any models you may need.
