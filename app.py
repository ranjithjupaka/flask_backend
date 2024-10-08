import os
import random
import string

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

# MANIFEST_URL = "https://your-app.com/tonconnect-manifest.json"
# ton_connect = TonConnect(MANIFEST_URL)

characters = [
    {'name': 'Minnows', 'coins': 1000, 'level': 0, 'rate': 100},
    {'name': 'Neon Tetra', 'coins': 2000, 'level': 0, 'rate': 250},
    {'name': 'Angelfish', 'coins': 5000, 'level': 0, 'rate': 600},
    {'name': 'Clownfish', 'coins': 7500, 'level': 0, 'rate': 800},
    {'name': 'Catfish', 'coins': 7500, 'level': 0, 'rate': 750},
    {'name': 'Dogfish', 'coins': 8000, 'level': 0, 'rate': 1100},
    {'name': 'Baby Shark', 'coins': 12000, 'level': 0, 'rate': 1300},
    {'name': 'Octopus', 'coins': 15000, 'level': 0, 'rate': 1700},
    {'name': 'Sad Clownfish', 'coins': 5000, 'level': 0, 'rate': 1500},
    {'name': 'Parrotfish', 'coins': 20000, 'level': 0, 'rate': 2500},
    {'name': 'Shrimp Cocktail', 'coins': 10000, 'level': 0, 'rate': 2000},
    {'name': 'Seahorse', 'coins': 40000, 'level': 0, 'rate': 3000},
    {'name': 'Mr Crabs', 'coins': 50000, 'level': 0, 'rate': 5000},
    {'name': 'Jellyfish', 'coins': 50000, 'level': 0, 'rate': 5500},
    {'name': 'Randy Cheeks', 'coins': 100000, 'level': 0, 'rate': 9000},
    {'name': 'Shooting Starfish', 'coins': 50000, 'level': 0, 'rate': 3000},
    {'name': 'Shark', 'coins': 120000, 'level': 0, 'rate': 6000},
    {'name': 'Harry Puffer', 'coins': 600000, 'level': 0, 'rate': 10000},
    {'name': 'Whale', 'coins': 3000000, 'level': 0, 'rate': 25000},
    {'name': 'Kraken', 'coins': 1000000, 'level': 0, 'rate': 27000},
]


def generate_random_string(length):
    alphanumeric_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(alphanumeric_chars) for _ in range(length))


@app.route('/user', methods=['POST'])
def create_user():
    data = request.json

    user_details = users_collection.find_one({"telegram_id": data['telegram_id']})

    if not user_details:
        ref_id = generate_random_string(6)
        user = {
            'telegram_id': data['telegram_id'],
            'username': data.get('username'),
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'ref_id': ref_id,
            'coins': 0,
            'characters': characters,
            'level': 0,
            'tickets': 0,
            'wallet': "",
            'refs': [],
            'max_energy': 1000,
            'coins_rate': 1,
            'refresh_rate': 1,
            'youtube_reward': False,
            'twitter_reward': False,
            'telegram_reward': False,
        }
        result = users_collection.insert_one(user)
        return jsonify({"message": "User created successfully", "id": str(result.inserted_id)}), 201
    else:
        return jsonify({"message": "User already exists "}), 400


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

    if data.get('max_energy'):
        update_data['max_energy'] = data.get('max_energy')

    if data.get('coins_rate'):
        update_data['coins_rate'] = data.get('coins_rate')

    if data.get('refresh_rate'):
        update_data['refresh_rate'] = data.get('refresh_rate')

    if data.get('youtube_reward'):
        update_data['youtube_reward'] = data.get('youtube_reward')

    if data.get('twitter_reward'):
        update_data['twitter_reward'] = data.get('twitter_reward')

    if data.get('telegram_reward'):
        update_data['telegram_reward'] = data.get('telegram_reward')

    if data.get("wallet"):
        update_data["wallet"] = data.get("wallet")

    if data.get("refs"):
        update_data["refs"] = data.get("refs")

    if data.get("tickets"):
        update_data["tickets"] = data.get("tickets")

    if data.get("coins"):
        update_data["coins"] = data.get("coins")

    if data.get("characters"):
        update_data["characters"] = data.get("characters")

    if data.get("level"):
        update_data["coins"] = data.get('coins')

    print(update_data, 'update_data')

    result = users_collection.update_one(
        {"telegram_id": telegram_id},
        {"$set": update_data}
    )

    # users_collection.update_one(
    #     {"telegram_id": telegram_id},
    #     {
    #         "$inc": {"coins": 50000},
    #     }
    # )

    if result.matched_count:
        return jsonify({"message": "User updated successfully"})
    return jsonify({"message": "User not found"}), 404


@app.route('/user/update-coins/<int:telegram_id>', methods=['PUT'])
def update_coins(telegram_id):
    data = request.json
    coins = data.get("coins")

    result = users_collection.update_one(
        {"telegram_id": telegram_id},
        {
            "$inc": {"coins": coins},
        }
    )

    if result.matched_count:
        return jsonify({"message": "User Coins updated successfully"})
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
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
