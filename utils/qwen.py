import os
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def explain_sensitive_words(word, context_text=None):
    """
    调用大模型 Qwen-Max 动态生成敏感词解释。
    """
    # 引入上下文的提示词
    prompt = f"""
    以下是一个敏感词检测场景。敏感词为：'{word}'。
    请基于敏感词生成一句话，必须要使用足够简洁的语言给出20个词左右的专业的解释，指出该词可能的风险或含义。
    """
    # 如果提供了上下文文本，追加上下文信息
    if context_text:
        prompt += f"\n上下文内容为：'{context_text}'。请结合上下文进行分析。"

    # 调用大模型
    completion = client.chat.completions.create(
        model="qwen-max",  # 使用阿里云通义千问-Max 模型
        messages=[
            {'role': 'system', 'content': '你是一个保险专业的直播敏感词分析助手，可以帮助检测分析直播的文本中是否有不符合保险行业规范的关键词，并解释敏感词的潜在含义和风险。'},
            {'role': 'user', 'content': prompt}
        ],
    )

    # 打印模型返回的完整响应（用于调试）
    print(completion.model_dump_json())

    # 返回生成的解释
    return completion.choices[0].message.content
