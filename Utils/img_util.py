import re

from PIL import Image
import base64
from io import BytesIO

'''
opencv中图片格式为BGR
pil中为RGB,需要转换一下
'''


#
#
# def numpy_to_cv():
#     image = np.zeros((300, 300, 1), dtype=np.uint8)
#     cv2.rectangle(image, (10, 10), (100, 100), (255, 255, 255), 10)
#     cv2.imshow('mask', image)
#     cv2.waitKey(0)
#
#
# def numpy_to_PIL():
#     image = np.zeros((300, 300, 3), dtype=np.uint8)
#     image = Image.fromarray(image)
#     image.show()
#
#
# def cv2_show():
#     '''opencv显示图片'''
#     image = cv2.imread('lena.png')
#     cv2.imshow('lena', image)
#     cv2.waitKey()
#
#
# def PIL_show():
#     '''PIL显示图片'''
#     image = Image.open('lena.png')
#     image.show()
#
#
# # cv2_show()
# # PIL_show()
# def cv2_to_PIL():
#     image = cv2.imread('lena.png')
#     image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     image.show()
#
#
# def PIL_to_cv2():
#     image = Image.open('lena.png')
#     image = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
#     cv2.imshow('lena', image)
#     cv2.waitKey()
#
#
# # cv2_to_PIL()
# # PIL_to_cv2()

def get_image_from_path(path: str):
    return Image.open(path)


def image_to_base64(image: Image):
    buffered = BytesIO()
    image.save(buffered, format="png")
    img_str = base64.b64encode(buffered.getvalue())
    return str(img_str, encoding='utf-8')


def base64_to_image(base64_str):
    base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)
    return img
