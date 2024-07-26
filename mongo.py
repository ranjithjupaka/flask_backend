from pymongo import MongoClient

import config

client = MongoClient(config.DB_URL)
db = client['telegram_game']
users_collection = db['users']
#
user = {
    'telegram_id': "1234",
    'username': "noobdev",
    'first_name': "ranjith",
    'last_name': "jupaka",
}
# result = users_collection.insert_one(user)
# print(result)

user = users_collection.find_one({"telegram_id": "1234"})
print(user)

result = users_collection.update_one(
    {"telegram_id": "1234"},
    {"$set": {
        "username": 'username',
        "first_name": 'first_name',
        "last_name": 'last_name'
    }}
)

user = users_collection.find_one({"telegram_id": "1234"})
print(user)

