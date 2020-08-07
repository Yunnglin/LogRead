from HLH.HLH_logfile import Logfile

if __name__ == '__main__':
    file = Logfile("HLH/HLH_config.yaml")
    file.read_log()
    print(file.dump_json())
