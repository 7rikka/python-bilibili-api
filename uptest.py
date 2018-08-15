import math
import os
import re
import sys
import time

from bilibili import Bilibili

vod = '296911304'  # 录像id
channel = 'shroud'  # twitch.tv/wadu 主播的id
client_id = '4zswqk0crwt2wy4b76aaltk2z02m67'  # 自己申请的client id
workdir='/root/twitch'
copystr = ''

username = '8016093861'
password = 'a123456789'
def get_size(path):
    return str(os.path.getsize(path))
def upload(path, fn):
    print("[提示]Step1.请求上传地址信息")
    r = b.get(
        url='https://member.bilibili.com/preupload',
        params={
            'os': 'upos',
            'upcdn': 'ws',
            'name': fn,
            'size': get_size(path),
            'r': 'upos',
            'profile': 'ugcupos/yb',
            'ssl': '0'
        }
    )
    # print(r)
    upos_uri = r['upos_uri']
    biz_id = r['biz_id']
    endpoint = r['endpoint']
    auth = r['auth']
    print('[提示]获得upos_url: ' + upos_uri[11:])
    print('[提示]获得biz_id: ' + str(biz_id))
    print('[提示]获得endpoint: ' + endpoint)
    print('[提示]获得auth: ' + auth)
    print('[提示]目标URL: https:' + endpoint + '/ugc/' + upos_uri[11:] + '?uploads&output=json')
    u = 'https:' + endpoint + '/ugc/' + upos_uri[11:] + '?uploads&output=json'

    print("[提示]Step.2.准备上传")
    s2 = b.options(
        url='https:' + endpoint + '/ugc/' + upos_uri[11:] + '?uploads&output=json'
    )
    print("[提示]Step.2.OPTIONS成功")
    s3 = b.post(
        url='https:' + endpoint + '/ugc/' + upos_uri[11:] + '?uploads&output=json',
        data={},
        headers={'X-Upos-Auth': auth}

    )
    print("[提示]Step.2.POST成功")
    upload_id = s3['upload_id']
    print("[提示]Step.2.获得upload_id:" + upload_id)

    CHUNK_SIZE = 4 * 1024 * 1024
    print("[提示]分块大小:" + str(CHUNK_SIZE))
    filesize = os.path.getsize(path)
    print("[提示]文件大小" + str(filesize))
    chunks_num = math.ceil(filesize / CHUNK_SIZE)
    print("[提示]分块数量:" + str(chunks_num))
    with open(path, 'rb') as f:
        chunks_index = 0
        t1 = time.time()
        while True:
            chunks_data = f.read(CHUNK_SIZE)
            if chunks_index == chunks_num:
                break
            params = {
                'partNumber': str(chunks_index + 1),  # 1开始
                'uploadId': upload_id,
                'chunk': str(chunks_index),  # 0开始
                'chunks': str(chunks_num),
                'size': len(chunks_data),
                'start': str(chunks_index * CHUNK_SIZE),
                'end': str(chunks_index * CHUNK_SIZE + len(chunks_data)),
                'total': str(filesize)
            }
            # print(params)
            # print(u)
            print("[提示]Step.3.请求上传块:" + str(chunks_index + 1))
            b.options(url=u)
            print("[提示]Step.3.开始上传块:" + str(chunks_index + 1))
            b.put(u, data=chunks_data, params=params, headers={'X-Upos-Auth': auth})

            chunks_index += 1
        t2 = time.time()
    print("[提示]Step.4.确认上传完成")
    queren = {
        'output': 'json',
        'name': fn,
        'profile': 'ugcupos/yb',
        'uploadId': upload_id,
        'biz_id': str(biz_id)
    }
    print("[提示]Step.4.OPTIONS成功")
    b.options(url=u, params=queren)
    dl = []
    for i in range(0, int(chunks_num)):
        dl.append({"partNumber": i, "eTag": "etag"})
    data = {'parts': dl}
    print("[提示]Step.4.POST成功")
    b.post(url=u, data=data, params=queren, headers={'X-Upos-Auth': auth})
    print("用时：" + str(t2 - t1))
    return upos_uri[11:-4]
# def tscopy():
##############################################################
def isLogin(session):
    req = session.get('https://api.vc.bilibili.com/feed/v1/feed/get_attention_list')
    print(req)
    code = re.findall("'code': (\\d+)",str(req))[0]
    print(code)
    if code == '0':
        print("[提示]登录成功！")
    else:
        print("[提示]cookies失效！")
        print("[提示]登录返回信息为："+req)
        sys.exit(1)
b = Bilibili()
# b.login(username, password)
b.login_by_cookies('cook.txt')
isLogin(b)
f='1.mp4'
fns=upload(f,f)
while True:
    cover = b.get('https://member.bilibili.com/x/web/archive/recovers?fns=' + fns)
    print(cover)
    time.sleep(2)

data={
    "copyright": infodict.get("copyright"),
    "source": infodict.get("source"),
    "tid": infodict.get("tid"),
    "cover": infodict.get("cover"),
    "title": infodict.get("title"),
    "tag": infodict.get("tag"),
    "desc_format_id": infodict.get("desc_format_id"),
    "desc": infodict.get("desc"),
    "dynamic": infodict.get("dynamic"),
    "videos": infodict.get("")

            }