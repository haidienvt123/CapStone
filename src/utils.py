import cv2
import base64
import numpy as np
import torch
from PIL import Image

def load_image(image):
    pil_image = Image.open(image)
    exif1 = pil_image._getexif()

    if exif1 is not None and 274 in exif1:
        if exif1[274] == 3:
            pil_image=pil_image.rotate(180, expand=True)
        elif exif1[274] == 6:
            pil_image=pil_image.rotate(270, expand=True)
        elif exif1[274] == 8:
            pil_image=pil_image.rotate(90, expand=True)

    img = np.array(pil_image)
    if len(img.shape) != 3:
        raise ValueError('Image Error')

    if img.shape[2] < 3:
        raise ValueError('img.shape = %d != 3' % img.shape[2])
    
    if img.shape[2] == 4:
        #convert the image from BGRA2RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    else:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    return img 

def encode_image(image, cv=True):
    """
    input: cv2 image
    output: base64 encoded image
    """
    image = np.array(image)
    if cv:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    _, im_arr = cv2.imencode('.jpg', image)
    im_bytes = im_arr.tobytes()
    b64_string = base64.b64encode(im_bytes)
    image_base64 = b64_string.decode("utf-8")
    return image_base64

def decode_img(img_base64):
    """
    input: base64 encoded image
    output: cv2 image
    """
    img = img_base64.encode()
    img = base64.b64decode(img)
    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, flags=cv2.IMREAD_COLOR)
    return img

# define a function for horizontally 
# concatenating images of different
# heights 
def hconcat_resize(img_list, 
                   interpolation 
                   = cv2.INTER_CUBIC):
    # take minimum hights
    h_min = min(img.shape[0] 
                for img in img_list)
      
    # image resizing 
    im_list_resize = [cv2.resize(img,
                       (int(img.shape[1] * h_min / img.shape[0]),
                        h_min), interpolation
                                 = interpolation) 
                      for img in img_list]
      
    # return final image
    return cv2.hconcat(im_list_resize)

def clip_boxes(boxes, shape):
    # Clip boxes (xyxy) to image shape (height, width)
    if isinstance(boxes, torch.Tensor):  # faster individually
        boxes[:, 0].clamp_(0, shape[1])  # x1
        boxes[:, 1].clamp_(0, shape[0])  # y1
        boxes[:, 2].clamp_(0, shape[1])  # x2
        boxes[:, 3].clamp_(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2

def blur_detection(image, size=30, threshold=10):
    if max(image.shape[:2]) > 250:
        size = 20
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# grab the dimensions of the image and use the dimensions to
	# derive the center (x, y)-coordinates
    (h, w) = gray.shape
    (cX, cY) = (int(w / 2.0), int(h / 2.0))

    fft = np.fft.fft2(gray)
    fftShift = np.fft.fftshift(fft)

    # zero-out the center of the FFT shift (i.e., remove low
	# frequencies), apply the inverse shift such that the DC
	# component once again becomes the top-left, and then apply
	# the inverse FFT
    fftShift[cY - size:cY + size, cX - size:cX + size] = 0
    fftShift = np.fft.ifftshift(fftShift)
    recon = np.fft.ifft2(fftShift)

    # compute the magnitude spectrum of the reconstructed image,
    # then compute the mean of the magnitude values
    magnitude = 20 * np.log(np.abs(recon))
    mean = np.mean(magnitude)

    # the image will be considered "blurry" if the mean value of the
    # magnitudes is less than the threshold value
    blur_result = mean <= threshold

    return blur_result

def check_valid_image(image):
    """"
    Check image is not blur and detectable
    input: image, blur_detection para: {size, threshold}
    output: status
    """
    status = "200"
    if image is None:
        status = "461"
        return status

    check_blur = blur_detection(image)
    if check_blur:
        status = "465"

    return status

def vconcat_2_images(image1, image2):
    """"
    Desc: Concatenate 2 images with order from image1 to image2
    Input: image1, image2
    Output: Concatenated image
    """
    dw = image1.shape[1] / image2.shape[1]
    new_w = int(image2.shape[0]*dw)

    image2 = cv2.resize(image2, (image1.shape[1], new_w))
    result_img = cv2.vconcat([image1, image2])
    return result_img

def calculate_list_distance(list_combination):
    # Calculate distance in list pair
    all_dist = []
    for cluster in list_combination:
        pts_dist = []
        for idx_pt1 in range(len(cluster) - 1):
            for idx_pt2 in range(idx_pt1 + 1, len(cluster)):
                pt1 = np.array(cluster[idx_pt1])
                pt2 = np.array(cluster[idx_pt2])
                dist = np.linalg.norm(pt1 - pt2)
                pts_dist.append(dist)
        all_dist.append(pts_dist)
    all_dist = np.array(all_dist)
    return all_dist

def calculate_merging_threshold(det):
    length_array = []
    for box in det:
        bbx = box[:4]
        length = np.sqrt(pow(bbx[0] - bbx[2], 2) + pow(bbx[1] - bbx[3], 2))
        length_array.append(length)
    chosen_idx = np.argmax(np.array(length_array))
    chosen_box = det[chosen_idx][:4]
    length = chosen_box[2] - chosen_box[0]
    margin_threshold = int(length/10) + 1
    return margin_threshold