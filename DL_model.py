import cv2 
from src.yolov7.plate_detector import PlateDetector
from src.yolov7.car_detector import CarDetector
from src.yolov7.text_detector import TextDetector
from src.PaddleOCR.model.text_angle_classifier import PaddleTextAngleClassifier
from src.PaddleOCR.model.text_recognizer import PaddleTextRecognizer
from src.PaddleOCR.model.text_detector import PaddleTextDetector
from src.utils import vconcat_2_images, check_valid_image, calculate_list_distance
from src.preprocess.preprocess import screen_alignment, rotate_bbx#, rule_split_index
from src.postprocess.postprocess import sorted_boxes
from src.yolov7.utils.plots import save_one_box
import numpy as np
import itertools
import pandas as pd
import copy
from tensorflow import keras

class license_id():
   def __init__(self) -> None:
      #Initialize DL model
      self.plate_detetor=PlateDetector.getInstance()
      self.text_detector = PaddleTextDetector.getInstance()
      # self.direction_detector = PaddleTextAngleClassifier.getInstance()
      self.text_recognizer = PaddleTextRecognizer.getInstance()

   def crop_image(self,img,box):
      x=[]
      y=[]
      for i in box:
         x.append(int(i[0]))
         y.append(int(i[1]))
      crop_img=img[min(y):max(y),min(x):max(x),:]
      return crop_img
   
   def license_detect(self,image):
      '''
      get the license info from image
      input: numpy ndarray
      output: str of id and confidence, image with bbox, crop image of plate license
      '''
      img=copy.deepcopy(image)
      cordinate=self.plate_detetor.detect(img)
      # crop = save_one_box(cordinate, img, BGR=True, save=False)

      if cordinate is not None:
         crop = save_one_box(cordinate, img, BGR=True, save=False)
         # Paddle Text Flow
         det = self.text_detector.detect(crop)
         det_ = self.text_detector.detect(img)

         img_crop_list = []
         if det is not None or det_ is not None:
            for box in det:
               img_crop = self.crop_image(crop, box)
               img_crop_list.append(img_crop)

            list_recognition = self.text_recognizer.detect(img_crop_list)
            if len(list_recognition)<2:
               temp=list_recognition[0][0].split('-')
               list_recognition=[(str(temp[1]),1),(str(temp[0]),1)] #testing
         else:
            list_recognition = ['0','0']

         bbox_image=copy.deepcopy(img)
         cv2.rectangle(bbox_image,(int(cordinate[0]),int(cordinate[1])),
                                    (int(cordinate[2]),int(cordinate[3])),
                                    color=(0,255,0),thickness=3)
      else:
         # Paddle Text Flow
         det = self.text_detector.detect(img)

         img_crop_list = []
         if det is None:
            list_recognition = ['0','0']
         else:
            for box in det:
               img_crop = self.crop_image(img, box)
               img_crop_list.append(img_crop)

            list_recognition = self.text_recognizer.detect(img_crop_list)

         bbox_image,crop=(img,img)

      return list_recognition,bbox_image,crop
   
class car_detector():
   def __init__(self) -> None:
      #Initialize DL model
      self.car_detector = CarDetector.getInstance()

   def crop_image(self,img,box):
      x=[]
      y=[]
      for i in box:
         x.append(int(i[0]))
         y.append(int(i[1]))
      crop_img=img[min(y):max(y),min(x):max(x),:]
      return crop_img
   
   def car_detect(self,image):
      '''
      get the car only image from camera shot
      input: numpy ndarray
      output: image with bbox, crop image of car
      '''
      img=copy.deepcopy(image)
      cordinate=self.car_detector.detect(img)
      # crop = save_one_box(cordinate, img, BGR=True, save=False)

      if cordinate is not None:
         crop = save_one_box(cordinate, img, BGR=True, save=False)

         bbox_image=cv2.rectangle(img,(int(cordinate[0]),int(cordinate[1])),
                                    (int(cordinate[2]),int(cordinate[3])),
                                    color=(0,255,0),thickness=3)
      else:
         bbox_image,crop=(img,img)

      return bbox_image,crop
   
class color_detector():
   def __init__(self) -> None:
      self.model = keras.models.load_model('model/color_detector/vehicle_color_haze_free_model.h5')
      self.d_b={0: 'black',1:'blue',2:'gray',3:'green',4:'red',5:'white',6:'yellow'}
      
   def take_color(self,img):
      dim = (100,100)
      resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
      df = resized.astype('float32')
      df=df/255
      activations = self.model.predict(df.reshape(1,100,100,3))
      return self.d_b[np.argmax(activations[len(activations)-1])]
   
class Channel_value:
    val = -1.0
    intensity = -1.0

#Finding the pixel with the highest atmospheric light
def atmospheric_light(img, gray):
    top_num = int(img.shape[0] * img.shape[1] * 0.001)
    toplist = [Channel_value()] * top_num
    dark_channel = dark_channel_find(img)

    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            val = img.item(y, x, dark_channel)
            intensity = gray.item(y, x)
            for t in toplist:
                if t.val < val or (t.val == val and t.intensity < intensity):
                    t.val = val
                    t.intensity = intensity
                    break
    max_channel = Channel_value()
    for t in toplist:
        if t.intensity > max_channel.intensity:
            max_channel = t
    return max_channel.intensity

#Finding the dark channel i.e. the pixel with the lowest R/G/B value
def dark_channel_find(img):
    return np.unravel_index(np.argmin(img), img.shape)[2]

#Finding a coarse image which gives us a transmission map
def coarse(minimum, x, maximum):
    return max(minimum, min(x, maximum))

#Uses values from other functions to aggregate and give us a clear image
def dehaze(img, light_intensity, windowSize, t0, w):
    size = (img.shape[0], img.shape[1])

    outimg = np.zeros(img.shape, img.dtype)

    for y in range(size[0]):
        for x in range(size[1]):
            x_low = max(x-(windowSize//2), 0)
            y_low = max(y-(windowSize//2), 0)
            x_high = min(x+(windowSize//2), size[1])
            y_high = min(y+(windowSize//2), size[0])

            sliceimg = img[y_low:y_high, x_low:x_high]

            dark_channel = dark_channel_find(sliceimg)
            t = 1.0 - (w * img.item(y, x, dark_channel) / light_intensity)

            outimg.itemset((y,x,0), coarse(0, ((img.item(y,x,0) - light_intensity) / max(t, t0) + light_intensity), 255))
            outimg.itemset((y,x,1), coarse(0, ((img.item(y,x,1) - light_intensity) / max(t, t0) + light_intensity), 255))
            outimg.itemset((y,x,2), coarse(0, ((img.item(y,x,2) - light_intensity) / max(t, t0) + light_intensity), 255))
    return outimg


def dehaze_processing(img):
   img = np.array(img, dtype=np.uint8)
   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
   light_intensity = atmospheric_light(img, gray)
   w = 0.95
   t0 = 0.55
   outimg = dehaze(img, light_intensity, 20, t0, w)
   return outimg