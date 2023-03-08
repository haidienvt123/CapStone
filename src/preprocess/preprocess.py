import cv2
import imutils
import numpy as np
from rembg import remove as rembg
from itertools import combinations
from scipy.spatial import distance as dist


APPROX_POLY_DP_ACCURACY_RATIO = 0.02
IMG_RESIZE_H = 1000.0

def cross_point(line1, line2):
    x = 0
    y = 0
    x1 = line1[0]
    y1 = line1[1]
    x2 = line1[2]
    y2 = line1[3]
    x3 = line2[0]
    y3 = line2[1]
    x4 = line2[2]
    y4 = line2[3]
    if (x2 - x1) == 0:
        k1 = None
    else:
        k1 = (y2 - y1) * 1.0 / (x2 - x1)
        b1 = y1 * 1.0 - x1 * k1 * 1.0
    if (x4 - x3) == 0:
        k2 = None
        b2 = 0
    else:
        k2 = (y4 - y3) * 1.0 / (x4 - x3)
        b2 = y3 * 1.0 - x3 * k2 * 1.0
    if k1 is None:
        if not k2 is None:
            x = x1
            y = k2 * x1 + b2
    elif k2 is None:
        x = x3
        y = k1 * x3 + b1
    elif not k2 == k1:
        x = (b2 - b1) * 1.0 / (k1 - k2)
        y = k1 * x * 1.0 + b1 * 1.0

    return [x, y]


def get_angle(sta_point, mid_point, end_point):
    ma_x = sta_point[0][0] - mid_point[0][0]
    ma_y = sta_point[0][1] - mid_point[0][1]
    mb_x = end_point[0][0] - mid_point[0][0]
    mb_y = end_point[0][1] - mid_point[0][1]
    ab_x = sta_point[0][0] - end_point[0][0]
    ab_y = sta_point[0][1] - end_point[0][1]
    ab_val2 = ab_x * ab_x + ab_y * ab_y
    ma_val2 = ma_x * ma_x + ma_y * ma_y
    mb_val2 = mb_x * mb_x + mb_y * mb_y
    cos_M = (ma_val2 + mb_val2 - ab_val2) / (2 * np.sqrt(ma_val2) * np.sqrt(mb_val2))
    angleAMB = np.arccos(cos_M) / np.pi * 180
    return angleAMB


def order_points(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    (br, tr) = rightMost[np.argsort(D)[::-1], :]

    return np.array([tl, tr, br, bl], dtype = "float32")


def four_point_transform(image, pts):
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype = "float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    return warped


def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)

    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation = inter)

    return resized


def align_screen(img):
    # orig for debug
    orig = cv2.copyMakeBorder(img, 200, 200, 200, 200, cv2.BORDER_CONSTANT, value=0)
    img = rembg(img, False, 10, 10)
    
    # padding to avoid wrong Hougline
    img = cv2.copyMakeBorder(img, 200, 200, 200, 200, cv2.BORDER_CONSTANT, value=0)

    # resize to reduce processing time
    img = imutils.resize(img, height=int(IMG_RESIZE_H))
    orig = imutils.resize(orig, height=int(IMG_RESIZE_H))
    _, img = cv2.threshold(img[:, :, 3], 10, 255, cv2.THRESH_BINARY)

    # define kernel
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    # apply blur to smooth shape
    img = cv2.medianBlur(img, 15)

    edges = cv2.Canny(img, 50, 150, apertureSize=3)

    lines = cv2.HoughLines(edges, 1, np.pi/180, 20)

    for r_theta in lines:
        arr = np.array(r_theta[0], dtype=np.float64)
        r, theta = arr
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*r
        y0 = b*r
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

    intersect_shape = 0
    strong_lines = np.zeros([4, 1, 2])
    for intersect_line in range(0, len(lines)):
        if intersect_shape == 4:
            break
        for rho, theta in lines[intersect_line]:
            if intersect_line == 0:
                strong_lines[intersect_shape] = lines[intersect_line]
                intersect_shape = intersect_shape + 1
            else:
                c1 = np.isclose(abs(rho), abs(strong_lines[0:intersect_shape, 0, 0]), atol=80)
                c2 = np.isclose(np.pi - theta, strong_lines[0:intersect_shape, 0, 1], atol=np.pi / 36)
                c = np.all([c1, c2], axis=0)
                if any(c):
                    continue
                closeness_rho = np.isclose(rho, strong_lines[0:intersect_shape, 0, 0], atol=40)
                closeness_theta = np.isclose(theta, strong_lines[0:intersect_shape, 0, 1], atol=np.pi / 36)
                closeness = np.all([closeness_rho, closeness_theta], axis=0)
                if not any(closeness) and intersect_shape < 4 and theta != 0:
                    strong_lines[intersect_shape] = lines[intersect_line]
                    intersect_shape = intersect_shape + 1
    # draw strong lines
    lines1 = np.zeros((len(strong_lines), 4), dtype=int)
    for i in range(0, len(strong_lines)):
        rho, theta = strong_lines[i][0][0], strong_lines[i][0][1]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        lines1[i][0] = int(x0 + 1000 * (-b))
        lines1[i][1] = int(y0 + 1000 * (a))
        lines1[i][2] = int(x0 - 1000 * (-b))
        lines1[i][3] = int(y0 - 1000 * (a))

    approx = np.zeros((len(strong_lines), 1, 2), dtype=int)
    index = 0
    combs = list((combinations(lines1, 2)))
    point_list = []
    for twoLines in combs:
        x1, y1, x2, y2 = twoLines[0]
        x3, y3, x4, y4 = twoLines[1]
        [x, y] = cross_point([x1, y1, x2, y2], [x3, y3, x4, y4])
        if 0 < x < orig.shape[1] and 0 < y < orig.shape[0] and index < 4:
            point_list.append((int(x), int(y)))
            approx[index] = (int(x), int(y))
            index = index + 1

    # final output
    wrap_img = four_point_transform(orig, approx.reshape(4, 2))

    return wrap_img

def rotate(point, radians, origin):
    x, y = point
    offset_x, offset_y = origin
    adjusted_x = (x - offset_x)
    adjusted_y = (y - offset_y)
    cos_rad = np.cos(radians)
    sin_rad = np.sin(radians)
    qx = offset_x + cos_rad * adjusted_x + sin_rad * adjusted_y
    qy = offset_y + -sin_rad * adjusted_x + cos_rad * adjusted_y
    return qx, qy

def rotate_bbx(original_image, rotated_image, angle, box):
    h, w = original_image.shape[:2]
    h_new, w_new = rotated_image.shape[:2]
    xoffset, yoffset = (w_new - w)/2, (h_new - h)/2
    origin = (w/2, h/2)

    result_box = []
    for point in box:
        x, y = rotate([point[0], point[1]], np.radians(angle), origin)
        x, y = x + xoffset, y + yoffset
        result_box.append([x,y])
    result_box = np.array(result_box, dtype=np.float32)
    return result_box

def screen_alignment(original_image, boxes, direction_detector):
    # Screen Alignment by average direction box
    image = original_image.copy()
    total_ang = []

    for box in boxes:
        crop_image = image[box[1]:box[3], box[0]:box[2]]
        angle = direction_detector.detect(crop_image)
        total_ang.append(angle)

    ang_result = np.mean(total_ang)
    image = imutils.rotate_bound(image, ang_result)
    # Build-in function imutils.rotate_bound use negative angle for rotate
    return image