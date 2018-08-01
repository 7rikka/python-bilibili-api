import sys

import requests


class Bilibili:
    def __init__(self):
        self.session = requests.session()

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
