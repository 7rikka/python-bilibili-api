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
