import os
import sys
from pathlib import Path
from argparse import Namespace

FILE = Path(__file__).resolve()
ROOT = FILE.parents[2]  # project's root
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  #  relative path

from src.PaddleOCR.infer.predict_cls import TextClassifier

LABEL_LIST = ['-40', '-34', '-30', '-28', '-20', '-18', '-14', '-10',
                '-8', '-4', '-2', '0', '2', '4', '8', '10', '14', '18', 
                '20', '30', '40', '44', '50', '54', '60']

class PaddleTextAngleClassifier(TextClassifier):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if PaddleTextAngleClassifier.__instance__ == None:
            PaddleTextAngleClassifier()
        return PaddleTextAngleClassifier.__instance__

    def __init__(self):

        if PaddleTextAngleClassifier.__instance__ != None:
            raise Exception('Paddle Text Angle Classifier is a singleton!')
        else:
            PaddleTextAngleClassifier.__instance__ = self

            cls_args = Namespace(use_gpu=False,
                                ir_optim=True,
                                use_npu=False,
                                min_subgraph_size=15,
                                precision='fp32',
                                gpu_mem=500,
                                use_onnx=False,
                                use_tensorrt=False,
                                benchmark=False,
                                cls_model_dir="model/PaddleModel/text_direction",
                                cls_image_shape='3, 48, 192',
                                label_list=LABEL_LIST,
                                cls_batch_num=6,
                                cls_thresh=0.9,
                                use_xpu=False,
                                enable_mkldnn=False)

            TextClassifier.__init__(self, cls_args)

    def detect(self, img):
        img_list = []
        img_list.append(img)
        imgs, cls_res, pred_times = TextClassifier.__call__(self, img_list)
        degree = int(cls_res[0][0])
        return degree

