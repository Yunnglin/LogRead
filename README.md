# LogRead
> 使用OCR识别屏幕参数并读取日志数据

该程序为32bit, 分为两部分, 一是读取日志和获取屏幕截图的边缘机器程序; 
另一个是接收请求, 识别截图参数, 并将参数发送到MQTT平台的中心机器程序, 
两程序通过Flask进行Http请求相互通信.

## 配置环境
推荐使用Anaconda进行环境管理
```shell script
# 添加镜像
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/ 
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/ 
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/ 
conda config --set show_channel_urls yes

# 开启32位环境
set CONDA_FORCE_32BIT=1

# 查看环境信息
conda info

# 创建新环境
conda create -n new_env python=3.7
conda activate new_env
```

## 安装依赖
参考使用 [requirements](requirments.txt) 文件或者手动安装如下依赖
```shell script
conda install pillow pyyaml pyinstaller opencv flask

conda install -c conda-forge pytesseract

pip install paho-mqtt
```
**注意:**

在使用`pytesseract`之前需要安装 [tesseract](https://github.com/tesseract-ocr/tesseract) 软件, 并配置环境变量. 同时下载中文包, 放在安装目录下的data中, 
config文件中的参数设置参考 [tesseract文档](https://github.com/tesseract-ocr/tesseract/blob/master/doc/tesseract.1.asc)

## 配置文件
- [日志](config/log_config.yaml)

常规的日志配置

- [Mqtt配置](config/mqtt_config.yaml)

主要配置mqtt平台的ip等相关信息, 指示当前运行程序任务配置

- [回流焊配置](config/HLH_config.yaml)

配置日志文件目录, 筛选字段, OCR使用参数等

- [印刷机配置](config/printer_config.yaml)

配置大致同上

## 使用

按如下方式build或者直接下载 [release](https://github.com/Yunnglin/LogRead/releases/tag/v1.0)

**注意:** 打包环境需要是32位才能在32位机器上运行

```shell script
# 使用pyinstaller打包中心机器运行程序, 之后运行run.exe即可
> build.bat 

# 使用pyinstaller打包边缘机器运行程序, 之后运行run_single.exe即可
> build_single.bat 
```