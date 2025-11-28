import os
import cloudpss # 引入 cloudpss 依赖
import json
import time
from config import Config

def generate_IEEE3_table():
    
    # 申请 token
    cloudpss.setToken(Config.CLOUDPSS["TOKEN"])

    # 设置算例所在的平台地址
    os.environ['CLOUDPSS_API_URL'] = Config.CLOUDPSS["API_URL"]
    
    # 获取指定 rid 的算例项目
    model = cloudpss.Model.fetch('model/jiangxiaoxuan0721/a39')
    
    # 选择参数方案，若未设置，则默认用 model 的第一个 config（参数方案）
    config = model.configs[0]

    # 选择计算方案，若未设置，则默认用 model 的第一个 job（潮流计算方案）
    job = model.jobs[0]

    # 启动计算任务
    runner = model.run(job,config) # 运行计算方案
    while not runner.status(): 
        logs = runner.result.getLogs() # 获得运行日志
        for log in logs: 
            print(log) #输出日志
        time.sleep(1)
    
    # 存储潮流计算结果到本地 json 文件
    with open(f'{Config.OUTPUT_DIR}/IEEE3_bus.json','w') as f:
        json.dump(runner.result.getBuses(),f,indent=4)
    # 存储节点计算结果到本地 json 文件
    with open(f'{Config.OUTPUT_DIR}/IEEE3_branch.json','w') as f:
        json.dump(runner.result.getBranches(),f,indent=4)
        
    return "success"