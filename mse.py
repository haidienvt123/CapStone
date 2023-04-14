import cv2
import numpy as np

def mse(img1, img2):
   h, w = img1.shape
   img2_resize = cv2.resize(img2,(w*5,h*5))
   img1_resize = cv2.resize(img1,(w*5,h*5))
   cv2.imwrite('bw_4.png',img2_resize)  
   cv2.imwrite('bw_5.png',img1_resize)  
   diff = np.subtract(img1_resize, img2_resize)
   err = np.sum(diff**2)
   mse = err/(float(h*w))    
   cv2.imwrite('bw_6.png',diff)     
   return mse

img1 = cv2.imread('bw_3_3.png')
img2 = cv2.imread('bw_3_4.png')
img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
error = mse(img2,img1)
print(error)