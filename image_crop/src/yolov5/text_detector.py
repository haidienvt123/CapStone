import os
import sys
import torch
import numpy as np
from pathlib import Path

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import (check_img_size, non_max_suppression)
from utils.torch_utils import select_device

class TextDetector(object):
  __instance__ = None

  @staticmethod
  def getInstance():
      """ Static access method. """
      if TextDetector.__instance__ == None:
          TextDetector()
      return TextDetector.__instance__

  def __init__(self,
              weights='./model/text_detection/best.pt',  # model weights
              data="",  # dataset.yaml path
              imgsz=(416, 416),  # inference size (height, width) 
              agnostic_nms=False,  # class-agnostic NMS
              augment=False,  # augmented inference
              classes=None,  # filter by class: --class 0, or --class 0 2 3
              device='cpu',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
              conf_thres=0.6,  # confidence threshold
              iou_thres=0.2,  # NMS IOU threshold
              dnn=False,  # use OpenCV DNN for ONNX inference
              half=False,  # use FP16 half-precision inference
              max_det=1000  # maximum detections per image
              ):
    
    if TextDetector.__instance__ != None:
      raise Exception("Text Detector is a singleton!")
    else:
      TextDetector.__instance__ = self

      self.augment = augment
      self.conf_thres = conf_thres
      self.iou_thres = iou_thres
      self.classes = classes
      self.agnostic_nms = agnostic_nms
      self.max_det = max_det

      # Load model
      bs = 1  # batch_size
      self.device = select_device(device)
      self.model = DetectMultiBackend(weights, device=self.device, dnn=dnn, data=data, fp16=half)
      self.stride, self.pt = self.model.stride, self.model.pt
      self.imgsz = check_img_size(imgsz, s=self.stride)  # check image sizes
      self.model.warmup(imgsz=(1 if self.pt else bs, 3, *self.imgsz))

    
  def detect(self, img):
    '''
    This function detects the text within an image
    Input: cv2 image (Screen cropped image)
    Output: det (list of object coordinates, confidence and class)
    '''
    # Padded resize
    img = letterbox(img, self.imgsz, stride=self.stride, auto=self.pt)[0]

    # Convert
    img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
    img = np.ascontiguousarray(img)

    # Run inference
    img = torch.from_numpy(img).to(self.device)
    img = img.half() if self.model.fp16 else img.float()  # uint8 to fp16/32
    img /= 255  # 0 - 255 to 0.0 - 1.0
    if len(img.shape) == 3:
      img = img[None]  # expand for batch dim

    # Inference
    pred = self.model(img, augment=self.augment)

    # NMS
    pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, self.classes, self.agnostic_nms, max_det=self.max_det)

    return pred[0], img.shape
