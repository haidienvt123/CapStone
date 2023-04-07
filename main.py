import tkinter
import cv2
import time
import PIL.Image, PIL.ImageTk
import tkinter.messagebox
import serial
from mongo import database
import platform
from DL_model import license_id,car_detector,color_detector
import os

# video capture
class MyvideoCapture:
    def __init__(self,video_source):
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source",video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            frame = cv2.resize(frame,(640,480))
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret,None)

class App:
    def __init__(self, window, window_title,video_source_1,video_source_2, fpsLimit = 30):

        self.window = window
        self.window.title(window_title)
        self.fpsLimit = fpsLimit
        self.video_source_1 = video_source_1
        self.vid_1 = MyvideoCapture(video_source_1)    
        self.video_source_2 = video_source_2
        self.vid_2 = MyvideoCapture(video_source_2)  
        self.solution = 'Match'

        # Top Left
        self.live1 = tkinter.Canvas(window, width = self.vid_1.width, height = self.vid_1.height*0.8)
        self.live1.grid(row = 0, column = 0, pady = 2)

        # Top Right
        self.image1 = tkinter.Canvas(window, width = self.vid_1.width, height = self.vid_1.height*0.8)
        self.image1.grid(row = 0, column = 1, pady = 2)

        # Bot Left
        self.live2 = tkinter.Canvas(window, width = self.vid_2.width, height = self.vid_2.height*0.8)
        self.live2.grid(row = 1, column = 0,pady = 2)

        # Bot Right
        self.image2 = tkinter.Canvas(window, width = self.vid_2.width, height = self.vid_2.height*0.8)
        self.image2.grid(row = 1, column = 1, pady = 2)

        # Top Left Button - Open Door Button
        self.button_takeImage=tkinter.Button(window, text="Open Door if Not Match", width=50, command=self.openDoor_notMatch)
        self.button_takeImage.grid(row = 2, column = 0, pady = 2)

        # TOp Right Button - Match or not
        self.button_solution=tkinter.Button(window, text=self.solution, width=50, background='green', activebackground='green')
        self.button_solution.grid(row = 3, column = 0, pady = 2)

        # Top Right Button - Lic_in
        self.button_number_in=tkinter.Button(window, text='Lic in: ', width=50)
        self.button_number_in.grid(row = 2, column = 1, pady = 2)

        # Bot Right Button - Lic_out
        self.button_number_out=tkinter.Button(window, text='Lic out: ', width=50)
        self.button_number_out.grid(row = 3, column = 1, pady = 2)

        self.delay = 1
        self.update()

        self.window.mainloop()
    
    # update live1 and live2
    def update(self):
        ret_1, frame_1 = self.vid_1.get_frame()
        ret_2, frame_2 = self.vid_2.get_frame()
        if ret_1:
            self.image_1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_1))
            self.live1.create_image(0, 0, image = self.image_1, anchor = tkinter.NW)
        if ret_2:
            self.image_2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_2))
            self.live2.create_image(0, 0, image = self.image_2, anchor = tkinter.NW)
        self.readuid()
        self.window.after(self.delay, self.update)
    
    #take image and opendoor
    def takeImage(self):
        # get frame and detect
        ret_1, frame_1 = self.vid_1.get_frame()
        ret_2, frame_2 = self.vid_2.get_frame()
        
        id_str,bbox_image,crop_image=license_plate.license_detect(frame_1)
        self.lic_in = str(id_str[1][0] + '_' + id_str[0][0])
        
        car_bbox_image,car_crop_image=car.car_detect(frame_2)
        self.color_in = color.take_color(car_crop_image)

        # show taken image and lic_in
        self.image_show1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(bbox_image))
        self.image_show2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(car_bbox_image))
        self.image1.create_image(0, 0, image = self.image_show1, anchor = tkinter.NW)
        self.image2.create_image(0, 0, image = self.image_show2, anchor = tkinter.NW)
        self.button_number_in.config(text="Lic in: "+self.lic_in)
        self.button_number_out.config(text="Lic out: ")

        # save image
        self.image_in1 = PIL.Image.fromarray(frame_1)
        self.image_in2 = PIL.Image.fromarray(frame_2)
        self.car_crop_image_in = PIL.Image.fromarray(car_crop_image)
        
        #send massage to arduino
        self.solution = 'Open Door'
        self.button_solution.config(text=self.solution, background='green', activebackground='green')
        cmd = "On"
        cmd = cmd + '\r'
        arduinoData.write(cmd.encode())
    
    def openDoor_notMatch(self):
        if (self.solution == 'Not Match'):

            self.solution = 'Open Door'
            self.button_solution.config(text=self.solution, background='green', activebackground='green')

            data.del_id(self.uid)
            # send massage to arduino
            cmd = "On"
            cmd = cmd + '\r'
            arduinoData.write(cmd.encode())

    def showImage(self):
        ret_1, frame_1 = self.vid_1.get_frame()
        ret_2, frame_2 = self.vid_2.get_frame()
        
        id_str,bbox_image,crop_image=license_plate.license_detect(frame_1)
        self.lic_out = str(id_str[1][0] + '_' + id_str[0][0])
        
        car_bbox_image,car_crop_image=car.car_detect(frame_2)
        self.color_out = color.take_color(car_crop_image)
        
        self.image_show1 = PIL.ImageTk.PhotoImage(image = self.image_show1)
        self.image_show2 = PIL.ImageTk.PhotoImage(image = self.image_show2)

        self.image1.create_image(0, 0, image = self.image_show1, anchor = tkinter.NW)
        self.image2.create_image(0, 0, image = self.image_show2, anchor = tkinter.NW)
        self.button_number_in.config(text="Lic in: "+self.lic_in)
        self.button_number_out.config(text="Lic out: "+str(id_str[1][0] + '_' + id_str[0][0]))

        if (self.lic_out == self.lic_in):
            self.solution = 'Match'
            self.button_solution.config(text=self.solution, background='green', activebackground='green')

            data.del_id(self.uid)
            # send massage to arduino
            cmd = "On"
            cmd = cmd + '\r'
            arduinoData.write(cmd.encode())
        else:
            self.solution = 'Not Match'
            self.button_solution.config(text=self.solution, background='red', activebackground='red')


    #Read self.uid card, show on bar and take image
    def readuid(self):
        #show id card 
        if (arduinoData.inWaiting()!=0):
            dataPacket = arduinoData.readline()
            dataPacket = str(dataPacket,'utf-8')
            self.uid = dataPacket.strip('\r\n')
            # os.path.isfile("photo/"+self.uid+".png")

            # database in/out
            if (data.check_id(self.uid) == None):
                self.takeImage()
                data.add_id(self.uid,self.lic_in,self.color_in,self.image_in1,self.image_in2,self.car_crop_image_in)
            else:
                self.lic_in,self.color_in,self.image_show1,self.image_show2,self.car_crop_image_in = data.get_id(self.uid)
                self.showImage()
                
if platform.system() == "Linux":
    arduinoData = serial.Serial('/dev/ttyACM0',9600)
    time.delay = 1000
    license_plate=license_id()
    car=car_detector()
    color = color_detector()
    data=database()
    App(tkinter.Tk(), "get_video",'/dev/video0','/dev/video2',30)
else:
    arduinoData = serial.Serial('COM8',9600)
    time.delay = 1000
    license_plate=license_id()
    car=car_detector()
    color = color_detector()
    data=database()
    App(tkinter.Tk(), "get_video",0,1,30)
