import tkinter
import cv2
import time
import PIL.Image, PIL.ImageTk
import tkinter.messagebox
import serial
import os.path
from test_mongo import database
import platform
from DL_model import license_id

#read signal from port
arduinoData = serial.Serial('/dev/ttyACM0',9600)
time.delay = 1000
license_plate=license_id()

data=database()

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

        ret_1, frame_1 = self.vid_1.get_frame()
        ret_2, frame_2 = self.vid_2.get_frame()
        self.image_save = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_1))

        self.abc = 0

        self.live1 = tkinter.Canvas(window, width = self.vid_1.width, height = self.vid_1.height*0.8)
        self.live1.grid(row = 0, column = 0, pady = 2)

        self.image1 = tkinter.Canvas(window, width = self.vid_1.width, height = self.vid_1.height*0.8)
        self.image1.grid(row = 0, column = 1, pady = 2)

        self.live2 = tkinter.Canvas(window, width = self.vid_2.width, height = self.vid_2.height*0.8)
        self.live2.grid(row = 1, column = 0,pady = 2)

        self.image2 = tkinter.Canvas(window, width = self.vid_2.width, height = self.vid_2.height*0.8)
        self.image2.grid(row = 1, column = 1, pady = 2)

        self.btn_getvideo=tkinter.Button(window, text="takeImage", width=50, command=self.takeImageButton)
        self.btn_getvideo.grid(row = 2, column = 0, pady = 2)

        self.number_in=tkinter.Button(window, text='0', width=50)
        self.number_in.grid(row = 2, column = 1, pady = 2)

        self.number_out=tkinter.Button(window, text='0', width=50)
        self.number_out.grid(row = 3, column = 1, pady = 2)

        self.delay = 1
        self.update()

        self.window.mainloop()
    
    # update live frame_1
    def update(self):
        ret_1, frame_1 = self.vid_1.get_frame()
        ret_2, frame_2 = self.vid_2.get_frame()
        if ret_1:
            self.photo_1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_1))
            self.live1.create_image(0, 0, image = self.photo_1, anchor = tkinter.NW)
        if ret_2:
            self.photo_2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_2))
            self.live2.create_image(0, 0, image = self.photo_2, anchor = tkinter.NW)
        self.readUID()
        self.window.after(self.delay, self.update)
    
    #take image and opendoor
    def takeImage(self,uid):
        ret_1, frame_1 = self.vid_1.get_frame()
        ret_2, frame_2 = self.vid_2.get_frame()
        id_str,bbox_image,crop_image=license_plate.license_detect(frame_1)
        self.lic_in = str(id_str[1][0] + '_' + id_str[0][0])

        self.image_show1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(bbox_image))
        self.image_show2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_2))
        self.image1.create_image(0, 0, image = self.image_show1, anchor = tkinter.NW)
        self.image2.create_image(0, 0, image = self.image_show2, anchor = tkinter.NW)
        self.number_in.config(text=self.lic_in)
        self.number_out.config(text='0')

        self.image_save = PIL.Image.fromarray(frame_2)
        self.image_save.save("photo/"+uid+"_head.png")
        self.image_save = PIL.Image.fromarray(frame_1)
        self.image_save.save("photo/"+uid+"_tail.png")
        # file = open("lic/"+uid+".txt", 'w')
        # file.write(uid + '\n' + uid)
        # file.write(id_str[1][0] + '\n' + id_str[0][0])
        # file.close()
        
        #send massage to arduino
        cmd = "On"
        print('on')
        cmd = cmd + '\r'
        arduinoData.write(cmd.encode())

    def takeImageButton(self):
        ret_1, frame_1 = self.vid_1.get_frame()
        ret_2, frame_2 = self.vid_2.get_frame()
        uid = '0'

        id_str,bbox_image,crop_image=license_plate.license_detect(frame_1)
        self.lic_in = str(id_str[1][0] + '_' + id_str[0][0])

        self.image_show1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(bbox_image))
        self.image_show2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_2))
        self.image1.create_image(0, 0, image = self.image_show1, anchor = tkinter.NW)
        self.image2.create_image(0, 0, image = self.image_show2, anchor = tkinter.NW)
        self.number_in.config(text=str(id_str[1][0] + '_' + id_str[0][0]))
        self.number_out.config(text='0')
        

        self.image_save = PIL.Image.fromarray(frame_2)
        self.image_save.save("photo/"+uid+"_head.png")
        self.image_save = PIL.Image.fromarray(frame_1)
        self.image_save.save("photo/"+uid+"_tail.png")
        # file = open("lic/"+uid+".txt", 'w')
        # file.write(uid + '\n' + uid)
        # file.write(id_str[1][0] + '_' + id_str[0][0])
        # file.close()
        
        #send massage to arduino
        cmd = "On"
        print('on')
        cmd = cmd + '\r'
        arduinoData.write(cmd.encode())

    def showImage(self,uid,lic_in):
        ret_1, frame_1 = self.vid_1.get_frame()
        ret_2, frame_2 = self.vid_2.get_frame()
        id_str,bbox_image,crop_image=license_plate.license_detect(frame_1)
        self.lic_out = str(id_str[1][0] + '_' + id_str[0][0])

        img_show1 = PIL.Image.open("photo/"+uid+"_tail.png")
        self.image_show1 = PIL.ImageTk.PhotoImage(image = img_show1)
        img_show2 = PIL.Image.open("photo/"+uid+"_head.png")
        self.image_show2 = PIL.ImageTk.PhotoImage(image = img_show2)

        self.image1.create_image(0, 0, image = self.image_show1, anchor = tkinter.NW)
        self.image2.create_image(0, 0, image = self.image_show2, anchor = tkinter.NW)
        self.number_in.config(text=lic_in)
        self.number_out.config(text=str(id_str[1][0] + '_' + id_str[0][0]))

        # file = open("lic/"+uid+".txt", 'r')
        # lic = file.read()
        # lic_in = str(uid + '\n' + uid)
        self.lic_in = lic_in
        if (self.lic_out == self.lic_in):
            print("match")

            os.remove("photo/"+uid+"_head.png") 
            os.remove("photo/"+uid+"_tail.png") 
            data.del_id(uid)
            #send massage to arduino
            cmd = "On"
            print('on')
            cmd = cmd + '\r'
            arduinoData.write(cmd.encode())
        else:
            print("not match")


    #Read UID card, show on bar and take iamge
    def readUID(self):
        #show id card 
        if (arduinoData.inWaiting()!=0):
            dataPacket = arduinoData.readline()
            dataPacket = str(dataPacket,'utf-8')
            uid = dataPacket.strip('\r\n')
            os.path.isfile("photo/"+uid+".png")

            # database in/out
            if (data.check_id(uid) == None):
                self.takeImage(uid)
                data.add_id(uid,self.lic_in,"red")
            else:
                data_out = data.get_id(uid)
                self.showImage(uid,data_out["lic"])
                

            # if os.path.isfile("/home/red/cap/CapStone/photo/"+uid+".png"):
            #     self.showImage(uid)
            # else:
            #     self.takeImage(uid)
if platform.system() == "Linux":
    App(tkinter.Tk(), "get_video",'/dev/video0','/dev/video2',30)
else:
    App(tkinter.Tk(), "get_video",0,1,30)
