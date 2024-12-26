import websocket
import logging
import time
import traceback
import json
from datetime import datetime

# 配置日志记录，设置日志级别为DEBUG，可按需调整为INFO、WARNING等
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
port = '8888'

# 定义WebSocket服务器地址，根据实际情况修改
WS_SERVER_URL = f"ws://127.0.0.1:{port}"


def on_message(ws, message):
    """
    处理接收到的消息的回调函数
    """
    # logging.info(f"接收到弹幕数据: {message}")
    # 客户端收到服务器的数据，进行解析、存储等操作
    try:
        json_data = json.loads(message)
        if 1 == json_data['Type']:
            data = json.loads(json_data['Data'])
            print("[直播间：{0} room_id：{1}] [time：{2}] [用户：{3}]：{4}".format(data['Onwer']['Nickname'],
                                                                              data['RoomId'],
                                                                              datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                                              data['User']['Nickname'],
                                                                              data['Content']))
    except json.JSONDecodeError as e:
        print(f'json数据解析错误：{e}')

def on_error(ws, error):
    """
    处理WebSocket连接出现错误的回调函数
    """
    logging.error(f"出现错误: {error}")


def on_close(ws):
    """
    处理WebSocket连接关闭的回调函数
    """
    logging.info("WebSocket连接已关闭")


def on_open(ws):
    """
    处理WebSocket连接成功打开的回调函数
    """
    logging.info("已成功连接到WebSocket服务器")
    # 在这里向服务器发送消息
    # ws.send('这是来自客户端的消息')


def connect_to_ws_server():
    """
    尝试连接到WebSocket服务器的函数，包含连接重试机制
    """
    max_retries = 5
    retry_delay = 3  # 重试间隔时间（秒）
    retries = 0
    while retries < max_retries:
        try:
            ws = websocket.WebSocketApp(WS_SERVER_URL,
                                        on_open=on_open,
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.run_forever()
            return ws
        except Exception as e:
            logging.error(f"连接WebSocket服务器失败，尝试次数: {retries + 1}，错误信息: {e}")
            logging.debug(traceback.format_exc())  # 打印详细的异常堆栈信息
            retries += 1
            time.sleep(retry_delay)
    raise ConnectionError("无法连接到WebSocket服务器，已达到最大重试次数")


if __name__ == "__main__":
    try:
        websocket_conn = connect_to_ws_server()
    except ConnectionError as ce:
        logging.critical(ce)

