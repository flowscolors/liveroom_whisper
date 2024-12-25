import json
import re
from urllib.parse import unquote_plus
import requests

res = requests.get(
    url="https://live.douyin.com/646454278948",
    #url="https://live.douyin.com/239390079803",
    #url="https://live.douyin.com/80017709309",
    headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    },
    cookies={
        "__ac_nonce": "063abcffa00ed8507d600"  # 可以是任意值
    }
)
hls_pull_url_list = re.findall(r'"hls_pull_url\\":\\"(.*?)\\",', res.text)
print(hls_pull_url_list)
hls_pull_url = next((url for url in hls_pull_url_list if 'auth_key' in url), None)
print(hls_pull_url)

roomInfo = re.findall(r'"roomInfo\\":({.*?})\}', res.text)[1]
print(roomInfo)

room_id = re.findall(r'"id_str\\":\\"(.*?)\\",', roomInfo)[0]

room_title = re.findall(r'"title\\":\\"(.*?)\\",', roomInfo)[0]

room_user_count = re.findall(r'"user_count_str\\":\\"(.*?)\\",', roomInfo)[0]

print(room_id,room_title,room_user_count)