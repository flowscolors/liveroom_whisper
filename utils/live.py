import requests
import re
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
        print(hls_pull_url)
        roomInfo = re.findall(r'"roomInfo\\":({.*?})\}', res.text)[1]
        room_id = re.findall(r'"id_str\\":\\"(.*?)\\",', roomInfo)[0]
        room_title = re.findall(r'"title\\":\\"(.*?)\\",', roomInfo)[0]
        room_user_count = re.findall(r'"user_count_str\\":\\"(.*?)\\",', roomInfo)[0]
        return hls_pull_url,room_id,room_title,room_user_count
    except Exception as e:
        print(f"An error occurred: {e}")
        return None