import tkinter
import cv2
import time
import PIL.Image, PIL.ImageTk
import tkinter.messagebox
import serial
# from DL_model import license_id

#read signal from port
arduinoData = serial.Serial('/dev/ttyACM0',9600)
time.delay = 1000
license_plate=license_id()

# video capture
class MyVideoCapture:
    def __init__(self, video_source):
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
    def __init__(self, window, window_title,video_source, fpsLimit = 30):

        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.fpsLimit = fpsLimit
        self.vid = MyVideoCapture(video_source)    

        ret, frame = self.vid.get_frame()
        self.image_save = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))

        self.abc = 0

        self.live1 = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height*0.8)
        self.live1.grid(row = 0, column = 0, pady = 2)

        self.image1 = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height*0.8)
        self.image1.grid(row = 0, column = 1, pady = 2)

        self.live2 = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height*0.8)
        self.live2.grid(row = 1, column = 0,pady = 2)

        self.image2 = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height*0.8)
        self.image2.grid(row = 1, column = 1, pady = 2)


        

        self.btn_getvideo=tkinter.Button(window, text="takeImage", width=50, command=self.takeImage('0'))
        self.btn_getvideo.grid(row = 2, column = 0, pady = 2)

        self.number=tkinter.Button(window, text='0', width=50)
        self.number.grid(row = 2, column = 1, pady = 2)

        self.delay = 1
        self.update()

        self.window.mainloop()
    
    # update live frame
    def update(self):
        ret, frame = self.vid.get_frame()
        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.live1.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
            self.live2.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
        self.readUID()
        self.window.after(self.delay, self.update)
    
    #take image and opendoor
    def takeImage(self,uid):
        ret, frame = self.vid.get_frame()

        id_str,bbox_image,crop_image=license_plate.license_detect(frame)

        self.image_show1 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(bbox_image))
        self.image_show2 = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        self.image1.create_image(0, 0, image = self.image_show1, anchor = tkinter.NW)
        self.image2.create_image(0, 0, image = self.image_show2, anchor = tkinter.NW)
        self.number.config(text=str(id_str[1][0] + '_' + id_str[0][0]))

        self.image_save = PIL.Image.fromarray(frame)
        self.image_save.save("photo/"+uid+'_'+id_str[1][0] + '_' + id_str[0][0]+".png")''
        
        # #send massage to arduino
        # cmd = "On"
        # cmd = cmd + '\r'
        # arduinoData.write(cmd.encode())

        print("success")

    #Read UID card, show on bar and take iamge
    def readUID(self):
        #show id card 
        if (arduinoData.inWaiting()!=0):
            dataPacket = arduinoData.readline()
            dataPacket = str(dataPacket,'utf-8')
            uid = dataPacket.strip('\r\n')
            # self.number.config(text=str(dataPacket))
            # print(dataPacket)
            self.takeImage(uid)
        
App(tkinter.Tk(), "get_video",'/dev/video0',30)

