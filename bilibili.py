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
            for line in f.read().split(';')[:-1]:
                name, value = line.strip().split('=', 1)
                cookies[name] = value
            cookies = requests.utils.cookiejar_from_dict(cookies, cookiejar=None, overwrite=True)
            self.session.cookies = cookies
            self.csrf = self.session.cookies.get('bili_jct')
            print("Cookies设置成功")

    def post(self, url, data, headers=None, params=None):
        while True:
            try:
                if headers is None:
                    if params is None:
                        req = self.session.post(url, data=data, timeout=5)
                    else:
                        req = self.session.post(url, data=data, params=params, timeout=5)
                else:
                    if params is None:
                        req = self.session.post(url, data=data, headers=headers, timeout=5)
                    else:
                        req = self.session.post(url, data=data, headers=headers, params=params, timeout=5)
                if req.status_code == 200:
                    try:
                        return req.json()
                    except Exception as e:
                        print("[提示]JSON化失败:"+str(e)+"\n[提示]内容为:"+req.text)
                        return req.text
                else:
                    print("[提示]状态码为"+str(req.status_code)+"！请检查错误\n[提示]" + req.text)
                    sys.exit(0)
            except Exception as e:
                print("[提示]POST出错\n[提示]%s" % str(e))

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
                        return req.json()
                    except Exception as e:
                        print("[提示]JSON化失败:" + str(e) + "\n[提示]内容为:" + req.text)
                        return req.text
                else:
                    print("[提示]状态码为" + str(req.status_code) + "！请检查错误\n[提示]" + req.text)
                    sys.exit(0)
            except Exception as e:
                print("[提示]GET出错\n[提示]%s" % str(e))

    def options(self, url, params=None, headers=None):
        while True:
            try:
                if params is None:
                    if headers is None:
                        req = self.session.options(url, timeout=5)
                    else:
                        req = self.session.options(url, headers=headers, timeout=5)
                else:
                    if headers is None:
                        req = self.session.options(url, params=params, timeout=5)
                    else:
                        req = self.session.options(url, params=params, headers=headers, timeout=5)
                if req.status_code == 200:
                    try:
                        return req.json()
                    except Exception as e:
                        print("[提示]JSON化失败:" + str(e) + "\n[提示]内容为:" + req.text)
                        return req.text
                else:
                    print("[提示]状态码为" + str(req.status_code) + "！请检查错误\n[提示]" + req.text)
                    sys.exit(0)
            except Exception as e:
                print("[提示]OPTIONS出错\n[提示]%s" % str(e))

    def put(self, url, data, params=None, headers=None):
        while True:
            try:
                if params is None:
                    if headers is None:
                        req = self.session.put(url, data=data)
                    else:
                        req = self.session.put(url, data=data, headers=headers)
                else:
                    if headers is None:
                        req = self.session.put(url, data=data, params=params)
                    else:
                        req = self.session.put(url, data=data, params=params, headers=headers)
                if req.status_code == 200:
                    try:
                        return req.json()
                    except Exception as e:
                        print("[提示]JSON化失败:" + str(e) + "\n[提示]内容为:" + req.text)
                        return req.text
                else:
                    print("[提示]状态码为" + str(req.status_code) + "！请检查错误\n[提示]" + req.text)
                    sys.exit(0)
            except Exception as e:
                print("[提示]PUT出错\n[提示]%s" % str(e))

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

    def pagelist(self, aid):
        """
            获得稿件的分p，cid等信息的列表，每条信息封装为一个元组
            (分p的cid,分p序号,分p标题,持续时间(单位为秒))
            :param s: session
            :param aid: 稿件aid，不含av前缀
            :return:稿件信息列表
        """
        req = self.get(
            url='https://api.bilibili.com/x/player/pagelist',
            params={'aid': aid}
        )
        data = req['data']
        plist = []
        for d in data:
            plist.append((d['cid'],
                          d['page'],
                          d['part'],
                          d['duration'])
                         )
        return plist

    def search_default(self):
        """
        获取搜索框的默认关键字
        :return:dict
        """
        req = self.get(
            url='https://api.bilibili.com/x/web-interface/search/default'
        )
        return {
            'type': req['data']['type'],
            'seid': req['data']['seid'],
            'id': req['data']['id'],
            'show_name': req['data']['show_name'],
            'name': req['data']['name']
        }

    def relation_followings(self, vmid):
        """
        获取自己的关注列表，最多40页，最多2000条
        获取用户的关注列表，系统限制访问前5页，分页最大为50，倒序正序各获取250条记录，共500条
        返回元组为(int(vmid), d['mid'], d['mtime'])
        意为这个用户int(vmid)关注了d['mid']，时间为d['mtime']
        :param s:
        :param vmid:
        :return:
        """
        followings = []
        rel = []
        for i in range(1, 41):
            req = self.get(
                url='https://api.bilibili.com/x/relation/followings',
                params={
                    'vmid': vmid,
                    'pn': str(i),
                    'ps': '50',
                    'order': 'desc',
                }
            )
            data = req['data']['list']
            if len(data) == 0:
                break
            for d in data:
                if d['mid'] not in followings:
                    followings.append(d['mid'])
                    rel.append((int(vmid), d['mid'], d['mtime']))
        for i in range(1, 6):
            req = self.get(
                url='https://api.bilibili.com/x/relation/followings',
                params={
                    'vmid': vmid,
                    'pn': str(i),
                    'ps': '50',
                    'order': 'asc',
                }
            )
            data = req['data']['list']
            for d in data:
                if d['mid'] not in followings:
                    followings.append(d['mid'])
                    rel.append((int(vmid), d['mid'], d['mtime']))
        return rel

    def relation_followers(self, vmid):
        """
        系统限制访问前五页
        获取用户的粉丝列表，最多5页x50=250条
        查看自己的粉丝列表，最多1000条，分页50，最多20页
        返回元组为(i['mid'], int(vmid), i['mtime'])
        意思为粉丝（i['mid']）关注（这个用户vmid），i['mtime']
        :param vmid:
        :return:
        """
        followers = []
        rel = []
        for i in range(1, 21):
            req = self.get(
                url='https://api.bilibili.com/x/relation/followers',
                params={
                    'vmid': vmid,
                    'pn': str(i),
                    'ps': '50',
                    'order': 'asc'
                }
            )
            data = req['data']['list']
            if len(data) == 0:
                break
            for i in data:
                if i['mid'] not in followers:
                    followers.append(i['mid'])
                    rel.append((i['mid'], int(vmid), i['mtime']))
        return rel

    def modify(self, fid, act):
        """
        关注/取消关注用户
        (不要短时间大量调用，会封禁一段时间)
        :param fid: 要进行操作的用户
        :param act: 进行的操作1.关注 2.取消关注 3.悄悄关注 4.取消悄悄关注 5.加入黑名单 6.移除黑名单
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/relation/modify',
            data={
                'fid': fid,
                'act': act,
                're_src': '11',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            if act == '1':
                print('关注用户' + fid + '成功')
            elif act == '2':
                print('取消关注用户' + fid + '成功')
            else:
                print(req)
        else:
            print(req)

    def followings_group(self):
        """
        获得当前用户的关注分组
        (i['tagid'], i['name'], i['count'])
        (分组id,分组名称,分组内的用户数)
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/relation/tags'
        )
        data = req['data']
        group = []
        for i in data:
            group.append((i['tagid'], i['name'], i['count']))
        return group

    def move_followings_to_group(self,fids,tagids):
        """
        将指定用户加入指定关注分组
        :param fids:
        :param tagids: 分组id，使用followings_group获取
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/relation/tags/addUsers',
            data={
                'fids': fids,
                'tagids': tagids,
                'csrf': self.csrf
            },
            headers={'Referer': 'https://space.bilibili.com/%s/' % fids}
        )
        print(req)
        if req['code'] == 0:
            print("将用户%s加入分组成功！" % fids)
        else:
            print(req)