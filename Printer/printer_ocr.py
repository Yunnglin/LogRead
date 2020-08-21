import json

from Utils.config_util import load_config
from PIL import ImageGrab
from pytesseract import image_to_string
import cv2 as cv
import numpy as np
import logging


class Box:
    def __init__(self, origin_x, origin_y, size_w, size_h, is_num=True):
        """
        屏幕截图图像
        :param origin_x: 起始x坐标
        :param origin_y: 起始y坐标
        :param size_w: 图像宽度
        :param size_h: 图像高度
        :param is_num: 标识该字段是否是数字，否则是中文
        """
        self.origin = [origin_x, origin_y]
        self.size = [size_w, size_h]
        self.is_num = is_num
        self.border = (self.origin[0],
                       self.origin[1],
                       self.origin[0] + self.size[0],
                       self.origin[1] + self.size[1])


class ParameterOCR:
    def __init__(self, path: str):
        self.config = load_config(path)['ocr_config']
        self.num_config = self.config['num_config']
        self.chi_sim_config = self.config['chi_sim_config']
        self.boxes = []
        self.__get_boxes()
        self.image = None
        self.parameters = []
        self.parameters_dict = {
            '生产模式': '',
            'PCB长度': '',
            'PCB宽度': '',
            'PCB厚度': '',
            '运输速度': '',
            '印刷速度': '',
            '运动状态': '',
            '印刷长度': '',
            '印刷起点': '',
            '脱模长度': '',
            '后刮刀压力': '',
            '前刮刀压力': '',
            '脱模方式': '',
            '印刷方式': '',
            '平台X轴': '',
            '平台Y1轴': '',
            '平台Y2轴': '',
            '平台Z轴': '',
            'CCD X轴': '',
            'CCD Y轴': '',
            '清洗': '',
            '刮刀': '',
            '取像方式': '',
            '清洗次数': '',
            '清洗纸': '',
            '脱模速度': '',
            '清洗速度': '',
            '清洗间隔': '',
            '清洗液': '',
            '空气压力': '',
            '下轮清洗': '',
            '生产周期': '',
            '产量': '',
            '刮刀片使用次数1': '',
            '刮刀片使用次数2': ''
        }

    def __get_boxes(self):
        # 第一列
        boxes1 = [
            Box(125, 370, 50, 25, False),
            Box(125, 395, 50, 25),
            Box(125, 395 + 25, 50, 25),
            Box(125, 395 + 50, 50, 25),
            Box(125, 395 + 75, 50, 25),
            Box(125, 395 + 100, 50, 25),
            Box(25, 565, 300, 50, False)
        ]
        # 第二列
        boxes2 = [
            Box(455, 320, 50, 25),
            Box(455, 320 + 25, 50, 25),
            Box(455, 320 + 50, 50, 25),
            Box(455, 320 + 75, 50, 25),
            Box(455, 320 + 100, 50, 25),
            Box(455, 320 + 125, 130, 25, False),
            Box(455, 320 + 150, 60, 25, False),
        ]
        # 第三列
        boxes3 = []
        origin = (760, 18)
        chi_index = [8, 10, 14, 15, 16]
        for i in range(19):
            if i in chi_index:
                boxes3.append(Box(origin[0], origin[1] + i * 25, 100, 25, False))
                continue
            boxes3.append(Box(origin[0], origin[1] + i * 25, 50, 25))

        # 刮刀片
        boxes4 = [
            Box(480, 515, 58, 16),
            Box(561, 515, 58, 16)

        ]
        self.boxes.extend(boxes1)
        self.boxes.extend(boxes2)
        self.boxes.extend(boxes3)
        self.boxes.extend(boxes4)

    def get_parameters(self, boxes: [Box]):
        full_screen = (0, 0, 1366, 768)
        # screen = ImageGrab.grab(full_screen)
        screen = self.image
        index = 1
        for box in boxes:
            # 截取图像
            part_img = screen.crop(box.border)
            # 读取为灰度图
            img = cv.cvtColor(np.array(part_img), cv.COLOR_RGB2GRAY)
            # 长宽各放大3倍
            img = cv.resize(img, None, fx=3, fy=3, interpolation=cv.INTER_CUBIC)
            # 二值化
            ret, threshold = cv.threshold(img, 90, 255, cv.THRESH_BINARY_INV)
            # 进行腐蚀操作
            kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 3))
            threshold = cv.erode(threshold, kernel)
            if box.is_num:
                yield image_to_string(threshold, lang='eng', config=self.num_config)
            else:
                yield image_to_string(threshold, lang='chi_sim', config=self.chi_sim_config).replace(' ', '')
            # part_img.save(os.path.join('./pics', str(index) + '-part.png'), 'png')
            # index += 1

    def identify(self):
        self.parameters = []
        param = self.get_parameters(self.boxes)
        try:
            while True:
                new_para = param.__next__().strip()
                self.parameters.append(new_para)
        except StopIteration:
            pass
        except Exception:
            logging.exception('Unexpected exception!!!')

    def dump_dict(self):
        index = 0
        for key in self.parameters_dict.keys():
            self.parameters_dict[key] = self.parameters[index]
            index += 1
        return self.parameters_dict

    def dump_json(self):
        self.dump_dict()
        return json.dumps(self.parameters_dict, ensure_ascii=False, indent=2)
