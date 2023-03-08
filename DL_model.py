import cv2 
from src.yolov7.plate_detector import PlateDetector
from src.yolov7.text_detector import TextDetector
from src.PaddleOCR.model.text_angle_classifier import PaddleTextAngleClassifier
from src.PaddleOCR.model.text_recognizer import PaddleTextRecognizer
from src.PaddleOCR.model.text_detector import PaddleTextDetector
from src.utils import vconcat_2_images, check_valid_image, calculate_list_distance
from src.preprocess.preprocess import screen_alignment, rotate_bbx#, rule_split_index
from src.postprocess.postprocess import sorted_boxes
import numpy as np
import itertools
import pandas as pd
import copy

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
      try:
         crop,cordinate=self.plate_detetor.detect(img)

         # Paddle Text Flow
         det = self.text_detector.detect(crop)

         img_crop_list = []
         for box in det:
            img_crop = self.crop_image(crop, box)
            img_crop_list.append(img_crop)

         list_recognition = self.text_recognizer.detect(img_crop_list)

         bbox_image=cv2.rectangle(img,(int(cordinate[0]),int(cordinate[1])),
                                    (int(cordinate[2]),int(cordinate[3])),
                                    color=(0,255,0),thickness=3)
      except TypeError:
         list_recognition,bbox_image,crop=('0',img,img)

      return list_recognition,bbox_image,crop
   
