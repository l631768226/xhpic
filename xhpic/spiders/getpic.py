import os
import re

import requests
import urllib.parse
import urllib.request
import pymysql
import random
import time


# 下载图片的链接，并保存于folder
def download(folder, url, tableName):
    if not os.path.exists(folder):
        os.makedirs(folder)
    try:
        # 设置请求头，不设置会出现访问个别图片报错400，加入后问题解决
        ua = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        req = requests.get(url, timeout=15, headers=ua)
    except Exception as e:
        print("请求失败：" + e.args)
    if req.status_code == requests.codes.ok:
        name = url.split('/')[-1]
        # name = name.split('?')[0]
        try:
            # 保存图片
            f = open("./" + folder + '/' + name, 'wb')
            f.write(req.content)
            f.close()
        except Exception as e:
            print("下载失败" + e.args)
        # 更新已下载图片的状态
        conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='ly10', database='zhihu',
                               charset='utf8')
        cs = conn.cursor()
        cs.execute('update '+ tableName + ' set tag = 1 where imgurl = %s',  url);
        conn.commit()
        cs.close()
        conn.close()

        return True
    else:
        print("请求错误" + str(req.status_code) + " url = " + url)
        return False


# 初始化
# 加入请求头
def init(url):
    ua = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

    s = requests.Session()
    s.headers.update(ua)
    ret = s.get(url)
    s.headers.update({"authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20"})
    return s


# 设置请求地址和参数
def fetch_answer(s, qid, limit, offset):
    includeStr = 'data/[*/].is_normal,is_sticky,collapsed_by,suggest_edit,comment_count,collapsed_counts,reviewing_comments_count,can_comment,content,editable_content,voteup_count,reshipment_settings,comment_permission,mark_infos,created_time,updated_time,relationship.is_author,voting,is_thanked,is_nothelp,upvoted_followees;data[].author.is_blocking,is_blocked,is_followed,voteup_count,message_thread_token,badge[?(type=best_answerer)].topics'
    includeStr = urllib.parse.quote(includeStr, 'utf-8')
    params = {
        'include': includeStr,
        'limit': limit,
        'offset': offset,
        'platform': 'desktop',
        'sort_by': 'default'
    }
    url = "https://www.zhihu.com/api/v4/questions/" + qid + "/answers"
    print(url)
    return s.get(url, params=params)


def fetch_ans(s, qid, limit, offset):
    try:
        with s.get(
                "https://www.zhihu.com/api/v4/questions/" + qid + "/answers?include=comment_count,content,voteup_count,reshipment_settings,is_author,voting,is_thanked,is_nothelp;data[*].mark_infos[*].url;data[*].author.follower_count,badge[*].topics&limit=5&offset={}&sort_by=default".format(
                    offset), timeout=3) as rep:
            data = rep.json()
            if data:
                # collection.insert_many(data["data"])
                return data
    except Exception as e:
        print(e.args)


# 设置翻页
def fetch_all_answers(url):
    session = init(url)
    q_id = url.split('/')[-1]
    offset = 0
    limit = 5
    answers = []
    is_end = False
    while not is_end:
        # ret=fetch_answer(session,q_id,limit,offset)
        # total = ret.json()['paging']['totals']
        ret = fetch_ans(session, q_id, limit, offset)
        answers += ret['data']
        is_end = ret['paging']['is_end']
        print("Offset: ", offset)
        print("is_end: ", is_end)
        s = ret['paging']
        # print(ret.json()['paging'])
        # print(ret.json()['data']['title'])
        offset += limit

    print("it is over")

    print(len(answers))
    return answers


# 正则匹配所有图片格式（在text中匹配）
def grep_image_urls(text):
    imgs = []
    jpg = re.compile(r'https://[^\s]*?_r\.jpg')
    jpeg = re.compile(r'https://[^\s]*?_r\.jpeg')
    gif = re.compile(r'https://[^\s]*?_r\.gif')
    png = re.compile(r'https://[^\s]*?_r\.png')
    # jpg = re.findall('src=\"(https://.*?)"', text)
    # # jpeg = re.compile(r'https://[^\s]*?_r\.jpeg')
    # # gif = re.compile(r'https://[^\s]*?_r\.gif')
    # # png = re.compile(r'https://[^\s]*?_r\.png')
    imgs += jpg.findall(text)
    imgs += jpeg.findall(text)
    imgs += gif.findall(text)
    imgs += png.findall(text)
    imgs = list(set(imgs))
    return imgs


def update_record(tablename):
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='ly10', database='zhihu', charset='utf8')
    cs = conn.cursor()

    cs.execute('update record set tag = 1 where tablename = %s', tablename);
    conn.commit()
    cs.close()
    conn.close()
    return


def add_mysql_data(Imgs, tableName):
    imgValues = []
    for img in Imgs:
        imgValues.append(img)

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='ly10', database='zhihu', charset='utf8')
    cs = conn.cursor()

    # cs.execute('select id from bodypeak where imgurl in (%s)', imgValues);
    # urls = cs.fetchall()
    #
    # if not urls:
    #     conn.commit()
    #     cs.close()
    #     conn.close()
    #     return
    # else:
    cs.executemany('insert into '+ tableName + ' (imgurl) values (%s)', imgValues)
    conn.commit()
    cs.close()
    conn.close()
    print('PL')
    pass


def select_record(tablename):
    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root',
                           password='ly10', database='zhihu', charset='utf8')
    cs = conn.cursor()
    cs.execute('select tag from record where tablename = %s', tablename)
    # 取出数据为元组
    tag = cs.fetchone()
    conn.commit()
    cs.close()
    conn.close()
    if tag[0] == '1':
        return True
    else:
        return False
        pass

def select_imgUrl(tableName):
    imgUrl = []

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='ly10', database='zhihu', charset='utf8')
    cs = conn.cursor()
    cs.execute('select imgurl from '+ tableName + ' where tag = 0')
    imgs = cs.fetchall()

    if imgs:
        for img in imgs:
            imgUrl.append(img)
        return imgUrl
    else:
        return imgUrl


# url = "https://www.zhihu.com/question/31983868"
# url = "https://www.zhihu.com/question/366062253"
# url = "https://www.zhihu.com/question/46435597"
# url = "https://www.zhihu.com/question/297715922"
url = "https://www.zhihu.com/question/313825759"
folder = '313825759'
tableName = 'girlfriend'
record_tag = select_record(tableName)
if record_tag:
    # 数据已入库，开始下载图片
    print('下载图片')
    pass
else:
    # 数据未爬取完继续爬取

    # 将所有的网页内容提取出来answers+=ret.json()['data']
    answers = fetch_all_answers(url)
    for ans in answers:
        # # 获取点赞数
        # voteCount = ans['voteup_count']
        # # if voteCount > 10:
        imgs = grep_image_urls(ans['content'])
        add_mysql_data(imgs, tableName)
    print('结束url数据爬取')
    update_record(tableName)
    pass
# 获取未下载的图片list
imgUrl = select_imgUrl(tableName)

if imgUrl:
    #下载图片，更新数据库
    for url in imgUrl:
        download(folder, url[0], tableName)
        randomSecond = random.randint(5, 10)
        time.sleep(randomSecond)
    pass
else:
    print('图片数据为空，结束')
    pass

print('all over')
# 将所有的网页内容提取出来answers+=ret.json()['data']
# answers=fetch_all_answers(url)
# folder = '297715922'
# for ans in answers:
#     # 获取点赞数
#     voteCount = ans['voteup_count']
#     # if voteCount > 10:
#     imgs = grep_image_urls(ans['content'])
#     add_mysql_data(imgs)

# for url in imgs:
#     try:
#         download(folder,url)
#     except BaseException:
#         print("出现异常" + url)
# else:
#     print("点赞数不足")
#     pass
