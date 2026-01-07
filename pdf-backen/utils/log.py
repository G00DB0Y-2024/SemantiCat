import logging
import csv
import os

from datetime import datetime

PURPLE = "\033[35m"  # 紫色
RESET = "\033[0m"    # 重置颜色
# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format=PURPLE+ '%(levelname)s'+ RESET +':     [%(asctime)s] - %(message)s',
    datefmt='%Y/%m/%d %H:%M'  # 设置时间格式
)
logger = logging.getLogger('')

def debug(text):
    logger.info(text)
    

def log(admin, target, oldcontent, newcontent):
    now = datetime.now()
    if not os.path.exists("./logs/"):
        os.mkdir("./logs/")
    # 打开 CSV 文件并写入数据
    with open(f'./logs/log-{now.strftime("%Y%m%d")}.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # 如果需要在文件中写入标题行（可选）
        if file.tell() == 0:  # 检查文件是否为空
            writer.writerow(["Time", "AdminId","Target","History", "Update"])  # 写入标题行
        
        # 写入数据行
        writer.writerow([now.strftime("%H:%M:%S"), admin, target, oldcontent, newcontent])
