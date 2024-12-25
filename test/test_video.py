import gradio as gr
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

# 动态生成 iframe
def generate_iframe(m3u8_url):
    # 修复 URL 转义问题
    sanitized_url = m3u8_url.replace("\\u0026", "&")
    # 动态生成 iframe
    iframe_code = f"""
    <iframe src="/static/player.html?url={sanitized_url}" width="100%" height="600px" frameborder="0" allowfullscreen></iframe>
    """
    return iframe_code

# 创建 Gradio 界面
with gr.Blocks() as demo:
    m3u8_url_input = gr.Textbox(label="M3U8 URL", placeholder="输入 M3U8 视频流链接")
    video_player = gr.HTML()
    m3u8_url_input.change(generate_iframe, inputs=m3u8_url_input, outputs=video_player)

# 挂载 Gradio 应用
app = gr.mount_gradio_app(app, demo, path="/")

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=7860)