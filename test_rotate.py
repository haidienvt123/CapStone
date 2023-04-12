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
    
def label_xy(ba,i,j,a,b,x_min,x_max,y_min,y_max):
    if (i == a) or (i<-a) or (j==b) or (j<-b):
        return None
    if ba[i][j] == 0:
        ba[i][j] = 255
        _,_,_,_ = label_xy(ba,i-1,j,a,b,x_min,x_max,y_min,y_max)
        _,_,_,_ = label_xy(ba,i,j+1,a,b,x_min,x_max,y_min,y_max)
        _,_,_,_ = label_xy(ba,i,j-1,a,b,x_min,x_max,y_min,y_max)
        _,_,_,_ = label_xy(ba,i+1,j,a,b,x_min,x_max,y_min,y_max)
        if j < x_min:
            x_min = j
        if i < y_min:
            y_min = i
        if j > x_max:
            x_max = j
        if i > y_max:
            y_max = i
    return x_min,x_max,y_min,y_max

def crop(bina):
    t=0
    a,b = bina.shape
    bina_copy = bina.copy()
    for j in range(b):
        for i in range(a):
            if bina[i][j] == 0:
                x_min = 1000
                y_min = 1000
                x_max = 0
                y_max = 0
                x_min,x_max,y_min,y_max = label_xy(bina_copy,i,j,a,b,x_min,x_max,y_min,y_max)
                # print(x_min,x_max,y_min,y_max)
                t+=1
    print(t)
    return 0

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
    ret,binary = cv2.threshold(gray,100,255,cv2.THRESH_BINARY)
    cv2.imwrite("bw_0.png",binary)
    bina = change_color(binary)
    cv2.imwrite("bw_1.png",bina)
    # min_h = 10
    # min_w = 7
    # d=0
    # num = crop(bina)
    # for i in bina:
    #     for j in i:
    #         if j == 255:
    #             d+=1
    return bina

# img = cv2.imread('lic.jpg')
# crop_num(img)