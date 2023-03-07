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

from src.yolov7.models.experimental import attempt_load
from src.yolov7.utils.datasets import letterbox
from src.yolov7.utils.general import check_img_size, non_max_suppression, scale_coords
from src.yolov7.utils.torch_utils import select_device, TracedModel

class TextDetector(object):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if TextDetector.__instance__ == None:
            TextDetector()
        return TextDetector.__instance__

    def __init__(self,
              weights='./model/text_detection/text_detect_14_12.pt',  # model weights
              data="",  # dataset.yaml path
              imgsz=(416, 416),  # inference size (height, width) 
              agnostic_nms=True,  # class-agnostic NMS
              augment=False,  # augmented inference
              classes=None,  # filter by class: --class 0, or --class 0 2 3
              device='cpu',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
              conf_thres=0.5,  # confidence threshold
              iou_thres=0.2,  # NMS IOU threshold
              dnn=False,  # use OpenCV DNN for ONNX inference
              half=False,  # use FP16 half-precision inference
              trace=False, # Traced Model
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
        self.half = half 

        # Load model
        self.device = select_device(device)
        self.model = attempt_load(weights, map_location=self.device)
        self.stride = int(self.model.stride.max())
        self.imgsz = check_img_size(imgsz[0], s=self.stride)  # check image sizes
        if trace:
            self.model = TracedModel(self.model, self.device, self.imgsz)
        if half:
            self.model.half()

    
    def detect(self, img):
        '''
        This function detects the text within an image
        Input: cv2 image (Screen cropped image)
        Output: det (list of object coordinates, confidence and class)
        '''
        img_org = img.copy()

        # Padded resize
        img = letterbox(img, self.imgsz, stride=self.stride)[0]

        # Convert
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)

        # Run inference
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim

        # Inference
        with torch.no_grad():
            pred = self.model(img, augment=self.augment)[0]

        # NMS
        pred = non_max_suppression(pred, self.conf_thres, self.iou_thres, self.classes, self.agnostic_nms)
        det = pred[0]
        
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img_org.shape)
            det = det.cpu().numpy()
            # Filter out SYS, DIA, PULSE
            det = np.array([detection for detection in det if int(detection[-1]) < 10])
            # Check detection after filter out
            if len(det):
                return det
        return None
