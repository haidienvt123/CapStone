from fastapi import FastAPI 
import pymongo
import uvicorn
from pydantic import BaseModel

class id_lic(BaseModel):
    id_card: str
    lic: str

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

@app.get("/get_id/{id_card}")
def get_id(id_card: str | None = '3'):
    query = col.find_one({"id_card": id_card},{"_id": 0})
    return query

@app.post("/post_data")
def post_data(data: id_lic):
    # add_data = []
    # add_data.append(data)
    # print(add_data)
    return data

@app.delete("/delete_data")
def delete_user(id_card: str):
    id = { "id_card": id_card}
    col.delete_one(id)
    return "Deleted"
    
if __name__ == "__main__":
    uvicorn.run(app)