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
                        print(req.text)
                        return req.json()
                    except Exception as e:
                        print("[提示]JSON化失败:" + str(e) + "\n[提示]内容为:" + req.text)
                        return req.content.decode('utf-8')
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
        :param tagids: 分组id，使用followings_group获取，允许传入多个值，
        用逗号分开。例：-10,74801
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

    def followings_group_create(self, tag):
        """
        创建新的关注分组
        code=0      创建成功
        code=22106  该分组已经存在
        :param tag: 分组的名字
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/relation/tag/create',
            data={
                'tag': tag,
                'csrf': self.csrf
            }
        )
        print(req)
        if req['code'] == 0:
            print("分组创建成功！分组id为：%s" % req['data']['tagid'])
        else:
            print(req)

    def followings_group_rename(self, tagid, name):
        """
        重命名关注分组
        code=0      修改成功
        code=22104  该分组不存在
        code=-101   账号未登录
        code=-400   请求错误
        :param tagid:
        :param name:
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/relation/tag/update',
            data={
                'tagid': tagid,
                'name': name,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        print(req)
        if req['code'] == 0:
            print("分组id:%s已经更名为:%s" % (tagid, name))
        else:
            print(req)

    def followings_group_delete(self, tagid):
        """
        删除指定的关注分组
        code=0      操作成功（删除不存在的分组也返回code0）
        code=-101   账号未登录
        code=-400   请求错误
        :param tagid: 关注分组id
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/relation/tag/del',
            data={
                'tagid': tagid,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] ==0:
            print("操作成功")
        else:
            print(req)

    def followings_group_copy_users(self, fids, tagids):
        """
        将多个用户复制到指定关注分组
        code=0          操作成功
        code=22104      该分组不存在
        code=22105      请先公开关注后再添加分组(关注后才能复制到分组)
        code=-101       账号未登录
        code=-400   请求错误
        :param fids:    用户列表（list类型），示例[1234,5678,9012]
        :param tagids:  分组id
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/relation/tags/copyUsers',
            data={
                'fids': str(fids)[1:-1].replace(' ', ''),
                'tagids': tagids,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("操作成功")
        else:
            print(req)

    def followings_group_move_users(self, beforeTagids, afterTagids, fids):
        """
        将多个用户移动到指定的关注分组
        code=0          操作成功
        code=22104      该分组不存在
        code=22105      请先公开关注后再添加分组(关注后才能复制到分组)
        code=-101       账号未登录
        code=-400       请求错误
        :param beforeTagids:    移动前所在分组id
        :param afterTagids:     目标分组id
        :param fids:            需要操作的用户id列表（list类型），示例[1234,5678,9012]
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/relation/tags/moveUsers',
            data={
                'beforeTagids': beforeTagids,
                'afterTagids': afterTagids,
                'fids': str(fids)[1:-1].replace(' ', ''),
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("操作成功")
        else:
            print(req)

    def getSubmitVideos(self, mid, pagesize=100, tid=0, page=1, keyword='', order='pubdate'):
        """
        获得用户投稿的视频列表
        :param mid:         用户mid
        :param pagesize:    分页大小,默认100,最大100
        :param tid:         按分区查询,0.查询所有,tid对照见tid.txt
        :param page:        查询页数,默认查询第一页
        :param keyword:     按关键字查找
        :param order:       查询排序方式,默认pubdate(最新发布)/click(点击数)/stow(最多收藏)
        :return:
        """
        req = self.get(
            url='https://space.bilibili.com/ajax/member/getSubmitVideos',
            params={
                'mid': mid,
                'pagesize': pagesize,
                'tid': tid,
                'page': page,
                'keyword': keyword,
                'order': order
            }
        )
        return req['data']['vlist']

    def get_album_list(self, mid, page_num=0, page_size=99999, biz='all'):
        """
        获得用户相簿列表
        :param mid: 用户mid
        :param page_num: 页数,从0开始,默认为0
        :param page_size: 分页大小,目前没有限制(WHAT?)
        :param biz: 分类查找,默认all,draw(画友),daily(日常),photo(摄影)
        :return:
        """
        req = self.get(
            url='https://api.vc.bilibili.com/link_draw/v1/doc/doc_list',
            params={
                'uid': mid,
                'page_num': page_num,
                'page_size': page_size,
                'biz': biz
            }

        )
        print(req)
        l=req['data']['items']
        print(l)
        print(len(l))
        for i in l:
            print(i)

    def get_user_article_list(self, mid, page=1, pagesplit=30, sort='publish_time'):
        """
        获得用户专栏文章列表
        :param mid: 用户mid
        :param page: 页数,默认第1页
        :param pagesplit: 分页大小,默认12,最大30
        :param sort: 排序方式,默认publish_time(发布时间)/view(最多观看)/fav(最多收藏)
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/space/article',
            params={
                'mid': mid,
                'pn': page,
                'ps': pagesplit,
                'sort': sort,
                'jsonp': 'jsonp'
            }
        )
        return req['data']['articles']

    def get_user_audio_list(self, mid, page=1, pagesplit=30, order=1):
        """
        获得用户音频作品列表
        :param mid:         用户mid
        :param page:        页数,默认为1
        :param pagesplit:   分页大小,默认30,最大为(?)
        :param order:       排序方式 1.最新发布 2.最多播放 3.最多收藏
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/audio/music-service-c/web/song/upper',
            params={
                'uid': mid,
                'pn': page,
                'ps': pagesplit,
                'order': order,
                'jsonp': 'jsonp'
            }
        )
        return req['data']['data']

    def get_history_danmaku_index(self, cid, month):
        """
        获得指定月份可用历史弹幕的列表(需要登录)
        返回示例：{"code":0,"message":"0","ttl":1,"data":["2018-08-05","2018-08-09","2018-08-10"]}
        :param cid: 视频cid号
        :param month: 以年-月组合的字符串，用于查询当月可用的历史弹幕,例:2018-08
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/v2/dm/history/index',
            params={
                'type': 1,  # 谜
                'oid': cid,
                'month': month
            }
        )
        if req['code'] == 0:
            return req['data']
        else:
            print(req)

        dlist=req

    def get_history_danmaku(self, cid, data):
        """
        获得指定时间的历史弹幕
        :param cid:     视频cid
        :param data:    指定日期,通过get_history_danmaku_index获取
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/v2/dm/history',
            params={
                'type': 1,  # 谜
                'oid': cid,
                'date': data
            }
        )
        return req

    def get_danmaku(self, cid):
        """
        通过cid获取弹幕
        :param cid: 视频cid
        :return:
        """
        req = self.get(
            url='https://comment.bilibili.com/%s.xml' % cid,
            params={'platform': 'bilihelper'}
        )
        return req
    def old_view(self, avnum):
        """
        旧接口,获得稿件信息
        :param avnum:
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/view',
            params={
                'type': 'jsonp',
                'appkey': '8e9fc618fbd41e28',
                'id': avnum
            }
        )
        print(req)

    def old_pagelist(self, aid):
        """
        旧接口,获得稿件的分p信息,cid信息
        :param aid: 稿件aid
        :return:
        """
        req = self.get(
            url='https://www.bilibili.com/widget/getPageList',
            params={'aid': aid}
        )
        print(req)