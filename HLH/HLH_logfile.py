import json
import os
import time
import logging
from Utils.config_util import load_config


class LogItem(object):
    def __init__(self, index, date, m_time, parameter):
        self.index = index
        self.date = date
        self.time = m_time
        self.parameter = parameter

    def to_dict(self) -> dict:
        return {
            'index': self.index,
            'date': self.date,
            'time': self.time,
            'parameter': self.parameter
        }


class Logfile(object):

    def __init__(self, path: str):
        self.log = []
        self.single_log = {'log_name': '',
                           'detail': []}
        self.config = load_config(path)
        self.fields = self.config['log']['fields']
        self.__fix = 2592000  # 1*30*24*60*60 one month
        self.valid_time = self.config['log']['valid_time'] * self.__fix

    def __add_log(self):
        """
        添加日志
        """
        self.log.append(self.single_log.copy())

    def __add_item(self, values):
        """
        添加条目
        :param values: 字段值
        :return: 无
        """
        log_item: LogItem = LogItem(int(values[0]),
                                    values[1],
                                    values[2],
                                    values[3])
        self.single_log['detail'].append(log_item.to_dict())

    def __filter_file(self, path) -> bool:
        """
        根据时间筛选日志
        :param path: 文件路径
        :return: 是否被筛选
        """
        stat = os.stat(path)
        t = time.time()
        return (int(t) - stat.st_mtime) > self.valid_time

    def read_log(self):
        """
        读取日志
        """
        base_path = self.config['base']
        log_path = os.path.join(base_path, self.config['log']['path'])
        # 用os.walk方法取得path路径下的文件夹路径，子文件夹名，所有文件名
        for _, _, filenames in os.walk(log_path):
            for f in filenames:
                log_file_path = os.path.join(log_path, f)
                try:
                    # 按条件筛选
                    if self.__filter_file(log_file_path):
                        continue

                    self.single_log['log_name'] = f
                    self.single_log['detail'] = []
                    # 打开文件并读取
                    with open(log_file_path, 'r', encoding='gbk') as log:
                        skip_line = 3  # 跳过前面两行
                        while skip_line:
                            skip_line -= 1
                            line = log.readline()

                        while line:
                            # 字段分别为： 索引 日期 时间 参数
                            values = line.strip().split('  ')
                            if not self.config['log']['filter']:
                                self.__add_item(values)
                            # 只添加在fields中的字段
                            elif values[3] in self.fields:
                                self.__add_item(values)
                            line = log.readline()

                    self.__add_log()
                except IOError:
                    logging.error("read log file error", exc_info=True)
                except Exception:
                    logging.exception("something is wrong when reading log files")

    def dump_json(self, indent=None) -> str:
        """
        将日志转为json格式, 按时间降序排序
        """
        self.log.sort(key=lambda x: x['log_name'], reverse=True)
        return json.dumps(self.log, ensure_ascii=False, indent=indent)

    def dump_dict(self):
        self.log.sort(key=lambda x: x['log_name'], reverse=True)
        return self.log
