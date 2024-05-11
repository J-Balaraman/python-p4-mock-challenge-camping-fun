#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods=['GET', 'POST'])
def campers():
    if request.method == 'GET':
        campers = Camper.query.all()
        campers_json = [camper.to_dict() for camper in campers]
        return make_response(campers_json, 200)
    elif request.method == 'POST':
        try:
            json=request.get_json()
            new_camper = Camper(
                name=json['name'],
                age=json['age'],
            )
    
            db.session.add(new_camper)
            db.session.commit()
            message_dict = new_camper.to_dict()
            return make_response(message_dict, 201)
        except ValueError as e:
            error_message = str(e)
            return make_response({"errors": error_message}, 400)


@app.route('/campers/<int:id>', methods=['GET', 'PATCH'])
def campers_by_id(id):
    camper = Camper.query.filter(Camper.id == id).first()

    if camper is None:
        return make_response({"error": "Camper not found"}, 404)
    
    elif request.method == 'PATCH':
        json = request.get_json()
        try:
            # Attempt to update the camper's attributes
            for attr in json:
                setattr(camper, attr, json[attr])

            db.session.add(camper)
            db.session.commit()
            message_dict = camper.to_dict()

            return make_response(message_dict, 202)
        except ValueError as e:
            # Handle validation error
            return make_response({"errors": ["validation errors"]}, 400)
    
    elif request.method == 'GET':
        try:
            camper_data = camper.to_dict()
            camper_data['signups'] = [signup.to_dict() for signup in camper.signups]
            return make_response(camper_data, 200)
        except ValueError as e:
            error_message = str(e)
            return make_response({"errors": [error_message]}, 400)


@app.route('/activities', methods=['GET', 'POST'])
def activities():
    if request.method == 'GET':
        activities = Activity.query.all()
        activities_json = [activity.to_dict() for activity in activities]
        return make_response(activities_json, 200)
    elif request.method == 'POST':
        json=request.get_json()
        new_activity = Activity(
            name=json['name'],
            difficulty=json['difficulty'],
        )

        db.session.add(new_activity)
        db.session.commit()
        message_dict = new_activity.to_dict()
        return make_response(message_dict, 201)

@app.route('/activities/<int:id>', methods=['PATCH', 'DELETE'])
def activities_by_id(id):
    activity = Activity.query.filter(Activity.id == id).first()

    if activity == None:
        response_body = {
            "error": "Activity not found"
        }
        return make_response(response_body, 404)
    
    elif request.method == 'PATCH':
        json=request.get_json()
        for attr in json:
            setattr(activity, attr, json[attr])

        db.session.add(activity)
        db.session.commit()
        message_dict = activity.to_dict()

        return make_response(message_dict, 200)
    
    elif request.method == 'DELETE':
        db.session.delete(activity)
        db.session.commit()
        response_body = {
            "delete_successful": True,
            "message": "Message deleted."
        }

        return make_response(response_body, 204)

@app.route('/signups', methods=['POST'])
def signups():
    if request.method == 'POST':
        try:
            json=request.get_json()
            new_signup = Signup(
                camper_id=json['camper_id'],
                activity_id=json['activity_id'],
                time=json['time']
            )
    
            db.session.add(new_signup)
            db.session.commit()
            message_dict = new_signup.to_dict()
            return make_response(message_dict, 201)
        except ValueError as e:
            # Handle validation error
            return make_response({"errors": ["validation errors"]}, 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
