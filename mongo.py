import pymongo
import io
from PIL import Image
import base64

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
    img1 = base64.b64encode(image_bytes_1.getvalue()).decode()
    image_bytes_2 = io.BytesIO()
    image2.save(image_bytes_2, format='JPEG')
    img2 = base64.b64encode(image_bytes_2.getvalue()).decode()
    query = { "id_card": str(id_card), "lic": str(lic), "color": color, "image1": img1, "image2": img2}
    self.col.insert_one(query)

  def get_id(self,id_card):
    id = { "id_card": str(id_card)}
    query = self.col.find_one(id)
    lic = query["lic"]
    color = query["color"]
    image1_str = base64.b64decode(query['image1'])
    img1 = io.BytesIO(image1_str)
    image1 = Image.open(img1)
    image2_str = base64.b64decode(query['image2'])
    img2 = io.BytesIO(image2_str)
    image2 = Image.open(img2)
    return lic,color,image1,image2

  def del_id(self,id_card):
    id = { "id_card": str(id_card)}
    self.col.delete_one(id)
  