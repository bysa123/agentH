# 1. 调用公开模拟接口获取用户列表数据
# 2. 对数据做简单清洗过滤
# 3. 记录当前处理时间，封装实体类
# 4. 将处理后的数据保存到本地 json 文件
# 5. 异常捕获，网络失败、文件异常不会直接崩溃
# 6. 文件被其他脚本导入时不会自动执行逻辑
import requests
from pathlib import Path
import pandas as pd
base_dir = Path(__file__).resolve().parent
def get_label():
    url="https://damtest.baowugroup.com/df-assets-manager/service/BEXY51/querySysLabelTree"
    headers = {
        "cookie": "DF-ASSETS-MANAGERSESSION=ZjBhZDlhNmEtZjM2Mi00YTVlLWFhNTgtYTY1NTJmOGUzMTE1",
    }
    body = {"__version__":"2.0","__sys__":{"name":"","descName":"","msg":"","msgKey":"","detailMsg":"","status":0,"traceId":""},"__blocks__":{"inqu_status":{"attr":{},"meta":{"desc":"","attr":{},"columns":[{"pos":0,"name":"parentLabelId"},{"pos":1,"name":"orgCode"},{"pos":2,"name":"filterType"},{"pos":3,"name":"filterStr"}]},"rows":[["","BSTA","system",""]]},"result":{"attr":{"offset":0,"limit":-999999},"meta":{"desc":"","attr":{},"columns":[]},"rows":[]}}}
    try:
        print("开始请求接口获取系统标签")
        res = requests.post(url, headers=headers, json=body, timeout=5);
        # 如果 HTTP 状态码是 **4xx（400、401、403、404）或者 5xx（500、502、503）**，就**主动抛出 `requests.exceptions.HTTPError` 异常**
        res.raise_for_status()
        columns = res.json()["__blocks__"]["result"]["meta"]["columns"]
        data = res.json()["__blocks__"]["result"]["rows"]
        # zip(list1, list2) 将两个列表按位置两两配对成元组{id, "122"} list1 = ["id", "name"] list2 = ["122", "张三"]
        # dict(zip()) 将元组转换为字典 {id: "122"}
        dictData = [dict(zip([col["name"] for col in columns], row)) for row in data]
        filter_data = [item for item in dictData if item["parentLabelId"] == "系统标签"]
        print(filter_data)
        # save_data_to_excel(filter_data, base_dir / "data" / '系统标签.xlsx')
        return filter_data

    except requests.exceptions.HTTPError as e:
        # 捕获4xx 5xx
        print(f"http状态异常: {e}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        exit(1)
    except Exception as e:
        print(f"其他异常: {e}")
        exit(1)

def save_data_to_excel(data, file_path):
    try:
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
    except Exception as e:
        print(f"保存数据到Excel文件异常: {e}")
        exit(1)

if __name__ == "__main__":
    get_label()

# message的三种角色:
# role + content组成
# role: 
# system-系统提示: 给模型定人设和规则边界,影响整个对话的行为,优先级最高,模型严格遵守
# user-用户提示: 用户输入,模型根据用户输入生成回复
# assistant-模型回复: 模型已经回答过的内容,多轮对话时必须带上

# from openai import OpenAI
# client = OpenAI(
#     api_key="sk-",
#     base_url="https://api.openai.com/v1",
# )

# message = [
#     {"role": "system", "content": "你是一个专业的系统标签助手"},
#     {"role": "user", "content": "请获取所有系统标签"},
# ]

# response = client.chat.completions.create(
#     model="gpt-3.5-turbo",
#     messages=message,
#     temperature=0.5, # 创造性, 0=严谨,1=发散
# )
# replay = response.choices[0].message.content
# print(replay)

# SSE Server-Sent Events 服务器向浏览器单向推送数据的技术,用于实时更新数据,无需刷新页面
# # 客户端需要使用 fetch API 或 WebSocket 连接服务器,服务器会返回一个流,客户端可以实时接收数据
# http是一问一答的,客户端请求一次,服务器响应一次,连接会关闭
# websocket 是一种双工通信协议,客户端和服务器可以同时发送数据,连接不会关闭
# 底层技术: 本质是http, 基于StreamingResponse 实现,用生成器yield一段一段数据


# @app.get("/chat/stream")
# async def chat_stream(prompt: str):
#     def generate():
#         stream = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "你是一个专业的助手"},
#                 {"role": "user", "content": prompt}],
#             temperature=0.5, # 创造性, 0=严谨,1=发散
#             stream=True
#         )
#         for chunk in stream:
#             if chunk.choices[0].delta.content:
#             #sse格式： data：内容\n\n
#                 yield f"data: {chunk.choices[0].delta.content}\n\n"
#         yield "data: done\n\n"
#     return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

# 调用chat/stream接口,就可以看到实时推送
    