import whisper

# 加载本地模型
model = whisper.load_model("F:/whisper-model/base.pt")

# 转录音频文件
result = model.transcribe("test.mp4")

# 打印转录结果
print(result['text'])