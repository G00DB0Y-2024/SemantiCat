import uvicorn
import base64
import os, json, sys

import xml.etree.ElementTree as ET

from utils.log import debug

from datetime import datetime
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, Request
from fastapi import APIRouter,File, UploadFile, Form, Header
from typing import List, Dict, Any

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager


'''
******************************************
'''
GREEN = "\033[32m"
PURPLE = "\033[35m"  # 紫色
RED = "\033[31m"   # 红色
YELLOW = "\x1b[33m" 
RESET = "\033[0m"

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan=lifespan)

'''
******************************************
'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  # 允许的源，可以是单个或多个
    allow_credentials=False,
    allow_methods=["*"],  # 允许的方法，例如 GET, POST 等
    allow_headers=["*"],  # 允许的请求头
)

if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS  # PyInstaller临时目录
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

static_file_abspath = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_file_abspath, exist_ok=True)  # 如果目录不存在则创建
app.mount("/static", StaticFiles(directory=static_file_abspath), name="static")

class AiLoadReq(BaseModel):
    fp:str

class AiSaveReq(BaseModel):
    fp:str
    mode:str
    index:int
    cont:Any

class OpacityArray(BaseModel):
    ops: List[float]  # 接收一个浮点数数组
    fp:str

class ImageReq(BaseModel):
    imgname:str
    base64:str
    mode:str

class HlInfo(BaseModel):
    fp:str
    key:str
    hl:Any

@app.put("/reqHighlightSet")
async def req_highlight_save(req_info: HlInfo):
    # 确保save目录存在
    save_dir = os.path.join(base_dir, 'save')
    os.makedirs(save_dir, exist_ok=True)  # 如果目录不存在则创建
    file_path = os.path.join(save_dir, f'{req_info.fp}_hls.json')

    if not os.path.exists(file_path):
        res = {}
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            res = json.load(f)  # 读取JSON文件内容并赋值给load
    if req_info.key in res:
        del res[req_info.key]
    else:
        res[req_info.key] = req_info.hl

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(res, f)

@app.post("/reqHighlightGet")
async def req_highlight_load(req_info: HlInfo):
    # 确保save目录存在
    save_dir = os.path.join(base_dir, 'save')
    os.makedirs(save_dir, exist_ok=True)  # 如果目录不存在则创建
    file_path = os.path.join(save_dir, f'{req_info.fp}_hls.json')

    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r', encoding='utf-8') as f:
        res = json.load(f)  # 读取JSON文件内容并赋值给load
        return res

@app.post("/reqLoadAIPre")
async def func(req_info:AiLoadReq):   
    file_path = os.path.join(base_dir, 'save', f'{req_info.fp}.json')
    if os.path.exists(file_path):
        return True

    return False  

@app.post("/reqLoadAI")
async def func(req_info:AiLoadReq):   
    file_path = os.path.join(base_dir, 'save', f'{req_info.fp}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            res = json.load(f)  # 读取JSON文件内容并赋值给load
            debug(f'PDF[{req_info.fp}] has loaded {len(res)} logs!')
            return res
    return []  # 返回完整的响应

@app.put("/reqSaveAI")
async def func(req_info:AiSaveReq):   
    # 确保save目录存在
    save_dir = os.path.join(base_dir, 'save')
    os.makedirs(save_dir, exist_ok=True)  # 如果目录不存在则创建
    
    file_path = os.path.join(save_dir, f'{req_info.fp}.json')
    
    try:
        # 如果文件不存在，创建一个空列表
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            data:list = json.load(f)
        
        # 根据mode处理数据
        if req_info.mode == 'ADD':
            data.append(req_info.cont)
        elif req_info.mode == 'DEL':
            data.pop(req_info.index)
        elif req_info.mode == 'SET':
            data[req_info.index] = req_info.cont

        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON format in file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/saveOps")
async def func(op_info: OpacityArray): 
    # 确保save目录存在
    save_dir = os.path.join(base_dir, 'save')
    os.makedirs(save_dir, exist_ok=True)  # 如果目录不存在则创建
    file_path = os.path.join(save_dir, f'{op_info.fp}_ops.json')
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(op_info.ops, f)

    return True

@app.post("/loadOps")
async def func(op_info: AiLoadReq): 
    file_path = os.path.join(base_dir, 'save', f'{op_info.fp}_ops.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            res = json.load(f)  # 读取JSON文件内容并赋值给load
            return res
            
    return [0]*100  # 返回完整的响应


@app.put("/reqImg")
async def handle_image(req: ImageReq):
    static_dir = os.path.join(base_dir, 'static')
    os.makedirs(static_dir, exist_ok=True)  # 如果目录不存在则创建

    # 构建文件完整路径
    img_path = os.path.join(static_dir, req.imgname)  #名字自带.png
    save_dir = os.path.join(base_dir, 'save')
    os.makedirs(save_dir, exist_ok=True)  # 如果目录不存在则创建
    file_path = os.path.join(save_dir, f'imgname_maps.json')

    # 处理ADD模式：解码Base64并保存为PNG
    if req.mode == "ADD":
        # 移除Base64前缀（如 "data:image/png;base64,"）
        base64_data = req.base64.split(",")[-1]
        image_data = base64.b64decode(base64_data)   
        with open(img_path, "wb") as f:
            f.write(image_data)

    # 处理DEL模式：删除指定图片
    elif req.mode == "DEL":
        if os.path.exists(img_path):
            os.remove(img_path)

        #删除名字映射
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                res = json.load(f)  
                if req.imgname in res:
                    del res[req.imgname]

            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(res, f)

    
    # 处理无效模式
    else:
        raise HTTPException(
            status_code=400,
            detail="mode参数无效，仅支持 'ADD' 或 'DEL'"
        )

@app.post("/reqImgInfoGet")
async def handle_image(req: ImageReq):
    save_dir = os.path.join(base_dir, 'save')
    os.makedirs(save_dir, exist_ok=True)  # 如果目录不存在则创建
    file_path = os.path.join(save_dir, f'imgname_maps.json')

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            res = json.load(f)  
            if req.imgname in res:
                return res[req.imgname]
    
    return ""


@app.post("/reqImgInfoSet")
async def handle_image(req: ImageReq):
    save_dir = os.path.join(base_dir, 'save')
    os.makedirs(save_dir, exist_ok=True)  # 如果目录不存在则创建
    file_path = os.path.join(save_dir, f'imgname_maps.json')

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            res = json.load(f)  
            res[req.imgname] = req.base64   #base64位置暂代图片名字
            if req.base64 == "":
                del res[req.imgname]
                
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(res, f)

    else:
        # 写回文件
        if req.base64 != "":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    req.imgname:req.base64
                }, f)

def delete_dir_fp(dir, fp):
    if not os.path.exists(dir):
        return
    # 遍历目录中的所有文件
    for filename in os.listdir(dir):
        file_path = os.path.join(dir, filename)
        
        # 只处理文件，跳过子目录
        if os.path.isfile(file_path):
            # 检查文件名是否包含fp
            if fp in filename:
                # 删除文件
                os.remove(file_path)
                
@app.put("/clear_all")
async def handle_image(req: Dict):
    debug(f"Request for delete {req['fp']} all!")
    # 清空所有和该指纹相关的记录
    save_dir = os.path.join(base_dir, 'save')
    static_dir = os.path.join(base_dir, 'static')

    delete_dir_fp(save_dir, req['fp'])
    delete_dir_fp(static_dir, req['fp'])
     
               
# if __name__ == '__main__':
#     uvicorn.run(app='Main:app', host="127.0.0.1", port=8225, reload=True)
    
if __name__ == '__main__':
    # 打包环境下需要绝对导入
    from PdfBacken import app  # 明确从Main模块导入app对象
    
    uvicorn.run(
        app,  # 直接使用app对象而不是字符串
        host="127.0.0.1",
        port=8225,
        reload=False,
        log_config=None,
    )