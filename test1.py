import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
import numpy as np
from tensorflow import keras
import cv2

model = keras.models.load_model('vehicle_color_haze_free_model.h5')

d={'black':0,'blue':1,'cyan':2,'gray':3,'green':4,'red':5,'white':6,'yellow':7}
d_b={0: 'black',1:'blue',2:'cyan',3:'gray',4:'green',5:'red',6:'white',7:'yellow'}

def take_color(img):
    dim = (100,100)
    resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    df = resized.astype('float32')
    df=df/255
    activations = model.predict(df.reshape(1,100,100,3))
    return d_b[np.argmax(activations[len(activations)-1])]

class App:
    def __init__(self, window):
        self.window = window

        self.live1 = tkinter.Canvas(window, width = 600, height = 400)
        self.live1.grid(row = 0, column = 0, pady = 2)
        #self.live1.pack()

        self.image1 = tkinter.Canvas(window, width = 600, height = 400)
        self.image1.grid(row = 0, column = 1, pady = 2)
        #self.image1.pack()

        self.select_img=tkinter.Button(window, text="select_img", width=50, command=self.upload_file)
        self.select_img.grid(row = 1, column = 0,pady = 2)
        #self.live2.pack()

        self.img_path=tkinter.Button(window, text="img_path", width=50)
        self.img_path.grid(row = 1, column = 1, pady = 2)
        #self.image2.pack()

        self.btn_getvideo=tkinter.Button(window, text="Detect Image", width=50, command = self.det_img)
        self.btn_getvideo.grid(row = 2, column = 0, pady = 2)
        #self.btn_getvideo.pack(anchor=tkinter.CENTER, expand=True)

        self.number=tkinter.Button(window, text='0', width=50)
        self.number.grid(row = 2, column = 1, pady = 2)
        #self.number.pack(anchor=tkinter.CENTER, expand=True)
        self.window.mainloop()

    
    #take image and opendoor
    def det_img(self):
        self.color = take_color(self.cv_img)
        self.number.config(text= self.color)

    #Read UID card, show on bar and take iamge
    def upload_file(self):
        f_types = [('Jpg Files', '*.jpg')]
        filename = filedialog.askopenfilename(filetypes=f_types)
        self.image=Image.open(filename)
        self.image=self.image.resize((600, 400))
        self.cv_img = cv2.imread(filename)
        self.img = ImageTk.PhotoImage(self.image)
        self.live1.create_image(0, 0, image = self.img, anchor = tkinter.NW)
        self.img_path.config(text=filename)
        
App(tkinter.Tk())

