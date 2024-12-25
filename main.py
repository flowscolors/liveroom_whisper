import gradio as gr
from live_assistant import live_assistant_interface
from danmu_capture import danmu_capture_interface
from connect_analysis import connect_analysis_interface
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import requests


# 创建 FastAPI 应用
app = FastAPI()

# 添加 CORS 中间件解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源。可以根据需要限制特定域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 代理服务器，用于解决 CORS 问题
@app.get("/proxy")
async def proxy(url: str):
    try:
        # 转发请求到目标 URL
        response = requests.get(url, stream=True)
        # 将目标服务器的响应转发给客户端
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={
                "Content-Type": response.headers.get("Content-Type", "application/octet-stream"),
                "Access-Control-Allow-Origin": "*",  # 添加跨域头
                "Access-Control-Allow-Methods": "GET, OPTIONS",  # 允许的方法
                "Access-Control-Allow-Headers": "*",  # 允许的请求头
            },
        )
    except Exception as e:
        # 捕获错误并返回失败信息
        return Response(content=f"Error: {str(e)}", status_code=500)

with gr.Blocks() as demo:
    live_assistant_interface()
    danmu_capture_interface()
    connect_analysis_interface()

# 挂载 Gradio 应用
app = gr.mount_gradio_app(app, demo, path="/")

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7860)