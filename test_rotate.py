import cv2

def label(ba,i,j):
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

image = cv2.imread("lic.jpg")
gray =cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret,binary = cv2.threshold(gray,150,255,cv2.THRESH_BINARY)
contours,hierarchy = cv2.findContours(binary,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
min_x = 1000
min_y = 1000
max_x = 0
max_y = 0
for i in contours:
    x,y,w,h = cv2.boundingRect(i)
    if x < min_x:
        min_x = x
    if y < min_y:
        min_y = y
    if x+w > max_x:
        max_x = x+w
    if y+h > max_y:
        max_y = y+h
foreground = binary[min_y:max_y, min_x:max_x]
a,b = foreground.shape
label(foreground,0,0)
ret,bin = cv2.threshold(foreground,150,255,cv2.THRESH_BINARY_INV)
contours,hierarchy = cv2.findContours(bin,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
min_x = 1000
min_y = 1000
max_x = 0
max_y = 0
for i in contours:
    x,y,w,h = cv2.boundingRect(i)
    if x < min_x:
        min_x = x
    if y < min_y:
        min_y = y
    if x+w > max_x:
        max_x = x+w
    if y+h > max_y:
        max_y = y+h
foreground = bin[min_y:max_y, min_x:max_x]
cv2.imwrite("bw.png",foreground)