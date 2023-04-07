import requests
# import pymongo

# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["garage"]
# col = db["info"]
# query = col.find_one({"id_card": "3"},{"_id": 0})

query = {'id_card': '1', 'lic' : '00_00'}

url = 'http://127.0.0.1:8000/post_data'
x = requests.post(url, json= query)
print(x)