## SCREEN DETECTION

- Download and put your Screen detection model in to `model/screen_detection/` folder via this [link](https://box.tma.com.vn/index.php/s/iVcZhtaJ64EJPyJ).
- Change model path in file: src/yolov7/screen_detector.py
```sh
weights='./model/screen_detection/screen_detection.pt'
```


## TEXT DETECTION

- Download and put your Text detection models in to `model/text_detection/` via this [link](https://box.tma.com.vn/index.php/s/RjNSKuemVoGeJ1k).
- Change model path in file: src/yolov7/text_detector.py:
```sh
weights='./model/text_detection/text_detect_3_11.pt'
```