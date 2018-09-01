import base64
import json
import re
import sys
import time

import requests


class Channel:
    id = None  # 频道id
    owner = None  # 所有者mid
    name = None  # 频道名称
    intro = None  # 频道介绍
    ctime = None  # 频道创建时间
    video_count = None  # 频道中视频的数量
    cover = None  # 频道封面


class Video:
    aid = None              # 视频编号
    videos = None           # 分p数
    tid = None              # 所属分区编号
    copyright = None        # 1.自制 2.搬运
    pic = None              # 封面
    title = None            # 标题
    pubdate = None          # 发布日期
    ctime = None            # 提交日期
    description = None      # 简介
    state = None            # 稿件状态 0.正常 -4.撞车(?)
    forward = None          # 撞车跳转的目标
    attribute = None        # (?)不详
    duration = None         # 持续时间,单位为秒
    owner_mid = None        # 作者mid
    stat_view = None        # 播放次数
    stat_danmaku = None     # 弹幕数
    stat_reply = None       # 回复数
    stat_favorite = None    # 收藏数
    stat_coin = None        # 投币数
    stat_share = None       # 分享数
    stat_now_rank = None    # 当前排名
    stat_his_rank = None    # 历史最高排名
    stat_like = None        # 点赞数
    stat_dislike = None     # 踩的次数
    dynamic = None          # 在动态显示的文本
    cids = None             # 所有分p的cid
    access = None           # 观看所需权限


class VideoPart:
    cid = None          # 分p的cid
    page = None         # 分p序号
    vfrom = None        # 视频来源
    part = None         # 分p标题
    duration = None     # 持续时间
    vid = None          # 不详
    weblink = None      # 不详
    width = None        # 视频宽度
    height = None       # 视频高度
    rotate = None       # 不详


class User:
    archive_count = None            # 稿件数量
    article_count = None            # 文章数量
    follower = None                 # 粉丝数量
    mid = None                      # 用户ID
    name = None                     # 用户名称
    approve = None                  # 不详
    sex = None                      # 性别
    rank = None                     # 权限等级
    face = None                     # 头像
    DisplayRank = None              # 不详
    regtime = None                  # 注册时间
    spacesta = None                 # 账户状态
    birthday = None                 # 生日
    place = None                    # 所在地区
    description = None              # 不详
    article = None                  # 不详
    fans = None                     # 粉丝数
    friend = None                   # 关注数
    attention = None                # 关注数
    sign = None                     # 签名
    current_level = None            # 当前等级
    pendant_pid = None              # 头像边框ID
    pendant_expire = None           # 头像边框过期时间
    nameplate_nid = None            # 勋章ID
    Official_role = None            # 不详
    Official_title = None           # 不详
    Official_desc = None            # 不详
    official_verify_type = None     # 认证类别0.个人认证
    official_verify_desc = None     # 认证描述
    vip_vipType = None              # 大会员类型
    vip_dueRemark = None            # 不详
    vip_accessStatus = None         # 不详
    vip_vipStatus = None            # 大会员状态
    vip_vipStatusWarn = None        # 不详


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
            print(cookies)
            self.csrf = self.session.cookies.get('bili_jct')
            print("Cookies设置成功")

    def post(self, url, data, headers=None, params=None):
        while True:
            try:
                if headers is None:
                    if params is None:
                        req = self.session.post(url, data=data,timeout=99999)
                    else:
                        req = self.session.post(url, data=data, params=params,timeout=99999)
                else:
                    if params is None:
                        req = self.session.post(url, data=data, headers=headers,timeout=99999)
                    else:
                        req = self.session.post(url, data=data, headers=headers, params=params,timeout=99999)
                        # print(req.url)
                if req.status_code == 200:
                    try:
                        return req.json()
                    except Exception as e:
                        print("[POST][提示]JSON化失败:"+str(e)+"\n[提示]内容为:"+req.text)
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
                        # print(req.text)
                        return req.json()
                    except Exception as e:
                        # print("[GET][提示]JSON化失败:" + str(e) + "\n[提示]内容为:" + req.text)
                        return req.content.decode('utf-8')
                else:
                    print("[提示]状态码为" + str(req.status_code) + "！请检查错误\n[提示]" + req.text)
                    # sys.exit(0)
                    time.sleep(1)
            except Exception as e:
                print("[提示]GET出错\n[提示]%s" % str(e))

    def options(self, url, params=None, headers=None):
        while True:
            try:
                if params is None:
                    if headers is None:
                        req = self.session.options(url, timeout=5)
                        print()
                    else:
                        req = self.session.options(url, headers=headers, timeout=5)
                else:
                    if headers is None:
                        req = self.session.options(url, params=params, timeout=5)
                        print(req.url)
                    else:
                        req = self.session.options(url, params=params, headers=headers, timeout=5)
                if req.status_code == 200:
                    return True
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
                    return True
                else:
                    print("[提示]状态码为" + str(req.status_code) + "！请检查错误\n[提示]" + req.text)
                    sys.exit(0)
            except Exception as e:
                print("[提示]PUT出错\n[提示]%s" % str(e))

    def upload_chunk(self, url, data, params, auth):
        while True:
            try:
                req = self.session.options(url=url)
                if req.status_code != 200:
                    raise RuntimeError('OPTIONS返回码不是200')
                req1=self.session.put(url=url, data=data, params=params, headers={'X-Upos-Auth': auth})
                if req1.status_code != 200:
                    raise RuntimeError('OPTIONS返回码不是200')
                return True
            except:
                print("[提示]上传块失败,重试...")

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
        l = req['data']['items']
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

    def get_tag_info(self, tag_id):
        """
        通过tag_id获得tag信息
        :param tag_id:
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/tag/info',
            params={'tag_id': tag_id}
        )
        print(req)

    def get_similar_tags(self, tag_id):
        """
        获得tag的相关tags
        :param tag_id:
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/tag/change/similar',
            params={'tag_id': tag_id}
        )
        print(req)
        if req['code'] == 0:
            return req['data']

    def get_tag_video(self, tag_id, page=1, pagesplit=20):
        """
        获得指定tag下的视频,按时间顺序排列
        :param tag_id:
        :param page:
        :param pagesplit: 分页大小,默认20,最大40,但返回数据不一定是40,可能是30~40条数据,不定
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/tag/detail',
            params={
                'jsonp': 'jsonp',
                'pn': page,
                'ps': pagesplit,
                'tag_id': tag_id,
            }

        )
        # print(req)
        if req['code'] == 0:
            return req['data']['news']['archives']

    def get_user_following_bangumi(self, mid, page=1):
        """
        获得用户订阅的番剧
        :param mid: 用户mid
        :param page: 查询页数
        :return:
        """
        req = self.get(
            url='https://space.bilibili.com/ajax/Bangumi/getList',
            params={
                'mid': mid,
                'page': page
            }
        )
        blist = []
        if req['status']:
            for b in req['data']['result']:
                blist.append(b['season_id'])
            return blist

    def get_user_following_tags(self, mid):
        """
        获得用户关注的tag
        :param mid:
        :return:
        """
        req = self.get(
            url='https://space.bilibili.com/ajax/tags/getSubList',
            params={'mid': mid}
        )
        if req['status']:
            return req['data']['tags']

    def get_user_channel_list(self, mid):
        """
        获得用户创建的频道列表
        :param mid: 用户mid
        :return: Channel对象的list
        """
        req = self.get(
            url='https://api.bilibili.com/x/space/channel/list',
            params={
                'mid': mid,
                'guest': 'false',  # 谜,false
                'jsonp': 'jsonp'
            }
        )
        clist = []
        if req['code'] == 0:
            for c in req['data']['list']:
                channel = Channel()
                channel.id = c['cid']
                channel.owner = c['mid']
                channel.name = c['name']
                channel.intro = c['intro']
                channel.ctime = c['mtime']
                channel.video_count = c['count']
                channel.cover = c['cover']
                clist.append(channel)
            return clist

    def channel_add(self, ch_name, intro='',):
        """
        创建新的频道
        code=0 创建成功
        code=53001 频道名字数超过限制啦
        :param ch_name: 频道名称
        :param intro: 频道介绍
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/space/channel/add',
            data={
                'name': ch_name,
                'intro': intro,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("[提示]频道<%s>创建成功,频道ID为%s" % (ch_name, req['data']['cid']))
            return req['data']['cid']
        else:
            print(req)

    def channel_edit(self, ch_id, name, intro=''):
        """
        修改频道信息
        code=0 修改成功
        code=53001 频道名字数超过限制啦
        code=-400 请求错误
        :param ch_id:频道id
        :param name: 频道新名称
        :param intro: 频道新简介
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/space/channel/edit',
            data={
                'cid': ch_id,
                'name': name,
                'intro': intro,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        print(req)
        if req['code'] == 0:
            print("[提示]频道ID:<{}>名称已修改为<{}>,简介为:<{}>".format(ch_id, name, intro))

    def channel_del(self, ch_id):
        """
        删除指定频道
        :param ch_id:频道id
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/space/channel/del',
            data={
                'cid': ch_id,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("[提示]频道ID:<{}>已成功删除!".format(ch_id))

    def channel_video(self, mid, cid, page=1, pagesplit=30, order=0):
        """
        获得频道内的视频
        :param mid:
        :param cid:
        :param page:
        :param pagesplit:分页大小,默认30,最大100
        :param order:0.默认排序 1.倒序排序
        :return:视频aid列表
        """
        req = self.get(
            url='https://api.bilibili.com/x/space/channel/video',
            params={
                'mid': mid,
                'cid': cid,
                'pn': page,
                'ps': pagesplit,
                'order': order,
                'jsonp': 'jsonp'
            }
        )
        print(req)
        vlist = []
        if req['code'] == 0:
            for v in req['data']['list']['archives']:
                vlist.append(v['aid'])
            return vlist

    def get_video_info(self, aid):
        """
        获得视频详细信息
        code=0 正常
        code=62002 稿件不可见(稿件被删除 state为-100)
        code=-404  啥都木有(稿件下架)
        :param aid: 视频aid
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/web-interface/view',
            params={'aid': aid}
        )
        print(req)
        if req['code'] == 0:
            v = Video()
            v.aid = req['data']['aid']
            v.videos = req['data']['videos']
            v.tid = req['data']['tid']
            v.copyright = req['data']['copyright']
            v.pic = req['data']['pic']
            v.title = req['data']['title']
            v.pubdate = req['data']['pubdate']
            v.ctime = req['data']['ctime']
            v.description = req['data']['desc']
            v.state = req['data']['state']
            if req['data']['state'] == -4:
                v.forward = req['data']['forward']
            v.attribute = req['data']['attribute']
            v.duration = req['data']['duration']
            v.owner_mid = req['data']['owner']['mid']
            v.stat_view = req['data']['stat']['view']
            if req['data']['stat']['view'] == -1:
                v.access = req['data']['access']
            v.stat_danmaku = req['data']['stat']['danmaku']
            v.stat_reply = req['data']['stat']['reply']
            v.stat_favorite = req['data']['stat']['favorite']
            v.stat_coin = req['data']['stat']['coin']
            v.stat_share = req['data']['stat']['share']
            v.stat_now_rank = req['data']['stat']['now_rank']
            v.stat_his_rank = req['data']['stat']['his_rank']
            v.stat_like = req['data']['stat']['like']
            v.stat_dislike = req['data']['stat']['dislike']
            v.dynamic = req['data']['aid']
            cids = []
            part = []
            for p in req['data']['pages']:
                cids.append(p['cid'])
                vp = VideoPart()
                vp.cid = p['cid']
                vp.page = p['page']
                vp.vfrom = p['from']
                vp.part = p['part']
                vp.duration = p['duration']
                vp.vid = p['vid']
                vp.weblink = p['weblink']
                vp.width = p['dimension']['width']
                vp.height = p['dimension']['height']
                vp.rotate = p['dimension']['rotate']
                part.append(vp)
            v.cids = str(cids)[1:-1].replace(' ', '')
            return v, part

    def get_user_card(self, mid,):
        """
        获得用户详细的资料卡
        :param mid: 用户
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/web-interface/card',
            params={
                'jsonp': 'jsonp',
                'mid': mid,
                # 'loginid': 'loginid' 非必要参数
            }
        )
        print(req)

    def get_video_tags(self, aid):
        """
        获得视频的tag
        :param aid: 视频aid
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/tag/archive/tags',
            params={
                'aid': aid,
                'jsonp': 'jsonp'
            }
        )
        print(req)

    def get_my_attentions(self):
        """
        获得当前用户的关注列表
        :return: 关注用户mid列表
        """
        req = self.get(
            url='https://api.bilibili.com/x/web-interface/attentions',
            params={'jsonp': 'jsonp'}
        )
        if req['code'] == 0:
            return req['data']

    def get_attention_list(self):
        """
        获得当前用户关注的mid列表，带不带params不影响结果
        :return:
        """
        req = self.get(
            url='https://api.vc.bilibili.com/feed/v1/feed/get_attention_list'
            # params={'uid': '3296491'}
        )
        if req['code'] == 0 and req['message'] == 'success':
            return req['data']['list']

    def is_favoured(self, aid):
        """
        判断当前登录的用户是否收藏指定视频
        返回示例：{'code': 0, 'message': '0', 'ttl': 1, 'data': {'count': 1, 'favoured': False}}
        count作用不详
        :param aid: 视频aid
        :return: 已收藏返回True 未收藏返回False
        """
        req = self.get(
            url='https://api.bilibili.com/x/v2/fav/video/favoured',
            params={
                'aid': aid,
                'jsonp': 'jsonp'
            }
        )
        print(req)
        if req['code'] == 0:
            return req['data']['favoured']

    def archive_coins(self, aid):
        """
        (谜)关于硬币的api
        :param aid:视频aid
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/web-interface/archive/coins',
            params={
                'jsonp': 'jsonp',
                'aid': aid
            }
        )
        print(req)
        
    def elec_show(self, aid, mid):
        """
        获得指定稿件的充电信息
        :param aid: 稿件aid
        :param mid: 作者mid
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/web-interface/elec/show',
            params={
                'jsonp': 'jsonp',
                'aid': aid,
                'mid': mid
            }
        )
        if req['code'] == 0:
            av_count = req['data']['av_count']  # 本视频充电人数
            count = req['data']['count']  # 本月充电人数
            total_count = req['data']['total_count']  # 历史充电总人数
            av_list = req['data']['av_list']  # 本视频充电排行榜
            list = req['data']['list']  # 本月充电排行榜
            return av_count, count, total_count, av_list, list

    def video_related(self, aid):
        """
        获得指定视频的相关视频(看过该视频的还喜欢)
        :param aid:视频aid
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/web-interface/archive/related',
            params={
                'aid': aid,
                'jsonp': 'jsonp'
            }
        )
        print(req)

    def video_reply(self, aid, page=1, type=1, sort=0):
        """
        获得视频的评论
        code=12002 禁止评论(type>1)
        code=12009 评论主体的type不合法(type=0)
        一些特殊的视频也会返回code12002
        :param aid:视频aid
        :param page:页数
        :param type:
        :param sort:
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/v2/reply',
            params={
                'jsonp': 'jsonp',
                'pn': page,
                'type': type,
                'oid': aid,
                'sort': sort  # 0.普通排序 2.按热度排序
            }
        )
        print(req)

    def video_tag_log(self, aid, page=1, pagesplit=20):
        """
        获得视频标签修改记录
        :param aid:
        :param page:
        :param pagesplit:
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/tag/archive/log',
            params={
                'aid': aid,
                'pn': page,
                'ps': pagesplit,
                'jsonp': 'jsonp'
            }
        )
        print(req)

    def video_tag_add(self, aid, tag_name):
        """
        为视频添加tag
        code=16009 这个频道已经添加过啦~
        code=-101 账号未登录
        :param aid: 视频aid
        :param tag_name: 要添加的tag名称
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/tag/archive/add',
            data={
                'aid': aid,
                'tag_name': tag_name,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("[提示]TAG:<{}>添加成功!".format(tag_name))
        elif req['code'] == 16009:
            print("[提示]TAG:<{}>已经添加过了!".format(tag_name))
        else:
            print(req)

    def video_tag_like(self, aid, tag_id):
        """
        视频tag点赞,再点一次取消赞
        :param aid:
        :param tag_id:
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/tag/archive/like2',
            data={
                'tag_id': tag_id,
                'aid': aid,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("[提示]视频aid:<{}>的TAG:<{}>点赞成功!".format(aid, tag_id))
        else:
            print(req)

    def video_tag_hate(self, aid, tag_id):
        """
        视频tag踩,再点一次取消踩
        :param aid:
        :param tag_id:
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/tag/archive/hate2',
            data={
                'tag_id': tag_id,
                'aid': aid,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("[提示]视频aid:<{}>的TAG:<{}>踩成功!".format(aid, tag_id))
        else:
            print(req)

    def video_tag_del(self, aid, tag_id):
        """
        删除视频的tag
        code=16011 删除太多频道啦,休息休息~
        code=16049 资源绑定tag关系不存在~
        code=16071 只有UP主可以删除哦
        :param aid:
        :param tag_id:
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/tag/archive/del',
            data={
                'aid': aid,
                'tag_id': tag_id,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        print(req)

    def video_tag_report(self, aid, tag_id, reason):
        """
        举报视频tag
        :param aid:
        :param tag_id:
        :param reason:必须为四个值之一：内容不相关|敏感信息|恶意攻击|剧透内容
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/tag/archive/report',
            data={
                'aid': aid,
                'tag_id': tag_id,
                'reason': reason,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("[提示]举报视频aid:<{}>中的TAG:<{}>成功,举报理由为:<{}>".format(aid, tag_id, reason))
        else:
            print(req)

    def tag_subscribe_add(self, tag_id):
        """
        订阅TAG
        code=16030 已经订阅过这个频道啦~
        :param tag_id:
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/tag/subscribe/add',
            data={
                'tag_id': tag_id,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("[提示]订阅TAG:<{}>成功!".format(tag_id))
        else:
            print(req)

    def tag_subscribe_cancel(self, tag_id):
        """
        取消订阅TAG
        code=16035 未订阅过此频道~
        :param tag_id:
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/tag/subscribe/cancel',
            data={
                'tag_id': tag_id,
                'jsonp': 'jsonp',
                'csrf': self.csrf,
            }

        )
        if req['code'] == 0:
            print("[提示]取消订阅TAG:<{}>成功".format(tag_id))
        elif req['code'] == 16035:
            print("[提示]未订阅过TAG:<{}>".format(tag_id))
        else:
            print(req)

    def tag_cancelSub(self, tag_id):
        """
        取消订阅TAG(通过个人主页-订阅-标签)
        :param tag_id:
        :return:
        """
        req = self.post(
            url='https://space.bilibili.com/ajax/tags/cancelSub',
            data={
                'tag_id': tag_id,
                'csrf': self.csrf
            },
            headers={'Referer': 'https://space.bilibili.com/'}
        )
        print(req)
        if req['status']:
            print("[提示]取消订阅TAG:<{}>成功".format(tag_id))
        elif not req['status']:
            print("[提示]取消订阅TAG:<{}>失败".format(tag_id))

    def space_pravacy(self, option, value):
        """
        个人主页-设置-隐私设置,设置指定项对其他用户是否可见
        1为可见,0为隐藏,可选项:
        我的收藏夹           fav_video
        订阅番剧             bangumi
        订阅标签             tags
        最近投币的视频        coins_video
        个人资料             user_info
        最近玩过的游戏         played_game
        :param value: 隐藏or显示
        :param option: 需要更改的项目
        :return:
        """
        req = self.post(
            url='https://space.bilibili.com/ajax/settings/setPrivacy',
            data={
                option: value,
                'csrf': self.csrf
            },
            headers={'Referer': 'https://space.bilibili.com/'}
        )
        print(req)
        if req['status']:
            print("[提示]操作成功!")
        elif not req['status']:
            print("[提示]操作失败!")

    def space_user_tags(self, mids):
        """
        获取一个或多个用户的个人标签
        :param mids:用户mid的list
        :return:
        """
        req = self.get(
            url='https://space.bilibili.com/ajax/member/getTags',
            params={'mids': str(mids)[1:-1].replace(" ", '')}
        )
        print(req)

    def space_user_tags_set(self, tags):
        """
        编辑个人标签
        需要使用space_user_tags获取自己的个人标签,然后加上新增的标签,用逗号隔开,一次性全部提交
        :param tags: 例:标签1,标签2,标签3
        :return:
        """
        req = self.post(
            url='https://space.bilibili.com/ajax/member/setTags',
            data={
                'tags': tags,
                'csrf': self.csrf
            },
            headers={'Referer': 'https://space.bilibili.com/'}
        )
        print(req)
        if req['status']:
            print("[提示]个人标签设置成功!")
        elif not req['status']:
            print("[提示]个人标签设置失败!")

    def space_index_order(self, index_order):
        """
        设置个人主页布局
        1.我的稿件
        2.我的收藏夹
        3.订阅番剧
        4.订阅标签
        5.最近投币的视频
        6.不详
        7.我的频道
        8.我的专栏
        9.我的相簿
        21.公告
        22.直播间
        23.个人资料
        24.官方活动
        25.最近玩过的游戏
        6总是在最后
        :param index_order:
        :return:
        """
        req = self.post(
            url='https://space.bilibili.com/ajax/settings/setIndexOrder',
            data={
                'index_order': str(index_order)[1:-1].replace(" ", ''),
                'csrf': self.csrf
            },
            headers={'Referer': 'https://space.bilibili.com/'}
        )
        if req['status']:
            print("[提示]个人空间布局设置成功!")
        elif not req['status']:
            print("[提示]个人空间布局设置失败!")

    def update_my_sign(self, newsign):
        """
        修改我的签名(有时不太好用)
        :param newsign:
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/member/web/sign/update',
            data={
                'user_sign': newsign,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        if req['code'] == 0:
            print("[提示]当前签名已修改为:<{}>".format(newsign))
        else:
            print(req)
            print(self.csrf)
            print("[提示]修改签名失败!")

    def site_user_info(self):
        """
        获得本账号的绑定情况信息
        :return:
        """
        req = self.get(
            url='https://passport.bilibili.com/web/site/user/info'
        )
        print(req)

    def realname_status(self):
        """
        查询本账号是否通过了实名认证
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/member/realname/status',

        )
        if req['code'] == 0:
            if req['data']['status'] == 1:
                return True
            else:
                return False

    def watchlater_video(self):
        """
        获得"稍后观看"中的视频
        :return: 视频aid列表
        """
        req = self.get(
            url='https://api.bilibili.com/x/v2/history/toview/web'
        )
        vlist = []
        if req['code'] == 0:
            for v in req['data']['list']:
                vlist.append(v['aid'])
            return vlist

    def get_my_blacklist(self, page=1, pagesplit=20):
        """
        获得我的黑名单列表
        :param page:
        :param pagesplit:
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/relation/blacks',
            params={
                're_version': 0,
                'pn': page,
                'ps': pagesplit,
                'jsonp': 'jsonp'
            }
        )
        return req['data']['list']

    def get_my_coin_log(self):
        """
        获得此账号硬币最近一周的变化情况
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/member/web/coin/log',
            params={'jsonp': 'jsonp'}
        )
        if req['code'] == 0:
            return req['data']['list']

    def get_my_login_log(self):
        """
        获得此账号最近一周的登录情况
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/member/web/login/log',
            params={'jsonp': 'jsonp'}
        )
        if req['code'] == 0:
            return req['data']['list']

    def get_my_moral_log(self):
        """
        获得此账号最近一周的节操值记录
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/member/web/moral/log',
            params={'jsonp': 'jsonp'}
        )
        print(req)

    def get_my_exp_log(self):
        """
        获得此账号最近一周的经验变化
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/member/web/exp/log',
            params={'jsonp': 'jsonp'}
        )
        if req['code'] == 0:
            return req['data']['list']

    def get_my_reply_list(self, stime, etime, order, sort, page=1, pagesplit=10):
        """
        查询此账号的历史发言
        :param stime: 查询起始时间戳(秒级)
        :param etime: 查询终止时间戳(秒级)
        :param order: 发布时间(ctime)获得的赞(like)
        :param sort: 倒序(desc) 正序(asc),以赞数查询时,只允许使用倒序查询
        :param page: 页数
        :param pagesplit:默认值10,根据查询范围最大值不定(例如查询最近三年的记录,最大值为715,更大的的查询范围,最大值更低,否则返回-500服务器错误)
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/member/web/reply/list',
            params={
                # 'mid': 2062761,
                'stime': stime,
                'etime': etime,
                'order': order,
                'sort': sort,
                'pn': page,
                'ps': pagesplit,
                'jsonp': 'jsonp'
            }
        )
        if req['code'] == 0:
            return req['data']['records']
        else:
            print(req)

    def get_my_basic_info(self):
        """
        获得此账号的基本信息(个人中心-我的信息)
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/member/web/account',

        )
        if req['code'] == 0:
            return req['data']

    def update_my_basic_info(self, uname, usersign, sex, birthday):
        """
        更新此账号的基本资料
        code=40004 昵称不可包含除-和_以外的特殊字符
        code=40005 昵称太长或包含特殊字符
        code=40014 该昵称已存在
        code=40021 签名不能包含表情图片
        code=40022 签名最多支持70个字
        :param uname: 用户名
        :param usersign: 签名
        :param sex: 性别,男,女,保密
        :param birthday:生日,例:2014-12-01
        :return:
        """
        req = self.post(
            url='https://api.bilibili.com/x/member/web/update',
            data={
                'uname': uname,
                'usersign': usersign,
                'sex': sex,
                'birthday': birthday,
                'csrf': self.csrf
            }
        )
        print(req)

    def report_add(self, mid, reason):
        """
        个人信息举报
        :param mid:
        :param reason: 1.头像违规 2.昵称违规 3.签名违规 选择多项，用逗号隔开1,2,3
        :return:
        """
        req = self.post(
            url='https://space.bilibili.com/ajax/report/add',
            data={
                'mid': mid,
                'reason': reason,
                'csrf': self.csrf
            },
            headers={
                'Referer': 'https://space.bilibili.com/%s/' % mid
            }

        )
        print(req)

    def watchlater_video_add(self, aid):
        req = self.post(
            url='https://api.bilibili.com/x/v2/history/toview/add',
            data={
                'aid': aid,
                'jsonp': 'jsonp',
                'csrf': self.csrf
            }
        )
        print(req)

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

    def submitArticle(self, infodict):
        """
        提交稿件
        code=10009 同一个视频，不能短时间同时提交到不同稿件，请先查看稿件列表是否第一次提交的稿件已经存在。如需在另一个稿件包含该视频，请分开上传提交。
        :param infodict:稿件信息的dict
        :return:
        """
        req = self.post(
            url='https://member.bilibili.com/x/vu/web/add',
            params={
                'csrf': self.csrf
            },
            data=infodict,
            headers={
                'Content-Type': 'application/json;charset=UTF-8'
            }
        )
        print(req)
        if req['code'] == 0:
            print("[提示]稿件提交成功,稿件ID为<{}>".format(req['data']['aid']))
        else:
            print("[提示]提交稿件发生错误!返回数据为:"+req)

    def get_bangumi_info(self, md):
        """
        获得番剧信息
        :param md: 番剧编号
        :return:
        """
        req = self.get(
            url='https://www.bilibili.com/bangumi/media/md{}/'.format(md),
        )
        jsdata = re.findall('window.__INITIAL_STATE__=(.*?);\(function\(\)', req)
        return jsdata[0]

    def s_get_info(self, aid):
        """
        只获得稿件的播放,回复,弹幕数等统计信息
        :param aid:
        :return:
        """
        req = self.get(
            url='https://api.bilibili.com/x/web-interface/view',
            params={'aid': aid}
        )
        return req['data']['stat']

    def get_my_archives(self, page=1, pagesplit=10, type=0):
        """
        获得我的投稿列表
        :param page:
        :param pagesplit: 分页大小,默认10,最大20
        :param type: 查询类型0.所有 1.审核中 2.已通过 3.未通过
        :return:
        """
        if type == 1:
            status = 'is_pubing'
        elif type == 2:
            status = 'pubed'
        elif type == 3:
            status = 'not_pubed'
        else:
            status = 'is_pubing,pubed,not_pubed'
        req = self.get(
            url='https://member.bilibili.com/x/web/archives',
            params={
                'status': status,
                'pn': page,
                'ps': pagesplit
            }
        )
        return req['data']['arc_audits']

    def getartical(self,aid):
        """
        获得稿件数据（编辑稿件）
        :param aid: av号
        :param session: session
        :return:
        """
        req = self.get(
            url='https://member.bilibili.com/x/web/archive/view',
            params={'aid': aid}
        )
        return req

    def updateArticle(self, datadict):
        """
        提交对稿件的修改
        :param datadict:
        :return:
        """
        data = str(datadict).replace("'", '"').replace('&amp;', '&').replace("&#39;", "'").encode('utf-8')
        req = self.post(
            url='https://member.bilibili.com/x/vu/web/edit',
            data=data,
            headers={'Content-Type': 'application/json;charset=UTF-8'},
            params={'csrf': self.csrf}
        )
        print(req)

    def getmychhose(self, mid):
        """
        查询我的直播间最近使用过的分类
        :param mid:直播间id
        :return:
        """
        req = self.get(
            url='https://api.live.bilibili.com/room/v1/Area/getMyChooseArea',
            params={'roomid':mid}
        )
        print(req)
        if req['code'] == 0:
            return req['data']