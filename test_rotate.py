import cv2
import numpy as np
import sys

sys.setrecursionlimit(10000)

def label(ba,i,j):
    a,b = ba.shape
    if (i == a) or (i<-a) or (j==b) or (j<-b):
        return None
    if ba[i][j] == 0:
        ba[i][j] = 255
        label(ba,i-1,j)
        label(ba,i,j+1)
        label(ba,i,j-1)
        label(ba,i+1,j)
        # label(ba,i+1,j+1)
        # label(ba,i+1,j-1)
        # label(ba,i-1,j+1)
        # label(ba,i-1,j-1) 
    
def label_xy(ba,i,j,a,b,list_x,list_y):
    if (i == a) or (i<-a) or (j==b) or (j<-b):
        return None
    if ba[i][j] == 0:
        ba[i][j] = 255
        list_x.append(i)
        list_y.append(j)
        label_xy(ba,i-1,j,a,b,list_x,list_y)
        label_xy(ba,i,j+1,a,b,list_x,list_y)
        label_xy(ba,i,j-1,a,b,list_x,list_y)
        label_xy(ba,i+1,j,a,b,list_x,list_y)


def crop(bina):
    t=0
    list = []
    a,b = bina.shape
    bina_copy = bina.copy()
    for j in range(b):
        for i in range(a):
            if bina_copy[i][j] == 0:
                list_x=[]
                list_y=[]
                label_xy(bina_copy,i,j,a,b,list_x,list_y)
                x_max = max(list_x)
                x_min = min(list_x)
                y_max = max(list_y)
                y_min = min(list_y)
                # list.append([x_min,x_max,y_min,y_max])
                crop_img = bina[x_min-1:x_max+2, y_min-1:y_max+2]
                h,w = crop_img.shape
                if (12<h<18) and (3<w<11):
                    list.append(crop_img)
    return list

def change_color(bina):
    a,b = bina.shape
    for i in range(a):
        label(bina,i,0)
        label(bina,i,-1)
    for i in range(b):
        label(bina,0,i)
        label(bina,-1,i)
    return bina

def crop_num(image):
    gray =cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret,binary = cv2.threshold(gray,120,255,cv2.THRESH_BINARY)
    cv2.imwrite("bw_0.png",binary)
    bina = change_color(binary)
    cv2.imwrite("bw_1.png",bina)
    min_h = 10
    min_w = 6
    list = crop(bina)
    # dùng để cắt từng chữ nhưng không theo thứ tự và không lấy được thứ tự
    # # ret,binary = cv2.threshold(bina,100,255,cv2.THRESH_BINARY_INV)
    # # contours, hierarchy = cv2.findContours(binary, 
    # # cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # # mask = np.zeros_like(binary) # Create mask where white is what we want, black otherwise
    # # cv2.drawContours(mask, contours, 3, 255, -1) # Draw filled contour in mask
    # # out = np.zeros_like(binary) # Extract out the object and place into output image
    # # out[mask == 255] = binary[mask == 255]
    
    # # (y, x) = np.where(mask == 255)
    # # (topy, topx) = (np.min(y), np.min(x))
    # # (bottomy, bottomx) = (np.max(y), np.max(x))
    # # out = out[topy:bottomy+1, topx:bottomx+1]
    return list

img = cv2.imread('lic.jpg')
list_crop = crop_num(img)
for i in range(8):
    cv2.imwrite("bw_3_"+str(i)+".png",list_crop[i])

# img = cv2.imread('bw_1.jpg')
# img_crop = img[list_crop[0][0]:list_crop[0][1],list_crop[0][2]:list_crop[0][3]]
# cv2.imwrite("bw_3.png",img_crop)