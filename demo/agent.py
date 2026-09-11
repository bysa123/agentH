# function calling: json schema 定义约束,工具执行与结果反馈
# json schema: 告诉大模型工具的准确用法，校验大模型输出的json是否合法，不合法就拒绝调用，将函数签名变成大模型可以理解的说明书
# ReAct 推理框架：怎么决定什么时候用工具，用哪个工具，用完了怎么思考， think -> act -> observe -> think -> act -> observe -> ...
# 框架选型： dify/coke 框架, langchain (工程化) autoGen(多agent协作)
# dify/coke: 把agent,RAG，工作流，工具调用做成可视化低代码页面
# 记忆管理：短期：滑动窗口+摘要 长期：向量数据库
# 先单agent后多agent
# 数据分析agent

import json
import dashscope
from dashscope import Generation
from typing import List, Dict, Any, Optional

# ====================== 配置 ======================
dashscope.api_key = "sk-ws-H.PDMHRXM.gn7P.MEUCICkp69SIzEw8QK6jBmgwhznhLcFBvIol2jzjiU6Bc-G9AiEAiLoHmWsOHXD1xjS3ycecisCdNJYx4wAXdWU0khZmwqg"

# ====================== 1. 定义工具（用 Pydantic 自动生成 JSON Schema）======================
from pydantic import BaseModel, Field
from typing import Literal

# 工具 1：数据分析
class AnalyzeSalesParams(BaseModel):
    data_path: str = Field(description="Excel 或 CSV 文件的路径")
    metric: Literal["销量", "销售额", "增长率"] = Field(description="分析指标，只能三选一")
    top_n: int = Field(default=5, ge=1, le=20, description="返回前 N 名，1~20 之间")

# 工具 2：查询天气（演示多工具场景）
class QueryWeatherParams(BaseModel):
    city: str = Field(description="城市名称，比如 北京、上海")
    date: Optional[str] = Field(default=None, description="查询日期，YYYY-MM-DD 格式，不传默认今天")

# 把 Pydantic 类转成 dashscope 需要的 tools 格式
def make_tool(pydantic_model, name: str, description: str) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": pydantic_model.model_json_schema(),
        }
    }

TOOLS = [
    make_tool(AnalyzeSalesParams, "analyze_sales", "分析销售数据文件，返回销量/销售额/增长率排名"),
    make_tool(QueryWeatherParams, "query_weather", "查询指定城市的天气信息"),
]

# ====================== 2. 工具的真实实现 ======================
import pandas as pd

def analyze_sales(data_path: str, metric: str, top_n: int = 5) -> str:
    """真实的数据分析逻辑"""
    try:
        df = pd.read_excel(data_path) if data_path.endswith(".xlsx") else pd.read_csv(data_path)
        col_map = {"销量": "quantity", "销售额": "amount", "增长率": "growth_rate"}
        col = col_map.get(metric)
        if not col:
            return f"错误: 不支持的指标 {metric}"
        top = df.nlargest(top_n, col)[["product_name", col]].to_dict("records")
        return json.dumps({"metric": metric, "top": top}, ensure_ascii=False)
    except Exception as e:
        return f"错误: {str(e)}"

def query_weather(city: str, date: Optional[str] = None) -> str:
    """真实的天气查询逻辑（这里 mock 一下）"""
    date_str = date or "今天"
    # 实际生产里这里调真正的天气 API，比如高德天气
    mock_data = {"北京": "晴，25℃", "上海": "多云，28℃", "广州": "暴雨，30℃"}
    weather = mock_data.get(city, f"{city} 未知天气，26℃")
    return json.dumps({"city": city, "date": date_str, "weather": weather}, ensure_ascii=False)

# 工具名 → 函数的映射表
TOOL_MAP = {
    "analyze_sales": analyze_sales,
    "query_weather": query_weather,
}

# ====================== 3. ReAct 推理框架（核心循环）======================
def run_agent(user_question: str, max_steps: int = 10) -> str:
    """
    ReAct 循环：思考 → 行动 → 观察 → 再思考 → ... → 最终答案
    max_steps 防止死循环（大模型一直调工具）
    """
    # 初始化消息历史
    messages = [
        {"role": "system", "content": """你是一个智能助手，可以调用以下工具帮助用户：
- analyze_sales: 分析销售数据
- query_weather: 查询天气

每次只能调用一个工具。如果用户的问题不需要工具，直接回答即可。"""},
        {"role": "user", "content": user_question},
    ]

    print(f"\n🧑 用户: {user_question}")

    for step in range(1, max_steps + 1):
        print(f"\n{'='*40}")
        print(f"🔄 ReAct 第 {step} 轮")
        print(f"{'='*40}")

        # ------ 思考：大模型根据 messages 决定下一步 ------
        resp = Generation.call(
            model="qwen-plus",
            messages=messages,
            tools=TOOLS,              # JSON Schema 工具定义
            result_format="message",
        )
        assistant_msg = resp.output.choices[0].message
        print(f"🧠 思考: {assistant_msg.content or '(决定调用工具)'}")
        
        # ------ 判断：要不要调工具？ ------
        if not hasattr(assistant_msg, 'tool_calls') or not assistant_msg.tool_calls:
            # 大模型没有输出 tool_calls，说明它认为可以直接回答了
            print(f"\n🤖 最终答案: {assistant_msg.content}")
            return assistant_msg.content

        # ------ 行动：调工具 ------
        tool_call = assistant_msg.tool_calls[0]
        print(f"   工具调用: {tool_call}")
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])
        print(f"🛠️  调用工具: {tool_name}")
        print(f"   参数: {json.dumps(tool_args, ensure_ascii=False, indent=2)}")

        # 真实调用 Python 函数
        tool_func = TOOL_MAP.get(tool_name)
        if not tool_func:
            observation = f"错误: 未知工具 {tool_name}"
        else:
            observation = tool_func(**tool_args)
        print(f"👀 观察: {observation}")

        # ------ 观察：把工具返回值喂回消息历史 ------
        messages.append(assistant_msg)          # 大模型刚才的思考 + 工具调用
        messages.append({                      # 工具返回的结果
            "role": "tool",
            "name": tool_name,
            "content": observation,
        })

    # 超过最大步数还没结束
    return "抱歉，我尝试了多次但没能完成你的问题"

# ====================== 4. 测试 ======================
if __name__ == "__main__":
    # 测试 1：需要调工具的
    # run_agent("帮我分析 sales.xlsx 里销售额前 3 的产品")

    # 测试 2：不需要调工具的（大模型直接回答）
    # run_agent("你好，你能做什么？")

    # 测试 3：先调一个工具，拿到结果后可能还想调另一个
    run_agent("帮我查北京今天的天气")