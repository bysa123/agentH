from fastapi import FastAPI
import pandas as pd
from pathlib import Path
import requests
from fastapi.responses import FileResponse, StreamingResponse
from api_filter import get_label
import io
import asyncio
base_dir = Path(__file__).parent

app = FastAPI()
@app.get("/hello/{name}")
def greet(name: str, age: int=19):
    return {"message": f"信息, {name}!", "age": age}

# 同步迭代器
@app.get("/streamSync")
def stream_sync():
    def generate():
        for i in range(5):
            yield f"第{i}条数据"
    return StreamingResponse(generate(), media_type="text/plain")

# 异步迭代器
@app.get("/streamAsync")
async def stream_async():
    async def generate():
        for i in range(5):
            yield f"第{i}条数据"
            await asyncio.sleep(1)
    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/getLabelsExcel")
def get_labels_excel():
    file_path = base_dir / "data" / "系统标签.xlsx"
    return FileResponse(file_path, filename="系统标签.xlsx")


@app.get("/getLabelsExcelStreaming")
def get_labels_excel_stream():
    file_path = base_dir / "data" / "系统标签.xlsx"
    return StreamingResponse(
        open(file_path, "rb"),
        media_type="application/vnd.ms-excel",
        headers={"Content-Disposition": f"attachment; filename={file_path.name}"},
    )

@app.get("/getLabelCSV")
def get_label_csv():
    filter_data = get_label()
    if not filter_data:
        return {"message": "没有数据"}
    df = pd.DataFrame(filter_data)
    stream = io.StringIO()
    df.to_csv(stream, index=False, encoding="utf-8-sig")
    stream.seek(0)
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=系统标签.csv"},
    )

@app.get("/sse/hello")
async def sse_hello():
    async def generate():
        for i in range(5):
            # ✅ SSE 标准格式：data: 内容 + 两个换行
            yield f"data: 第 {i} 条消息\n\n"
            await asyncio.sleep(1)
        yield "data: [DONE]\n\n"
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",            # ✅ SSE 专属 MIME 类型
        headers={
            "Cache-Control": "no-cache",            # ✅ 禁止缓存，确保实时
            "X-Accel-Buffering": "no",              # ✅ Nginx 反代时也要关闭缓冲
        },
    )
    




