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
        hls_pull_url = re.findall(r'"hls_pull_url\\":\\"(.*?)\\",', res.text)[0]
        return hls_pull_url
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
