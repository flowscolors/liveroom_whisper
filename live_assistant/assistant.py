import subprocess
import threading
import numpy as np
from queue import Queue, Empty  # 正确导入 Empty
from faster_whisper import WhisperModel
from opencc import OpenCC
import gradio as gr
from datetime import datetime
from utils.live import get_douyin_room_info  # 假设您有这个方法来获取直播间信息
from utils.qwen import explain_sensitive_words

# 初始化 Faster-Whisper 模型和 OpenCC 转换器
cc = OpenCC('t2s')  # 繁体中文 -> 简体中文
model_path = "F:/whisper-model/faster-whisper-large-v2"  # 替换为 Whisper 模型路径
whisper_model = WhisperModel(model_path, device="cuda", compute_type="float16")  # 使用 GPU（可改为 CPU）

# 音频队列，用于线程间传递音频数据块
audio_queue = Queue(maxsize=500)

# 全局变量，用于实时更新转录结果
transcription_result = ""

# 全局变量，用于实时更新敏感词分析结果
sensitive_results = []

# 敏感词列表和对应的补充解释
sensitive_words = [
    "违禁品",
    "危险",
    "敏感",
    "退保",
    "理赔",
    "收益",
    "保险",
    "报销",
    "老年",
    "免赔",
    "保障",
    "理赔",
    "谢谢"
]

def detect_sensitive_words(text):
    """
    检测文本中是否包含敏感词，并返回提示和补充解释。
    """
    global sensitive_results

    # 遍历敏感词列表，逐一检测
    for word in sensitive_words:
        if word in text:
            # 调用大模型生成解释
            explanation = explain_sensitive_words(word, text)
            print(explanation)
            sensitive_results.append({'word': word, 'explanation': explanation})

    return None

def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1 / 32768
    return sound.squeeze()
# 封装音频读取逻辑
def read_audio_stream(m3u8_url):
    """
    从 m3u8 流中读取音频，使用 ffmpeg 提取为 PCM 格式，并将音频块放入队列。
    """
    try:
        # 替换 URL 中的 \u0026 为 &
        m3u8_url = m3u8_url.replace("\\u0026", "&")

        command = [
            "ffmpeg",
            "-i", m3u8_url,
            "-f", "wav",
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", "16000",
            "pipe:1"
        ]
        print("---------------------ffmpeg命令---------------------")
        print(command)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)

        while True:
            # 从 ffmpeg 读取音频块
            audio_chunk = process.stdout.read(4096)  # 每次读取 8192 samples (16-bit PCM)
            if not audio_chunk:
                # 检查进程是否已退出
                if process.poll() is not None:
                    stderr = process.stderr.read().decode("utf-8")
                    print(f"FFmpeg 进程退出，错误信息：{stderr}")
                    break
                print("警告：读取到空音频块，但进程仍在运行。")
                continue

            #print("读取音频成功。")
            if not audio_queue.full():
                audio_queue.put(audio_chunk)
                #print("音频放入 audio_chunk 队列")
            else:
                print("队列已满，音频块被丢弃")

    except Exception as e:
        print(f"音频流读取错误：{e}")

    finally:
        if process:
            process.terminate()
            print("FFmpeg 进程已终止。")


# 封装音频转录逻辑
def transcribe_audio():
    """
    从音频队列中提取音频块，收集固定长度（2 秒）的音频后调用 Faster-Whisper 进行转录。
    """
    audio_buffer = b""  # 缓冲区，用于存储音频块
    target_audio_length = 16000 * 2 * 2  # 2 秒音频长度（16000 采样率 x 2 秒 x 2 字节每采样）
    global transcription_result

    while True:
        try:
            # 从队列获取音频块
            audio_chunk = audio_queue.get(timeout=1)  # 如果 1 秒内无数据，则抛出 Empty 异常
            audio_buffer += audio_chunk

            # 如果缓冲区中音频长度达到目标长度，开始转录
            if len(audio_buffer) >= target_audio_length:
                # 转换为 numpy 数组并归一化为 float32
                audio_int16 = np.frombuffer(audio_buffer[:target_audio_length], np.int16)
                audio_float32 = int2float(audio_int16)

                # 使用 Faster-Whisper 模型进行转录
                try:
                    segments, _ = whisper_model.transcribe(audio_float32, beam_size=5, language="zh")
                    result_text = "".join([segment.text for segment in segments])

                    # 将繁体中文转换为简体中文
                    result_text_simplified = cc.convert(result_text)

                    # 检测敏感词
                    detect_sensitive_words(result_text_simplified)

                    # 打印转录结果
                    print(f"实时转录结果（简体中文）：{result_text_simplified}")
                    transcription_result =  transcription_result + result_text_simplified + "\n"
                except Exception as e:
                    print(f"转录错误：{e}")

                # 清空已处理的缓冲区
                audio_buffer = audio_buffer[target_audio_length:]
        except Empty:
            print("音频队列为空，等待新的音频数据...")
        except Exception as e:
            print(f"音频处理错误：{e}")
            continue


# 封装主方法，用于启动音频读取和转录线程
def start_transcription(m3u8_url):
    """
    启动音频读取和转录线程
    """
    # 创建并启动音频读取线程
    audio_thread = threading.Thread(target=read_audio_stream, args=(m3u8_url,))
    audio_thread.daemon = True
    audio_thread.start()

    # 创建并启动音频转录线程
    transcribe_thread = threading.Thread(target=transcribe_audio)
    transcribe_thread.daemon = True
    transcribe_thread.start()


# Gradio 实时更新函数
def get_transcription():
    """
    返回当前的实时转录结果
    """
    global transcription_result
    return transcription_result

def get_sensitive():
    """
    返回当前的实时转录结果
    """
    global sensitive_results
    return sensitive_results


# Gradio 页面构建
def generate_iframe(m3u8_url):
    """
    动态生成 HTML iframe 播放器
    """
    sanitized_url = m3u8_url.replace("\\u0026", "&")
    iframe_code = f"""
    <iframe src="/static/player.html?url={sanitized_url}" width="100%" height="600px" frameborder="0" allowfullscreen></iframe>
    """
    return iframe_code


def update_room_info_and_video(live_url):
    """
    获取直播间信息并更新页面内容
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

        # 启动实时转录
        start_transcription(hls_url)

        # 返回更新内容
        return room_info_md, iframe_code
    except Exception as e:
        return f"错误：{str(e)}", "", ""

# 定时触发更新文本提取内容
def update_text():
    def inner():
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        output = get_transcription()
        return f"欢迎使用,当前时间是: {current_time} ，当前内容 {output}"

    return inner

def update_analysis():
    def inner_analysis():
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        sensitive_data = get_sensitive()
        if sensitive_data:  # 如果有检测到敏感词
            # 将每个敏感词及其解释格式化为一行
            formatted_output = "\n".join(
                [f"敏感词: {item['word']}\n解释: {item['explanation']}" for item in sensitive_data]
            )
        else:  # 如果没有检测到敏感词
            formatted_output = "未检测到敏感词"
        return formatted_output

    return inner_analysis

# Gradio 定时触发更新
def live_assistant_interface():
    with gr.Tab("直播助手") as tab :
        # 输入 URL 和按钮在同一行
        with gr.Row():
            with gr.Column(scale=8):  # 输入框占 80%
                video_url_input = gr.Textbox(label="直播视频URL", placeholder="输入抖音直播间链接")
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

            # 文本提取结果实时更新
            with gr.Column(scale=1):
                gr.Markdown("## 实时文本提取")
                text_output = gr.Textbox(value=update_text(),every=1)
                gr.Markdown("## 智能语音分析")
                sensitive_analysis_output = gr.Textbox(value=update_analysis(), every=1)
        # 点击按钮事件，开始更新页面内容
        submit_button.click(
            fn=update_room_info_and_video,  # 处理函数
            inputs=video_url_input,  # 输入参数
            outputs=[room_info_display, video_player]  # 输出更新
        )


    return tab


