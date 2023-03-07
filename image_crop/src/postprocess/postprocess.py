import cv2
import numpy as np
import copy
import logging
import re
from shapely.geometry import Polygon

def sorted_boxes(dt_boxes):
    """
    (From Paddle Source) Sort text boxes in order from top to bottom, left to right
    args:
        dt_boxes(array):detected text boxes
    return:
        sorted boxes(array)
    """
    num_boxes = dt_boxes.shape[0]
    sorted_boxes = sorted(dt_boxes, key=lambda x: (x[1], x[0]))
    _boxes = list(sorted_boxes)

    for i in range(num_boxes - 1):
        for j in range(i, 0, -1):
            if abs(_boxes[j + 1][1] < _boxes[j][1]) and \
                    (_boxes[j + 1][0] < _boxes[j][0]):
                tmp = _boxes[j]
                _boxes[j] = _boxes[j + 1]
                _boxes[j + 1] = tmp
            else:
                break
    return _boxes

def check_same_line(check_point, line):
    """
    Desc: Check boxes are in the same line
    Input: checkpoint and line
    Output: return True if same line else False
    """

    point_A, point_B = check_point

    K = (point_A[1] - point_B[1]) / (point_A[0] - point_B[0])

    f_U = (line[0][0] - point_A[0]) * K - (line[0][1] - 3 - point_A[1])
    f_T = (line[1][0] - point_A[0]) * K - (line[1][1] + 3 - point_A[1])

    return f_U * f_T < 0

def combine_boxes(det, margin_threshold = 3):
    dt_boxes = copy.deepcopy(det)
    dt_boxes = sorted_boxes(dt_boxes)
    dt_boxes = [list(map(lambda x: int(x), box)) for box in dt_boxes]

    clustered_boxes_by_lines = []
    check_point = []

    for box in dt_boxes:
        middle_left = (box[0], (box[1] + box[3]) / 2)
        middle_right = (box[2], (box[1] + box[3]) / 2)

        if not check_point:
            # first box
            check_point.append((middle_left, middle_right))
            clustered_boxes_by_lines.append([box])
        else:
            is_same_line = check_same_line(check_point[-1], ((box[0], box[1]), (box[0], box[3])))

            if is_same_line:
                clustered_boxes_by_lines[-1].append(box)
            else:
                # first box of this line. init
                clustered_boxes_by_lines.append([box])
            check_point.append((middle_left, middle_right))

    # combine
    new_dt_boxes = []
    for boxes_line in clustered_boxes_by_lines:
        boxes_line.sort(key=lambda x: x[0])
        check_point = [boxes_line[0]]
        for box in boxes_line[1:]:
            merge_margin = margin_threshold * 10
            left = box[0]
            top = box[1]
            right = box[2]
            bottom = box[3]

            left -= merge_margin
            top -= merge_margin
            right += merge_margin
            bottom += merge_margin

            is_intersect = intersect(check_point[-1], [left, top, right, bottom])
            if is_intersect:
                last_box = check_point.pop(-1)
                last_box[0] = min(last_box[0], box[0])
                last_box[1] = min(last_box[1], box[1])
                last_box[2] = max(last_box[2], box[2])
                last_box[3] = max(last_box[3], box[3])
                last_box[-1] = str(last_box[-1]) + str(box[-1])
                check_point.append(last_box)
            else:
                check_point.append(box)
        new_dt_boxes.append(check_point)
    
    result_box = []
    value_text = []
    for value_box in new_dt_boxes:
        result_box += value_box
        value_text += [rule_split_index(box[-1])[0] for box in value_box]
    return result_box, value_text

def intersect(bbx1, bbx2):
    # https://stackoverflow.com/questions/40795709/checking-whether-two-rectangles-overlap-in-python-using-two-bottom-left-corners
    point1 = Polygon([(bbx1[0], bbx1[1]), (bbx1[0], bbx1[3]), (bbx1[2], bbx1[3]), (bbx1[2], bbx1[1])])
    point2 = Polygon([(bbx2[0], bbx2[1]), (bbx2[0], bbx2[3]), (bbx2[2], bbx2[3]), (bbx2[2], bbx2[1])])
    
    intersection = point1.intersection(point2).area / point1.union(point2).area
    return intersection

def rule_split_index(number):
    result = []
    number = str(number)
    number = re.sub("[^0-9]", "",number)
    display_text = number
    if len(number) > 3:
        # https://stackoverflow.com/questions/10825926/python-3-x-rounding-behavior
        # bug python 3.x round(2.5)=2
        middle_point = round(len(number)/2 + 0.1)
        num_left = number[:middle_point]
        num_right = number[middle_point:]
        result.append(num_left)
        result.append(num_right)
        display_text = num_left + '/' + num_right
    else:
        result.append(number)
    return result, display_text