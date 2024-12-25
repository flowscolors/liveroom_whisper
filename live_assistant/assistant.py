import gradio as gr
from utils.live import get_douyin_room_info

def generate_iframe(m3u8_url):
    # 修复 URL 转义问题
    sanitized_url = m3u8_url.replace("\\u0026", "&")
    print(sanitized_url)
    # 动态生成 iframe
    iframe_code = f"""
    <iframe src="/static/player.html?url={sanitized_url}" width="100%" height="600px" frameborder="0" allowfullscreen></iframe>
    """
    return iframe_code
def live_assistant_interface():
    with gr.Tab("直播助手") as tab:
        # 输入 URL 和按钮在同一行
        with gr.Row():
            with gr.Column(scale=8):  # 输入框占 80%
                video_url_input = gr.Textbox(label="直播视频URL", placeholder="输入抖音直播间链接", interactive=True)
            with gr.Column(scale=2):  # 按钮占 20%
                submit_button = gr.Button("确定")

        # 房间信息单独一行
        with gr.Row():
            room_info_display = gr.Markdown("### 输入直播间 URL 后显示直播间信息")

        # 实时视频流和文本提取信息
        with gr.Row():
            # 视频播放器
            with gr.Column(scale=1):
                video_player = gr.HTML(label="视频播放器")

            # 文本提取结果
            with gr.Column(scale=1):
                gr.Markdown("## 实时文本提取")
                text_output = gr.Textbox(label="提取的文本", interactive=False)

        # 点击按钮事件，开始更新页面内容
        submit_button.click(
            fn=update_room_info_and_video,  # 处理函数
            inputs=video_url_input,  # 输入参数
            outputs=[room_info_display, video_player, text_output]  # 输出更新
        )

    return tab
def update_room_info_and_video(live_url):
    """
    获取直播间信息并生成页面内容
    """
    try:
        # 调用 get_douyin_room_info 方法获取直播间信息
        room_info = get_douyin_room_info(live_url)
        if not room_info:
            return "无法获取直播信息，请检查 URL 是否正确", "", "N/A"

        # 解包直播间信息
        hls_url, room_id, room_title, room_user_count = room_info

        # 更新显示的 Markdown 内容
        room_info_md = f"""
        ### 直播间信息
        - **直播间 ID**: {room_id}          **标题**: {room_title}         **用户数**: {room_user_count}
        """

        # 生成 iframe 播放器
        iframe_code = generate_iframe(hls_url)

        # 返回更新内容
        return room_info_md, iframe_code, "文本提取功能待完善"  # 文本提取占位
    except Exception as e:
        return f"错误：{str(e)}", "", "N/A"