import pymongo
import io
from PIL import Image

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
    

  def add_id(self,id_card,lic,color,image1,image2):
    image_bytes_1 = io.BytesIO()
    image1.save(image_bytes_1, format='JPEG')
    image_bytes_2 = io.BytesIO()
    image2.save(image_bytes_2, format='JPEG')
    query = { "id_card": str(id_card), "lic": str(lic), "color": color, "image1": image_bytes_1.getvalue(), "image2": image_bytes_2.getvalue()}
    self.col.insert_one(query)

  def get_id(self,id_card):
    id = { "id_card": str(id_card)}
    query = self.col.find_one(id)
    lic = query["lic"]
    color = query["color"]
    image1 = Image.open(io.BytesIO(query['image1']))
    image2 = Image.open(io.BytesIO(query['image2']))
    return lic,color,image1,image2

  def del_id(self,id_card):
    id = { "id_card": str(id_card)}
    self.col.delete_one(id)

  