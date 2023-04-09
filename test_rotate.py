from PIL import Image
filename = "lic.jpg"

with Image.open(filename) as img:
    img.load()

img_gray = img.convert("L")
threshold = 150
img_threshold = img_gray.point(
    lambda x: 255 if x > threshold else 0
)
img_threshold.show()
# threshold = 57
# img_threshold = blue.point(lambda x: 255 if x > threshold else 0)
# img_threshold = img_threshold.convert("1")
# img_threshold.show()