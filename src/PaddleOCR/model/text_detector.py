from argparse import Namespace
import numpy as np
import cv2
from src.PaddleOCR.infer.predict_det import TextDetector
from src.PaddleOCR.infer.utility import get_rotate_crop_image

def sort_index(lst, rev=True):
    index = range(len(lst))
    s = sorted(index, reverse=rev, key=lambda i: lst[i])
    return s

class PaddleTextDetector(TextDetector):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if PaddleTextDetector.__instance__ == None:
            PaddleTextDetector()
        return PaddleTextDetector.__instance__

    def __init__(self):
        if PaddleTextDetector.__instance__ != None:
            raise Exception('Paddle Text Recognizer is a singleton!')
        else:
            PaddleTextDetector.__instance__ = self

            rec_args = Namespace(
                det_algorithm="DB",
                use_gpu=False,
                use_npu=False,
                use_xpu=False,
                gpu_mem=500,
                det_limit_side_len=960,
                det_limit_type="max",
                det_db_thresh=0.3,
                det_db_box_thresh=0.6,
                det_db_unclip_ratio=1.5,
                max_batch_size=10,
                use_dilation=False,
                det_db_score_mode="fast",
                det_model_dir="model/PaddleModel/ch_PP-OCRv3_det_infer",
                use_onnx=False,
                use_tensorrt=False,
                benchmark=False,
                enable_mkldnn=False
            )

            TextDetector.__init__(self, rec_args)

    def detect(self, img):
        infer_img = img.copy()
        det, _ = TextDetector.__call__(self, infer_img)
        if len(det):
            return det
        else:
            return None
