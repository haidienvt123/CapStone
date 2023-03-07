import cv2 
from src.yolov7.plate_detector import ScreenDetector
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
from src.bp_monitor import combine_boxes
import os

db_template = pd.read_parquet("./config/template.parquet")
LIST_DEVICE = db_template["deviceName"].tolist()
# DEVICE_TYPE = db_template["deviceType"]

screen_detector = ScreenDetector.getInstance()
text_detector = TextDetector.getInstance()
# text_detector = PaddleTextDetector.getInstance()
direction_detector = PaddleTextAngleClassifier.getInstance()
text_recognizer = PaddleTextRecognizer.getInstance()

# ==============================================================================
# Paddle Function
def get_rotate_crop_image(img, points):
    '''
    img_height, img_width = img.shape[0:2]
    left = int(np.min(points[:, 0]))
    right = int(np.max(points[:, 0]))
    top = int(np.min(points[:, 1]))
    bottom = int(np.max(points[:, 1]))
    img_crop = img[top:bottom, left:right, :].copy()
    points[:, 0] = points[:, 0] - left
    points[:, 1] = points[:, 1] - top
    '''
    assert len(points) == 4, "shape of points must be 4*2"
    img_crop_width = int(
        max(
            np.linalg.norm(points[0] - points[1]),
            np.linalg.norm(points[2] - points[3])))
    img_crop_height = int(
        max(
            np.linalg.norm(points[0] - points[3]),
            np.linalg.norm(points[1] - points[2])))
    pts_std = np.float32([[0, 0], [img_crop_width, 0],
                          [img_crop_width, img_crop_height],
                          [0, img_crop_height]])
    M = cv2.getPerspectiveTransform(points, pts_std)
    dst_img = cv2.warpPerspective(
        img,
        M, (img_crop_width, img_crop_height),
        borderMode=cv2.BORDER_REPLICATE,
        flags=cv2.INTER_CUBIC)
    dst_img_height, dst_img_width = dst_img.shape[0:2]
    if dst_img_height * 1.0 / dst_img_width >= 1.5:
        dst_img = np.rot90(dst_img)
    return dst_img

def add_label2img(image, display_text, x, y):
    thickness = 2
    fontScale = 1
    if min(image.shape[:2]) < 150:
        fontScale = 0.5
    result_img = cv2.putText(image, display_text, (x, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0,200,0), thickness, cv2.LINE_AA)
    return result_img

# ==============================================================================

folder_path = "./test/total/"
with open("./eval_label.txt", 'r') as f:
    total_label = f.read()
    total_label = total_label.splitlines()

total_checkme = 0
total_omron = 0
total_led = 0

for label in total_label:
    fname, device, value = label.split("\t")
    if "heckme" in device:
        total_checkme += 1
    elif "7600T" in device:
        total_omron += 1
    else:
        total_led += 1

miss = 0
wrong = 0
total_precision = 0
checkme_p = 0
omron_p = 0
led_p = 0

# for idx, label in enumerate(os.listdir(folder_path)):
#     # print(idx/len(total_label))
#     fname, device, value = label.split("\t")
#     if fname not in os.listdir(folder_path):
#         continue
#     fpath = folder_path + label 
#     img = cv2.imread(fpath)

#     # if "1668678202154" not in fname:
#     #     continue

#     index = LIST_DEVICE.index(device.upper())
#     # device_type = DEVICE_TYPE[index]

#     img_screen = screen_detector.detect(img)
#     if img_screen is None:
#         # print(label)
#         cv2.imwrite('./result_eval/screen/' + label, img)
#     else:
#         continue
    
#     det = text_detector.detect(img_screen)
#     merge_bboxes = [list(map(lambda x: int(x), box)) for box in det]
#     aligned_img = screen_alignment(img_screen, merge_bboxes, direction_detector)
#     re_det = text_detector.detect(aligned_img)
#     margin_threshold = max(round(aligned_img.shape[0] / 100) + 1.5, 2)
#     merge_bboxes, value_text = combine_boxes(re_det, margin_threshold)

    # -------------------------------------------------------------------------------------------------
    # Paddle Text Flow
    # det = text_detector.detect(img_screen)
    # det = sorted_boxes(np.array(det))
    # img_crop_list = []
    # for box in det:
    #     img_crop = get_rotate_crop_image(aligned_img, box)
    #     img_crop_list.append(img_crop)
    
    # list_recognition = text_recognizer.detect(img_crop_list)
    # first_box = det[0]
    # first_box_point = [first_box[0][0], first_box[0][1], first_box[2][0], first_box[2][1]]
    # first_box_point = np.array(first_box_point).astype(np.int32)

    # imglabel, ang_result = screen_alignment(aligned_img, first_box_point, self.direction_detector)
    # for idx, box in enumerate(det):
    #     if list_recognition[idx][1] > 0.5:
    #         rotated_box = rotate_bbx(aligned_img, imglabel, ang_result, box)
    #         rotated_box = np.array(rotated_box).astype(np.int32).reshape(-1, 2)
    #         top_left = rotated_box[0]
    #         txt_label = list_recognition[idx][0]
    #         subresult, txt_label = rule_split_index(txt_label)
    #         imglabel = cv2.polylines(imglabel, [rotated_box], True, color=(255, 255, 0), thickness=2)
    #         imglabel = add_label2img(imglabel, txt_label, top_left[0], top_left[1])
    #         result += subresult
    # -------------------------------------------------------------------------------------------------


    # result = list(itertools.chain.from_iterable(value_text))
    # if len(result) > 3:
    #     result = result[len(result)-3:]
    # value = value.split(" ")
    # result = [str(x) for x in result]
    
    # if len(result) != len(value):
    #     print("MISS", fname, result, value)
    #     miss += 1
    #     cv2.imwrite('./result_eval/miss/' + fname, img)
    # else:
    #     flag = True 
    #     for x in value:
    #         if x not in result:
    #             flag = False 
        
    #     if flag == True:
    #         total_precision += 1
    #         if "heckme" in device:
    #             checkme_p += 1
    #         elif "7600T" in device:
    #             omron_p += 1
    #         else:
    #             led_p += 1
    #     else:
    #         print("WRONG", fname, result, value)
    #         cv2.imwrite('./result_eval/text/' + fname, img)
    #         wrong += 1

# print ('----------------------------------------')
# print('Total data: ', len(total_label))
# print('Total led 7:', total_led)
# print('Total checkme: ', total_checkme)
# print('Total omron: ', total_omron)

# print ('----------------------------------------')
# print("Accuracy total: ", total_precision)
# print("Accuracy led 7: ", led_p)
# print("Accuracy checkme: ", checkme_p)
# print("Accuracy omron: ", omron_p)

# print('----------------------------------------')
# print('Total miss: ', miss)
# print('Total wrong: ', wrong)

for img_name in os.listdir(folder_path):
    img=cv2.imread(folder_path+img_name)
    
    #yolov7 text detector
    det = text_detector.detect(img)
    merge_bboxes = [list(map(lambda x: int(x), box)) for box in det]
    aligned_img = screen_alignment(img, merge_bboxes, direction_detector)
    re_det = text_detector.detect(aligned_img)
    margin_threshold = max(round(aligned_img.shape[0] / 100) + 1.5, 2)
    merge_bboxes, value_text = combine_boxes(re_det, margin_threshold)
    with open('yolo.txt','w') as h:
        h.write(str(det))

    #Paddle Text Flow
    det_paddle = text_detector.detect(img)
    det_paddle = sorted_boxes(np.array(det_paddle))
    # img_crop_list = []
    # for box in det_paddle:
    #     img_crop = get_rotate_crop_image(aligned_img, box)
    #     img_crop_list.append(img_crop)
    with open('paddle.txt','w') as h:
        h.write(str(det_paddle))

