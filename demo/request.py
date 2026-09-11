import requests
import json
from pathlib import Path
# 1. 批量循环调用接口，把返回数据写入 excel（requests + pandas）
# 2. 读取本地 json，循环 post 推送到后端服务
# 3. 写脚本做接口冒烟测试

base_dir = Path(__file__).resolve().parent
output_file = base_dir / "data" / "result.json"

def demo_post_json():
    url="https://damtest.baowugroup.com/df-assets-manager/service/BEXY51/querySysLabelTree"
    headers = {
        "cookie": "DF-ASSETS-MANAGERSESSION=ZjBhZDlhNmEtZjM2Mi00YTVlLWFhNTgtYTY1NTJmOGUzMTE1",
    }
    body = {"__version__":"2.0","__sys__":{"name":"","descName":"","msg":"","msgKey":"","detailMsg":"","status":0,"traceId":""},"__blocks__":{"inqu_status":{"attr":{},"meta":{"desc":"","attr":{},"columns":[{"pos":0,"name":"parentLabelId"},{"pos":1,"name":"orgCode"},{"pos":2,"name":"filterType"},{"pos":3,"name":"filterStr"}]},"rows":[["","BSTA","system",""]]},"result":{"attr":{"offset":0,"limit":-999999},"meta":{"desc":"","attr":{},"columns":[]},"rows":[]}}}
    try:
        print(f"请求URL: {url}")
        resp = requests.post(url, headers=headers, json=body, timeout=5)
        print(resp.status_code)
        columns = resp.json().get("__blocks__", {}).get("result", {}).get("meta", {}).get("columns", [])
        print(columns)
        res = resp.json().get("__blocks__", {}).get("result", {}).get("rows", [])
        # print(res)
        # 将返回结果与对应的属性列名组合成字典列表
        res = [dict(zip([col["name"] for col in columns], row)) for row in res]
        print(res)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        return res
        
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        exit(1)

def save_json_to_excel(data, excel_file):
    import pandas as pd
    try:
        df = pd.DataFrame(data)
        df.to_excel(excel_file, index=False)
        print(f"已将数据保存为 {excel_file}")
    except Exception as e:
        print(f"保存为Excel失败: {e}")

if __name__ == "__main__":
    result = demo_post_json()
    save_json_to_excel(result, base_dir / "data" / "result.xlsx")
