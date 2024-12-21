import gradio as gr

def danmu_capture():
    return "弹幕抓取功能尚未实现"

def danmu_capture_interface():
    with gr.Tab("弹幕抓取") as tab:
        gr.Markdown("### 弹幕抓取")
        gr.Button("启动弹幕抓取").click(danmu_capture)
    return tab