import pymongo

class database:
  def __init__(self):
    self.client = pymongo.MongoClient("mongodb://localhost:27017/")
    self.db = self.client["garage"]
    self.col = self.db["info"]

  def check_id(self,id_card):
    id = { "id_card": str(id_card)}
    query = self.col.find_one(id)
    # print(id)
    # print(query)
    return query
    

  def add_id(self,id_card,lic,color):
    query = { "id_card": str(id_card), "lic": str(lic), "color": color}
    self.col.insert_one(query)

  def get_id(self,id_card):
    id = { "id_card": str(id_card)}
    query = self.col.find_one(id)
    return query

  def del_id(self,id_card):
    id = { "id_card": str(id_card)}
    self.col.delete_one(id)

  