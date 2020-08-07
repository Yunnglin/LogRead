import json
import collections

import pytesseract
from PIL import Image, ImageGrab
import threading

from Utils.config_util import load_config

tree = lambda : collections.defaultdict(tree)

class ParameterOCR:

    def __init__(self, path: str):
        self.config = load_config(path)['parameter']
        self._bg_color = tuple(self.config['bg_color'])
        self._border_color = tuple(self.config['border_color'])
        self._ocr_config = self.config['ocr_config']
        # 4行8列的参数数组
        self._row = 4
        self._col = 8
        self.parameter = [[0 for i in range(self._col)] for j in range(self._row)]
        self.parameter_dict = tree()
        self.cool = [0, 0]
        self.cool_dict = {}
        self.pcb_statistic = [0, 0, 0]
        self.pcb_dict = {}
        self.trans_speed = [0.0, 0.0]
        self.trans_speed_dict = {}
        self.frequency = 0
        self.frequency_dict = {}

    def __process_img(self, pixels, image):
        """
        处理图像，将图像转为黑白
        :param pixels: 图像的像素
        :param image: 图像
        """
        for i in range(image.size[0]):
            for j in range(image.size[1]):
                if pixels[i, j] == (255, 0, 0):
                    pixels[i, j] = (0, 0, 0)
                    # pass
                elif pixels[i, j] == self._bg_color or pixels[i, j] == self._border_color:
                    pixels[i, j] = (255, 255, 255)

    def identify_image(self, image, show_image=False, config='') -> str:
        """
        调用pytesseract来识别参数
        :param image: 输入图像
        :param show_image: bool 是否显示图像
        :param config: pytesseract的参数
        :return: 识别出的参数
        """
        pixels = image.load()
        self.__process_img(pixels, image)
        if show_image:
            image.show()
        return pytesseract.image_to_string(image, lang='eng', config=config)

    def get_parameters(self, start_pos, box_size, count=1):
        """
        从ocr获取参数
        :param start_pos: 开始位置的坐标
        :param box_size:  每块的大小
        :param count: 循环次数
        :return: 返回相应的迭代器
        """
        offset_x = self.config['offset_x']
        full_screen = tuple(self.config['full_screen'])
        screen = ImageGrab.grab(full_screen)
        for pos in start_pos:
            for i in range(count):
                new_start = (pos[0] + i * offset_x, pos[1])
                box = (new_start[0],
                       new_start[1],
                       new_start[0] + box_size[0],
                       new_start[1] + box_size[1])
                part_img = screen.crop(box)
                yield (self.identify_image(image=part_img,
                                           show_image=self._ocr_config['show_img'],
                                           config=self._ocr_config['para']))

    def __rough_identify(self):
        """
        不精确识别，进行16次识别
        """
        up_start_pos1 = tuple(self.config['up_start_pos1'])
        down_start_pos1 = tuple(self.config['down_start_pos1'])

        box_size = tuple(self.config['v_box_size'])
        start_pos = [up_start_pos1, down_start_pos1]

        para = self.get_parameters(start_pos, box_size, 8)
        # 将字符串转为数字
        self.parameter = [[0 for i in range(self._col)] for j in range(self._row)]
        try:
            count = 0
            while True:
                # 返回16次
                # 前8次为上层参数
                # 后8次为下层参数
                para_str = para.__next__()
                para_str = para_str.strip().split('\n')

                col = count % self._col
                row = 2 * (count // self._col)
                try:
                    if len(para_str) == 2:
                        self.parameter[row][col] = int(para_str[0])
                        self.parameter[row + 1][col] = int(para_str[1])
                    elif len(para_str) == 1:
                        self.parameter[row][col] = int(para_str[0])
                    else:
                        pass
                except ValueError as e:  # str转int出错
                    pass
                count += 1
        except StopIteration as e:  # 迭代终止
            pass

    def __precise_identify(self):
        """
        精确识别，进行32次识别
        """
        up_start_pos1 = tuple(self.config['up_start_pos1'])
        up_start_pos2 = tuple(self.config['up_start_pos2'])
        down_start_pos1 = tuple(self.config['down_start_pos1'])
        down_start_pos2 = tuple(self.config['down_start_pos2'])

        box_size = tuple(self.config['box_size'])
        start_pos = [up_start_pos1, up_start_pos2, down_start_pos1, down_start_pos2]

        para = self.get_parameters(start_pos, box_size, 8)
        # 将字符串转为数字
        self.parameter = [[0 for i in range(self._col)] for j in range(self._row)]

        try:
            count = 0
            while True:
                # 返回32次
                para_str = para.__next__()
                para_str = para_str.strip().split('\n')

                col = count % self._col
                row = count // self._col
                try:
                    if len(para_str) == 1:
                        self.parameter[row][col] = int(para_str[0])
                    else:
                        pass
                except ValueError as e:  # str转int出错
                    pass
                count += 1
        except StopIteration as e:  # 迭代终止
            pass

    def __identify_cool(self):
        start_pos = [(439, 266)]
        box_size = tuple(self.config['v_box_size'])
        para = self.get_parameters(start_pos, box_size)
        try:
            self.cool = para.__next__().strip().split('\n')
            if len(self.cool) != 2:
                self.cool = [0, 0]
        except StopIteration as e:  # 迭代终止
            pass

    def __vertical_identify(self, start_pos, box_size, count):
        res = []
        offset_y = self.config['offset_y']
        for i in range(count):
            new_start_pos = [(start_pos[0], start_pos[1] + i * offset_y)]
            para = self.get_parameters(new_start_pos, box_size)
            try:
                para_str = para.__next__()
                res.append(para_str.strip().split('\n')[0])
            except StopIteration as e:  # 迭代终止
                pass
        return res

    def __identify_pcb(self):
        # start_pos = (530, 520)
        # box_size = (38, 16)
        # self.pcb_statistic = self.__vertical_identify(start_pos, box_size, 3)
        start_pos = [(530, 520)]
        box_size = (38, 58)
        para = self.get_parameters(start_pos, box_size)
        try:
            para_str = para.__next__()
            self.pcb_statistic = para_str.strip().split('\n')
            if len(self.pcb_statistic) != 3:
                self.pcb_statistic = [0, 0, 0]
        except StopIteration as e:  # 迭代终止
            pass

    def __identify_trans_speed(self):
        start_pos = [(778, 520)]
        box_size = (50, 40)
        para = self.get_parameters(start_pos, box_size)
        try:
            para_str = para.__next__()
            self.trans_speed = para_str.strip().split('\n')
            if len(self.trans_speed) != 2:
                self.trans_speed = [0, 0]
        except StopIteration as e:  # 迭代终止
            pass

    def __identify_frequency(self):
        start_pos = [(1025, 520)]
        box_size = (38, 16)
        para = self.get_parameters(start_pos, box_size)
        try:
            para_str = para.__next__()
            self.frequency = para_str.strip().split('\n')
            if len(self.frequency) != 1:
                self.frequency = 0
            else:
                self.frequency = self.frequency[0]
        except StopIteration as e:  # 迭代终止
            pass

    def identify(self, precise: bool = False):
        """
        进行ocr识别
        :param precise: 是否精确
        """
        if precise:
            self.__precise_identify()
        else:
            self.__rough_identify()

        for i in range(self._row):
            for j in range(self._col):
                if i == 0:
                    self.parameter_dict[str(self._col - j) + 'T']['PV'] = self.parameter[i][j]
                elif i == 1:
                    self.parameter_dict[str(self._col - j) + 'T']['SV'] = self.parameter[i][j]
                elif i == 2:
                    self.parameter_dict[str(self._col - j) + 'B']['PV'] = self.parameter[i][j]
                elif i == 3:
                    self.parameter_dict[str(self._col - j) + 'B']['SV'] = self.parameter[i][j]

        self.__identify_cool()
        self.cool_dict = {
            'PV': self.cool[0],
            'SV': self.cool[1]
        }
        self.__identify_pcb()
        self.pcb_dict = {
            '入板': self.pcb_statistic[0],
            '出板': self.pcb_statistic[1],
            '炉内PCB': self.pcb_statistic[2]
        }
        self.__identify_trans_speed()
        self.trans_speed_dict = {
            'PV': self.trans_speed[0],
            'SV': self.trans_speed[1]
        }
        self.__identify_frequency()
        self.frequency_dict = {
            '通道1': self.frequency
        }

    def dump_json(self) -> str:
        """
        将获取到的参数转为json
        :return: json字符串
        """
        param = {
            'cool': self.cool_dict,
            'parameter': self.parameter_dict,
            'pcb_statistic': self.pcb_dict,
            'trans_speed': self.trans_speed_dict,
            'frequency': self.frequency_dict
        }
        return json.dumps(param, ensure_ascii=False, indent=2)
