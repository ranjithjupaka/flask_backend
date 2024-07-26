import os

from flask import Flask, request, jsonify
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from flask_cors import CORS

import config

app = Flask(__name__)
CORS(app)

port = int(os.environ.get("PORT", 8000))

client = MongoClient(config.DB_URL)
db = client['telegram_game']
users_collection = db['users']
characters_collection = db['characters']

characters = [
    {'name': 'Jellyfish', 'coins': 2000, 'purchased': False, 'level': 0},
    {'name': 'Mr Crabs', 'coins': 4000, 'purchased': False, 'level': 0},
    {'name': 'Minnows', 'coins': 6000, 'purchased': False, 'level': 0},
    {'name': 'Neon Tetra', 'coins': 8000, 'purchased': False, 'level': 0},
    {'name': 'Angelfish', 'coins': 10000, 'purchased': False, 'level': 0},
    {'name': 'Clownfish', 'coins': 12000, 'purchased': False, 'level': 0},
    {'name': 'Dogfish', 'coins': 14000, 'purchased': False, 'level': 0},
    {'name': 'Baby Shark', 'coins': 16000, 'purchased': False, 'level': 0},
    {'name': 'Octopus', 'coins': 18000, 'purchased': False, 'level': 0},
    {'name': 'Parrotfish', 'coins': 20000, 'purchased': False, 'level': 0},
]


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json

    user = users_collection.find_one({"telegram_id": data['telegram_id']})

    if not user:
        user = {
            'telegram_id': data['telegram_id'],
            'username': data.get('username'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'coins': 0,
            'cur_character': 0,
            'cur_level': 0,
            'characters': characters
        }
        result = users_collection.insert_one(user)
        return jsonify({"message": "User created successfully", "id": str(result.inserted_id)}), 201
    else:
        return jsonify({"message": "User exists Already"}), 201


@app.route('/user/<int:telegram_id>', methods=['GET'])
def get_user(telegram_id):
    user = users_collection.find_one({"telegram_id": telegram_id})
    if user:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        return jsonify(user)
    return jsonify({"message": "User not found"}), 404


@app.route('/user/<int:telegram_id>', methods=['PUT'])
def update_user(telegram_id):
    data = request.json
    update_data = {
        "coins": data.get('coins'),
        "character": data.get('character'),
        "level": data.get('level')
    }
    if data.get("coins"):
        update_data["coins"] = data.get("coins")

    if data.get("character"):
        update_data["character"] = data.get("character")

    if data.get("level"):
        update_data["coins"] = data.get('coins')

    print(update_data, 'update_data')

    result = users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": update_data}
    )
    if result.matched_count:
        return jsonify({"message": "User updated successfully"})
    return jsonify({"message": "User not found"}), 404


@app.route('/users/by-coins', methods=['GET'])
def get_users_by_coins():
    min_coins = int(request.args.get('min_coins', 0))
    limit = int(request.args.get('limit', 10))

    users = users_collection.find(
        {"coins": {"$gte": min_coins}},
        {"_id": 0}  # Exclude _id field from results
    ).sort("coins", DESCENDING).limit(limit)

    user_list = list(users)
    return jsonify(user_list)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=port)
