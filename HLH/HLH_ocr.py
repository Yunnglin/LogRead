import pytesseract
from PIL import Image, ImageGrab
import threading

from Utils.config_util import load_config


class ParameterOCR:

    def __init__(self, path:str):
        self.config = load_config(path)
        self.bg_color = (2, 117, 124)
        self.border_color = (100, 100, 100)

    def process_img(self, pixels, image):
        for i in range(image.size[0]):
            for j in range(image.size[1]):
                if pixels[i, j] == (255, 0, 0):
                    pixels[i, j] = (0, 0, 0)
                    # pass
                elif pixels[i, j] == self.bg_color or pixels[i, j] == self.border_color:
                    pixels[i, j] = (255, 255, 255)

    def identify_image(self, bbox, show_image=False, config='') -> str:
        image = ImageGrab.grab(bbox)
        pixels = image.load()
        self.process_img(pixels, image)
        if show_image:
            image.show()
        return pytesseract.image_to_string(image, lang='eng', config=config)

    def get_parameters(self, start_pos, box_size):
        box_size = (38, 15)
        v_box_size = (38, 36)
        offset_x = 60
        up_start_pos1 = (499, 266)
        up_start_pos2 = (499, 287)

        down_start_pos1 = (499, 401)
        down_start_pos2 = (499, 422)
        count: int = 8
        for pos in start_pos:
            for i in range(count):
                new_start = (pos[0] + i * offset_x, pos[1])
                boxx = (new_start[0], new_start[1], new_start[0] + box_size[0], new_start[1] + box_size[1])
                (self.identify_image(boxx))