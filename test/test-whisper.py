import whisper

# 加载本地模型
model = whisper.load_model("F:/whisper-model/large-v3.pt")

print("Whisper 模型加载成功")
# 转录音频文件
result = model.transcribe("test.mp4")

# 打印转录结果
print(result['text'])