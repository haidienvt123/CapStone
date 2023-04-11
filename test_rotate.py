import cv2
 
image = cv2.imread("lic.jpg")
gray =cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
ret,binary = cv2.threshold(gray,150,255,cv2.THRESH_BINARY)
contours,hierarchy = cv2.findContours(binary,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
print("Number of contours:" + str(len(contours)))
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
cv2.imwrite("bw.png",foreground)