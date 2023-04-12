import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
import numpy as np
import cv2
from DL_model import license_id,color_detector,car_detector
from test_rotate import crop_num

license_plate=license_id()
color = color_detector()
car = car_detector()

class App:
    def __init__(self, window):
        self.window = window

        self.live1 = tkinter.Canvas(window, width = 800, height = 600)
        self.live1.grid(row = 0, column = 0, pady = 2)
        #self.live1.pack()

        self.image1 = tkinter.Canvas(window, width = 800, height = 600)
        self.image1.grid(row = 0, column = 1, pady = 2)
        #self.image1.pack()

        self.btn_select_img=tkinter.Button(window, text="select_img", width=50, command=self.upload_file)
        self.btn_select_img.grid(row = 1, column = 0,pady = 2)
        #self.live2.pack()

        self.img_path=tkinter.Button(window, text="img_path", width=50)
        self.img_path.grid(row = 1, column = 1, pady = 2)
        #self.image2.pack()

        self.btn_color=tkinter.Button(window, text="Detect Color", width=50, command = self.det_col)
        self.btn_color.grid(row = 2, column = 0, pady = 2)
        #self.btn_getvideo.pack(anchor=tkinter.CENTER, expand=True)

        self.show_color=tkinter.Button(window, text='0', width=50)
        self.show_color.grid(row = 2, column = 1, pady = 2)
        #self.number.pack(anchor=tkinter.CENTER, expand=True)

        self.btn_lic=tkinter.Button(window, text="Detect Image", width=50, command = self.det_img)
        self.btn_lic.grid(row = 3, column = 0, pady = 2)
        #self.btn_getvideo.pack(anchor=tkinter.CENTER, expand=True)

        self.number=tkinter.Button(window, text='0', width=50)
        self.number.grid(row = 3, column = 1, pady = 2)
        #self.number.pack(anchor=tkinter.CENTER, expand=True)
        
        self.btn_car=tkinter.Button(window, text="Detect Car", width=50, command = self.det_car)
        self.btn_car.grid(row = 4, column = 0, pady = 2)
        #self.btn_getvideo.pack(anchor=tkinter.CENTER, expand=True)

        self.window.mainloop()

    def det_car(self):
        car_bbox_image,car_crop_image=car.car_detect(self.cv_img)
        bbox_image_show = cv2.cvtColor(car_bbox_image,cv2.COLOR_BGR2RGB)
        image = Image.fromarray(bbox_image_show)
        image=image.resize((600, 400))
        self.image_show1 = ImageTk.PhotoImage(image)
        self.image1.create_image(0, 0, image = self.image_show1, anchor = tkinter.NW)
    
    #take image and opendoor
    def det_col(self):
        car_bbox_image,car_crop_image=car.car_detect(self.cv_img)
        img = cv2.cvtColor(car_crop_image,cv2.COLOR_BGR2RGB)
        self.color = color.take_color(img)
        self.show_color.config(text= self.color)

    def det_img(self):
        id_str,bbox_image,crop_image=license_plate.license_detect(self.cv_img)
        cv2.imwrite('lic.jpg', crop_image)
        crop_number = crop_num(crop_image)
        bbox_image_show = cv2.cvtColor(bbox_image,cv2.COLOR_BGR2RGB)
        image = Image.fromarray(crop_number)
        image=image.resize((400, 80))
        self.image_show1 = ImageTk.PhotoImage(image)
        self.image1.create_image(0, 0, image = self.image_show1, anchor = tkinter.NW)
        self.number.config(text=str(id_str[1][0]+'_'+id_str[0][0]))

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

