from Utils.config_util import load_config
import json
import os
import time
import logging


class PrinterLog:
    def __init__(self, path: str):
        self.logs = []
        self.single_log = {
            'date': '',
            'detail': []
        }
        self.detail = {
            'time': '',
            'parameter': ''
        }
        self.config = load_config(path)['log']
        self.fields = self.config['fields']
        self.__fix = 2592000  # 1*30*24*60*60 one month
        self.valid_time = self.config['valid_time'] * self.__fix

    def __clear_single_log(self):
        self.single_log = {
            'date': '',
            'detail': []
        }

    def __clear_detail(self):
        self.detail = {
            'time': '',
            'parameter': ''
        }

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
        log_path = self.config['path']
        self.logs = []
        for _, _, file_names in os.walk(log_path):
            for name in file_names:
                log_file_path = os.path.join(log_path, name)
                try:
                    # 按条件筛选
                    if self.__filter_file(log_file_path):
                        continue

                    with open(log_file_path, 'r', encoding=self.config['encode']) as cur_log:
                        line = cur_log.readline()
                        pre_date = ''
                        while line:
                            # e.g： [2020.08.03-08_54_21]  | Login level 3 permissions.
                            values = line.split('|')
                            times = values[0].strip()[1:-1].split('-')
                            cur_date = times[0]
                            cur_time = times[1].replace('_', ':')
                            parameter = values[1].strip()

                            if parameter in self.fields:
                                if pre_date != cur_date:
                                    # 新一天的log
                                    if pre_date != '':
                                        self.logs.append(self.single_log.copy())
                                    pre_date = cur_date
                                    self.__clear_single_log()
                                    self.single_log['date'] = cur_date

                                # 添加字段
                                self.detail['time'] = cur_time
                                self.detail['parameter'] = parameter
                                self.single_log['detail'].append(self.detail.copy())

                            line = cur_log.readline()

                        # 添加剩余的最后一个文件
                        self.logs.append(self.single_log.copy())

                except IOError:
                    logging.error("read log file error", exc_info=True)
                except Exception:
                    logging.exception("something is wrong when reading log files")

    def dump_json(self) -> str:
        """
        将日志转为json格式, 按时间降序排序
        """
        self.logs.sort(key=lambda x: x['date'], reverse=True)
        return json.dumps(self.logs, ensure_ascii=False, indent=2)

    def dump_dict(self):
        self.logs.sort(key=lambda x: x['date'], reverse=True)
        return self.logs

