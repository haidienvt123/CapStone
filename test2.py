from fastapi import FastAPI 
import pymongo
import io

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["garage"]
col = db["info"]
result=[]
query = col.find({},{"_id": 0})
for i in query:
    result.append(i)

    
app = FastAPI()

@app.get("/")
def home():
    return result

@app.get("/get_id")
def get_id(id_card: str | None = '3'):
    query = col.find_one({"id_card": id_card},{"_id": 0})
    return query