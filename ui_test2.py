import requests
# import pymongo

# client = pymongo.MongoClient("mongodb://localhost:27017/")
# db = client["garage"]
# col = db["info"]
# query = col.find_one({"id_card": "3"},{"_id": 0})

query = {"id_card": "1", "lic": "00_00"}

url_del = 'http://127.0.0.1:8000/delete_data'
url_post = 'http://127.0.0.1:8000/post_data'
url_get_all = 'http://127.0.0.1:8000'
url_get = 'http://127.0.0.1:8000/get_id'

# x = requests.get(url_get, params={"id_card": "1"})

# x = requests.post(url_post, json=query)

# x = requests.delete(url_del, params = {'id_card': 1})
print(x.text)