import gradio as gr
from utils.live import  get_hls_stream_url
from utils.whisper import speech_to_text

def analyze_video(url):
    # 获取直播视频
    video_info = get_hls_stream_url(url)

    # 模拟语音到文本的转换
    extracted_text = speech_to_text(None)  # 暂时传递None作为音频输入

    print(video_info)

    # 返回视频流URL和提取的文本
    return video_info, extracted_text

def live_assistant_interface():
    with gr.Tab("直播助手") as tab :
        with gr.Column(scale=1):
            gr.Markdown("### 输入直播视频URL")
            video_url_input = gr.Textbox(label="直播视频URL")
            submit_button = gr.Button("确定")
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 实时视频流")
                video_output = gr.Video()

            with gr.Column(scale=1):
                gr.Markdown("## 实时文本提取")
                text_output = gr.Textbox(label="提取的文本", interactive=False)

            # 设置按钮点击行为并指定输出到特定组件
            submit_button.click(
                fn=analyze_video,  # 指定处理函数
                inputs=video_url_input,  # 输入组件
                outputs=[video_output, text_output]  # 输出到视频和文本组件
            )

    return tab
