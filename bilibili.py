import base64
import sys
import requests


class Bilibili:
    def __init__(self):
        self.session = requests.session()
        self.csrf = None

    def login(self, username, password):
        """
        调用第三方API，请谨慎使用
        详情见：http://docs.kaaass.net/showdoc/web/#/2?page_id=3
        :param username:登录的用户名
        :param password:密码
        :return:
        """
        req = self.post(
            url='https://api.kaaass.net/biliapi/user/login',
            data={
                'user': username,
                'passwd': password
            }
        )
        if req['status'] == 'OK':
            login = self.get(
                url='https://api.kaaass.net/biliapi/user/sso',
                params={
                    'access_key': req['access_key']
                }
            )
            if login['status'] == 'OK':
                print(login['cookie'])
                cookies = {}
                for line in login['cookie'].split(';')[:-1]:
                    name, value = line.strip().split('=')
                    cookies[name] = value
                cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
                self.session.cookies = cookies
                self.csrf = self.session.cookies.get('bili_jct')
                return True
            else:
                return login

    def login_by_cookies(self, path):
        with open(path, 'r') as f:
            cookies = {}
            for line in f.read().split(';'):
                name, value = line.strip().split('=', 1)
                cookies[name] = value
            cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
            self.session.cookies = cookies
            self.csrf = self.session.cookies.get('bili_jct')
            print("Cookies设置成功")

    def post(self, url, data, headers=None):
        while True:
            try:
                if headers is None:
                    req = self.session.post(url, data=data, timeout=5)
                else:
                    req = self.session.post(url, data=data, headers=headers, timeout=5)
                if req.status_code == 200:
                    try:
                        return req.json()
                    except Exception as e:
                        print(e)
                        return req.text
                else:
                    print("状态码不是200！请检查错误\n" + req.text)
                    sys.exit(0)
            except Exception as e:
                print("POST出错\n%s" % str(e))

    def get(self, url, params=None, headers=None):
        while True:
            try:
                if params is None:
                    if headers is None:
                        req = self.session.get(url, timeout=5)
                    else:
                        req = self.session.get(url, headers=headers, timeout=5)
                else:
                    if headers is None:
                        req = self.session.get(url, params=params, timeout=5)
                    else:
                        req = self.session.get(url, params=params, headers=headers, timeout=5)
                if req.status_code == 200:
                    try:
                        return req.json()  # 如果得到数据是json格式，返回json对象
                    except:
                        return req.text  # 不是json格式，直接返回内容
                else:
                    print("状态码不是200！请检查错误\n" + req.text)
                    sys.exit(0)
            except Exception as e:
                print("GET出错\n%s" % str(e))

    def user_info(self):
        """
        获取当前用户的信息
        :return:
        """
        req = self.get(
            url='https://member.bilibili.com/x/web/white'
        )
        return req

    def upload_cover(self, path):
        """
        上传封面，返回封面url地址
        :param path: 图片路径
        :return:
        """
        with open(path, 'rb') as f:
            req = self.post(
                url='https://member.bilibili.com/x/vu/web/cover/up',
                data={
                    "cover": 'data:image/jpeg;base64,' + base64.b64encode(f.read()).decode('utf-8'),
                    "csrf": self.csrf
                }
            )
            if req['code'] == 0 and req['message'] == '0':
                return req['data']['url']

    def report(self, cid, dmid, reason, content=None):
        """
        举报弹幕
        :param cid:     弹幕所在cid号
        :param dmid:    弹幕id号
        :param reason:  1违法违禁 2色情低俗 3赌博诈骗 4人身攻击 5侵犯隐私
                        6垃圾广告 7引战 8剧透 9恶意刷屏 10视频无关
                        11其他(带content) 12青少年不良信息
        :param content:
        """
        req = self.post(
            url='https://api.bilibili.com/x/dm/report/add',
            data={
                'cid': cid,
                'dmid': dmid,
                'reason': reason,
                'content': '' if content is None else content,
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("code = 0 举报成功")
        elif req['code'] == 36201:
            print('code = 36201 弹幕不存在')
        elif req['code'] == 36204:
            print('code = 36204 已举报')

    def stat(self, aid):
        """
            获得稿件的播放数等信息，返回一个元组
            [稿件id,播放数，弹幕数，回复，收藏，硬币，分享，点赞，
            目前排名，历史最高排名，是否禁止转载，稿件类型(自制/转载)]
            :param aid: 稿件编号，不含av前缀
            :return: 列表
            """
        req = self.get(
            url='https://api.bilibili.com/x/web-interface/archive/stat',
            params={'aid': aid}
        )
        print(req)
        if req['code'] == 0:
            return (req['data']['aid'],
                    req['data']['view'],
                    req['data']['danmaku'],
                    req['data']['reply'],
                    req['data']['favorite'],
                    req['data']['coin'],
                    req['data']['share'],
                    req['data']['like'],
                    req['data']['now_rank'],
                    req['data']['his_rank'],
                    req['data']['no_reprint'],
                    req['data']['copyright']
                    )

    def upstat(self, mid):
        """
        获得稿件播放总数和专栏浏览总数,
        需要带UA访问
        :param mid:用户mid
        :return:字典
        """
        req = self.get(
            url='https://api.bilibili.com/x/space/upstat',
            params={'mid': mid},
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                   'Chrome/67.0.3396.99 Safari/537.36'}
        )
        return {
            'archive': req['data']['archive']['view'],
            'article': req['data']['article']['view']
        }
