import cv2
import numpy as np

def mse(img1, img2):
   h, w = img1.shape
   img2_resize = cv2.resize(img2,(w*5,h*5))
   img1_resize = cv2.resize(img1,(w*5,h*5))
   diff = np.subtract(img1_resize, img2_resize)
   err = np.sum(diff**2)
   mse = err/(float(h*w))/25  
   if mse < 0.1: 
      return 1     
   return 0

img1 = cv2.imread('img/bw_5_4.png')
img2 = cv2.imread('img/bw_5_3.png')
img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
img1 = img1/255
img2 = img2/255
match = mse(img2,img1)
if match == 1:
   print("match")
else:
   print("not match")