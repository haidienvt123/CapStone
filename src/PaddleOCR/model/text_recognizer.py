import os
import sys
from pathlib import Path
from argparse import Namespace

FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # project's root
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  #  relative path

from src.PaddleOCR.infer.predict_rec import TextRecognizer

class PaddleTextRecognizer(TextRecognizer):
    __instance__ = None

    @staticmethod
    def getInstance():
        """ Static access method """
        if PaddleTextRecognizer.__instance__ == None:
            PaddleTextRecognizer()
        return PaddleTextRecognizer.__instance__

    def __init__(self):

        if PaddleTextRecognizer.__instance__ != None:
            raise Exception('Paddle Text Recognizer is a singleton!')
        else:
            PaddleTextRecognizer.__instance__ = self

            rec_args = Namespace(rec_image_shape='3, 48, 320',
                                use_gpu=False,
                                ir_optim=True,
                                use_npu=False,
                                use_xpu=False,
                                min_subgraph_size=15,
                                precision='fp32',
                                gpu_mem=500,
                                rec_algorithm='SVTR_LCNet',
                                rec_model_dir="model/PaddleModel/en_PP-OCRv3_rec_infer",
                                rec_image_inverse=True,
                                rec_batch_num=6,
                                max_text_length=25,
                                rec_char_dict_path="src/PaddleOCR/ppocr/utils/dict.txt",
                                use_space_char=True,
                                vis_font_path="src/PaddleOCR/ppocr/utils/simfang.ttf",
                                drop_score=0.5,
                                use_onnx=False,
                                use_tensorrt=False,
                                benchmark=False,
                                enable_mkldnn=False)

            TextRecognizer.__init__(self, rec_args)

    def detect(self, img_list):
        res_list, _ = TextRecognizer.__call__(self, img_list)
        return res_list

