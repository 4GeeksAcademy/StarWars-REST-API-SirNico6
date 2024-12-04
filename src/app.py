"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, People, Favourite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users],), 200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'Error':'User not found'}), 404
    return jsonify(user.serialize()), 200

@app.route('/users/favourites', methods=['GET'])
def get_favourites():

    body = request.json
    if not body or 'user_id' not in body:
        return jsonify({"msg": "User ID is required"}), 400
    
    user_id = body.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    favourites = Favourite.query.filter_by(user_id=user_id).all()
    if not favourites:
        return jsonify({"msg": "There are no favourites"}), 404

    return jsonify([favourite.serialize() for favourite in favourites]), 200

@app.route('/people', methods=['GET'])
def get_people():
    all_people = People.query.all()
    return jsonify([people.serialize() for people in all_people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person_by_id(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({'Error':'Person not found'}), 404
    return jsonify(person.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({'Error':'Planet not found'}), 404
    return jsonify(planet.serialize()), 200

@app.route('/favourite/planet/<int:planet_id>', methods=['POST'])
def add_fav_planet(planet_id):
    body = request.json
    if not body or 'user_id' not in body:
        return jsonify({"msg": "User ID is required"}), 400
    
    user_id = body.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    planet = Planet.query.get(planet_id)
    if planet == None:
        return jsonify({"msg" : "Planet doesn't exist"}), 404
    
    new_favourite = Favourite(
        user_id = user.id,
        planet_id = planet_id
        )
    db.session.add(new_favourite)
    db.session.commit()

    return jsonify(new_favourite.serialize()), 201

@app.route('/favourite/planet/<int:planet_id>', methods=['DELETE'])
def delete_fav_planet(planet_id):
    body = request.json
    if not body or 'user_id' not in body:
        return jsonify({"msg": "User ID is required"}), 400
    
    user_id = body.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    planet = Planet.query.get(planet_id)
    if planet == None:
        return jsonify({"msg" : "Planet doesn't exist"}), 404
    
    favourite_delete = Favourite.query.filter_by(user_id=user_id, planet_id=planet.id).first()
    if favourite_delete == None:
        return jsonify({"msg" : "Favourite doesn't exist"}), 404
    db.session.delete(favourite_delete)
    db.session.commit()

    return jsonify({"msg" : "Favourite successfully deleted"}), 201

@app.route('/favourite/people/<int:people_id>', methods=['POST'])
def add_fav_people(people_id):
    
    body = request.json
    if not body or 'user_id' not in body:
        return jsonify({"msg": "User ID is required"}), 400
    
    user_id = body.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    people = People.query.get(people_id)
    if people == None:
        return jsonify({"msg" : "People doesn't exist"}), 404
    
    new_favourite = Favourite(
        user_id = user.id,
        people_id = people_id
        )
    db.session.add(new_favourite)
    db.session.commit()

    return jsonify(new_favourite.serialize()), 201

@app.route('/favourite/people/<int:people_id>', methods=['DELETE'])
def delete_favourite_people(people_id):
    body = request.json
    if not body or 'user_id' not in body:
        return jsonify({"msg": "User ID is required"}), 400
    
    user_id = body.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    
    people = People.query.get(people_id)
    if people == None:
        return jsonify({"msg" : "People doesn't exist"}), 404
    
    favourite_delete = Favourite.query.filter_by(user_id=user.id, people_id=people.id).first()
    if favourite_delete == None:
        return jsonify({"msg" : "Favourite doesn't exist"}), 404
    db.session.delete(favourite_delete)
    db.session.commit()

    return jsonify({"msg" : "Favourite successfully deleted"}), 201

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)