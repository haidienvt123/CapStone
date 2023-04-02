import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
from DL_model import license_id
import numpy as np

license_plate=license_id()

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
        id_str,bbox_image,crop_image=license_plate.license_detect(self.cv_img)

        self.image_show1 = ImageTk.PhotoImage(image = Image.fromarray(bbox_image))
        self.image1.create_image(0, 0, image = self.image_show1, anchor = tkinter.NW)
        self.number.config(text=str(id_str[0][0]))

    #Read UID card, show on bar and take iamge
    def upload_file(self):
        f_types = [('Jpg Files', '*.jpg')]
        filename = filedialog.askopenfilename(filetypes=f_types)
        self.image=Image.open(filename)
        self.image=self.image.resize((600, 400))
        self.cv_img = np.array(self.image) 
        self.img = ImageTk.PhotoImage(self.image)
        self.live1.create_image(0, 0, image = self.img, anchor = tkinter.NW)
        self.img_path.config(text=filename)
        
App(tkinter.Tk())

