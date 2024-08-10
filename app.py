import os

from flask import Flask, request, jsonify
from pymongo import MongoClient, DESCENDING
from bson import ObjectId
from flask_cors import CORS

import config

app = Flask(__name__)
CORS(app)

client = MongoClient(config.DB_URL)
db = client['telegram_game']
users_collection = db['users']

characters = [
    {'name': 'Jellyfish', 'coins': 100,'level': 0, 'rate': 60},
    {'name': 'Mr Crabs', 'coins': 400,'level': 0, 'rate': 120},
    {'name': 'Minnows', 'coins': 600,'level': 0, 'rate': 180},
    {'name': 'Neon Tetra', 'coins': 800,'level': 0, 'rate': 240},
    {'name': 'Angelfish', 'coins': 1000,'level': 0, 'rate': 300},
    {'name': 'Clownfish', 'coins': 1200,'level': 0, 'rate': 360},
    {'name': 'Dogfish', 'coins': 1400,'level': 0, 'rate': 420},
    {'name': 'Baby Shark', 'coins': 1600,'level': 0, 'rate': 480},
    {'name': 'Octopus', 'coins': 1800,'level': 0, 'rate': 540},
    {'name': 'Parrotfish', 'coins': 2000,'level': 0, 'rate': 600},
]


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    user = {
        'telegram_id': data['telegram_id'],
        'username': data.get('username'),
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'coins': 0,
        'character': characters,
        'level': 0,
        'tickets':0
    }
    result = users_collection.insert_one(user)
    return jsonify({"message": "User created successfully", "id": str(result.inserted_id)}), 201


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
    update_data = {}

    if data.get("tickets"):
        update_data["tickets"] = data.get("tickets")

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
    app.run(debug=True,host='0.0.0.0',port=int(os.getenv('PORT', 8000)))
