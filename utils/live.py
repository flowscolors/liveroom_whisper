import requests
import re
import time
def connection_success():
    return "连接成功！"

def get_hls_stream_url(live_url):
    try:
        res = requests.get(
            url=live_url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            },
            cookies={
                "__ac_nonce": "063abcffa00ed8507d599"  # 可以是任意值
            }
        )
        hls_pull_url_list = re.findall(r'"hls_pull_url\\":\\"(.*?)\\",', res.text)
        hls_pull_url = next((url for url in hls_pull_url_list if 'auth_key' in url), None)
        return hls_pull_url
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_douyin_room_info(live_url):
    """
    获取抖音直播间信息，包括带 auth_key 的 hls_pull_url、房间 ID、标题和观看人数。
    如果没有找到带 auth_key 的 hls_pull_url，会自动重试，最多尝试 max_retries 次。
    """
    retries = 0
    max_retries = 5

    while retries < max_retries:
        try:
            # 发送请求
            res = requests.get(
                url=live_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
                },
                cookies={
                    "__ac_nonce": "063abcffa00ed8507d599"  # 可以是任意值
                }
            )

            # 提取 hls_pull_url
            hls_pull_url_list = re.findall(r'"hls_pull_url\\":\\"(.*?)\\",', res.text)
            hls_pull_url = next((url for url in hls_pull_url_list if 'auth_key' in url), None)

            # 如果找到了带 auth_key 的 hls_pull_url，则解析房间信息并返回
            if hls_pull_url:
                print(f"找到 hls_pull_url: {hls_pull_url}")

                roomInfo = re.findall(r'"roomInfo\\":({.*?})\}', res.text)[1]
                print(roomInfo)

                room_id = re.findall(r'"id_str\\":\\"(.*?)\\",', roomInfo)[0]

                room_title = re.findall(r'"title\\":\\"(.*?)\\",', roomInfo)[0]

                room_user_count = re.findall(r'"user_count_str\\":\\"(.*?)\\",', roomInfo)[0]

                return hls_pull_url, room_id, room_title, room_user_count

            # 如果没有找到带 auth_key 的 hls_pull_url，增加重试次数
            print(f"未找到带 auth_key 的 hls_pull_url，正在重试...（第 {retries + 1} 次）")
            retries += 1

        except Exception as e:
            print(f"请求或解析过程中发生错误：{e}")
            retries += 1

    # 如果达到最大重试次数仍然未找到，返回 None
    print("重试次数已达上限，未能获取到带 auth_key 的 hls_pull_url")
    return None