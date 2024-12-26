import subprocess
import threading
import wave
import numpy as np
from queue import Queue, Empty  # 正确导入 Empty
from faster_whisper import WhisperModel
from opencc import OpenCC

# 初始化 OpenCC 转换器（繁体中文 -> 简体中文）
cc = OpenCC('t2s')

# 音频队列，用于存储音频数据块
audio_queue = Queue(maxsize=50)

# 初始化 Faster-Whisper 模型
model_path = "F:/whisper-model/faster-whisper-large-v2"  # 替换为你的 Whisper 模型路径
whisper_model = WhisperModel(model_path, device="cuda", compute_type="float16")  # 使用 GPU（可改为 CPU）

# 音频格式转换：int16 -> float32
def int2float(sound):
    abs_max = np.abs(sound).max()
    sound = sound.astype('float32')
    if abs_max > 0:
        sound *= 1 / 32768
    return sound.squeeze()


# 保存音频文件（可选，用于调试）
def save_wave_file(audio, filename="output.wav"):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio)


# 音频读取线程：从 m3u8 流中提取音频并写入队列
def read_audio_stream(m3u8_url):
    """
    从 m3u8 流中读取音频，使用 ffmpeg 提取为 PCM 格式，并将音频块放入队列。
    """
    try:
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
        print( command)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10 ** 8)

        while True:
            print("audio_chunk开始读取")
            audio_chunk = process.stdout.read(8192 * 5)  # 每次读取 8192 samples (16-bit PCM)
            print("读取音频成功。")
            if not audio_chunk:
                break
            if not audio_queue.full():
                audio_queue.put(audio_chunk)
               # print("音频放入audio_chunk队列")
            else:
                print("队列已满，音频块被丢弃")
    except Exception as e:
        print(f"音频流读取错误：{e}")


# 音频转录线程：从队列中提取音频块并进行实时转录
def transcribe_audio():
    """
    从音频队列中提取音频块，收集固定长度（2 秒）的音频后调用 Faster-Whisper 进行转录。
    """
    audio_buffer = b""  # 缓冲区，用于存储音频块
    target_audio_length = 16000 * 2 * 2  # 2 秒音频长度（16000 采样率 x 2 秒 x 2 字节每采样）

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

                    # 打印转录结果
                    print(f"实时转录结果（简体中文）：{result_text_simplified}")
                except Exception as e:
                    print(f"转录错误：{e}")

                # 清空已处理的缓冲区
                audio_buffer = audio_buffer[target_audio_length:]
        except Empty:
            continue
          #  print("音频队列为空，等待新的音频数据...")
        except Exception as e:
            print(f"音频处理错误：{e}")
            continue


# 主函数
def main():
    m3u8_url = "http://pull-spe-l3.douyincdn.com/fantasy/stream-404675504787948214.m3u8?auth_key=1735264934-0-0-9398f52bae5547ff2f182af49d49f021\u0026major_anchor_level=vip"  # 替换为实际的 m3u8 URL

    # 创建音频读取线程
    audio_thread = threading.Thread(target=read_audio_stream, args=(m3u8_url,))
    audio_thread.daemon = True
    audio_thread.start()

    # 启动音频转录线程
    transcribe_audio()


if __name__ == "__main__":
    main()