from HLH.HLH_logfile import Logfile
from HLH.HLH_ocr import ParameterOCR

if __name__ == '__main__':
    path = "HLH/HLH_config.yaml"
    # file = Logfile(path)
    # file.read_log()
    # print(file.dump_json())

    param = ParameterOCR(path)
    # param.rough_identify()
    param.identify()
    # print(param.cool)
    # print(param.pcb_statistic)
    # print(param.trans_speed)
    # print(param.frequency)
    # print(param.parameter)
    print(param.dump_json())