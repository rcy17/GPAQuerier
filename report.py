import requests
from bs4 import BeautifulSoup
import json
import time
import os


def get_transcript(cookies):
    url = 'http://jxgl.cic.tsinghua.edu.cn/jxpg/f/zzzc/v_zzfw_zzdy_dd/bks_dzcjd'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }

    requests.get(url, headers=headers, cookies=cookies, timeout=10)

    data = {'cjdlx': 'yxw_zw'}

    url = 'http://jxgl.cic.tsinghua.edu.cn/jxpg/f/zzzc/v_zzfw_zzdy_dd/bks_dzcjd_lx'

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '12',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'jxgl.cic.tsinghua.edu.cn',
        'Origin': 'http://jxgl.cic.tsinghua.edu.cn',
        'Pragma': 'no-cache',
        'Referer': 'http://jxgl.cic.tsinghua.edu.cn/jxpg/f/zzzc/v_zzfw_zzdy_dd/bks_dzcjd',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }

    response = requests.post(url, headers=headers, cookies=cookies, data=data, timeout=10)

    with open('dzcjd.html', 'w', encoding='utf-8') as fp:
        fp.write(response.text)
    return response.text


def open_file():
    # for debug
    with open('dzcjd.html', 'r', encoding='utf-8') as fp:
        return fp.read()


def get_report(cookies):
    # data = open_file()
    data = get_transcript(cookies)
    soup = BeautifulSoup(data, 'html.parser')

    GP = {'A+': 4, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 'C+': 2.3,
          'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0}
    all_courses = []
    all_points = 0
    credits_count = 0
    nodes = soup.find_all('tr')
    for i in range(1, len(nodes) - 6):
        node = nodes[i]
        course = [x.text.strip() for x in node.contents if x != '\n']
        name, credit, point = course[1], int(course[2]), GP.get(course[3], None)
        if point is None:
            continue
        all_courses.append((name, credit, point))
        all_points += point * credit
        credits_count += credit
    if credits_count:
        GPA = all_points / credits_count
        node = soup.find_all('font', class_="shuxingzhi")
        all_credits = int(node[8].text.strip())
    else:
        GPA = None
        all_credits = None
    return all_courses, all_credits, GPA


def get_transcript2(cookies):
    url = 'http://zhjw.cic.tsinghua.edu.cn/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw'

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Host': 'zhjw.cic.tsinghua.edu.cn',
        'Origin': 'http://jxgl.cic.tsinghua.edu.cn',
        'Pragma': 'no-cache',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
    }

    response = requests.get(url, headers=headers, cookies=cookies, timeout=10)

    with open('zwcjd.html', 'w', encoding='gb2312') as fp:
        fp.write(response.text)
    return response.text


def open_file2():
    # for debug
    with open('zwcjd.html', 'r', encoding='gb2312') as fp:
        return fp.read()


def get_report2(cookies):
    # data = open_file()
    data = get_transcript2(cookies)
    soup = BeautifulSoup(data, 'html.parser')

    GP = {'A+': 4, 'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 'C+': 2.3,
          'C': 2.0, 'C-': 1.7, 'D+': 1.3, 'D': 1.0, 'F': 0.0}
    all_courses = []
    all_points = 0
    credits_count = 0
    nodes = soup.find_all('tr')
    for i in range(7, len(nodes) - 1):
        node = nodes[i]
        course = [x.text.strip() for x in node.contents if x != '\n']
        name, credit, point = course[1], int(course[2]), GP.get(course[3], None)
        if point is None:
            continue
        all_courses.append((name, credit, point))
        all_points += point * credit
        credits_count += credit
    if credits_count:
        GPA = all_points / credits_count
        node = soup.find_all('font', size="2px")
        all_credits = int(node[-5].text.strip())
    else:
        GPA = None
        all_credits = None
    return all_courses, all_credits, GPA


# check directory first
if not os.path.isdir('./query'):
    os.mkdir('./query')
file = open('./query/gpa_log.txt', 'a')


def printGPA(html):
    # just to save, these two lines can be commented
    # with open("gpa.html", "w", encoding='utf-8') as fp:
    #   fp.write(html)

    soup = BeautifulSoup(html, 'html.parser', )

    nodes = soup.find_all('span')
    GPA = None
    for node in nodes:
        if node.get_text() == '已修所有课程学分绩':
            node = node.next_sibling.next_sibling
            GPA = node.get('value')
            print(time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()), GPA, file=file, flush=True)
            break
    return GPA


def get_cookie(cookies=None):
    if cookies is None:
        with open('./cookies/cookies.json', 'r') as fp:
            cookies = json.load(fp)
    return cookies['jxgl'], cookies['zhjw2']


def query(cookies, gpa_save):
    url = 'http://jxgl.cic.tsinghua.edu.cn/jxpg/f/xssq/exwfx/xssqb/cksqs'
    gpa = printGPA(requests.post(url=url, cookies=cookies, timeout=10).content.decode('utf-8'))
    cnt = 0
    while gpa is None:
        if gpa_save is None:
            log = 'GPA轮询系统启动失败, 请尝试再次启动程序!'
            return None, False, log
        if cnt == 5:
            log = 'GPA轮询系统连接失败，请检查网络或重启程序!'
            return gpa_save, False, log
        cnt = cnt + 1
        time.sleep(15)
        gpa = printGPA(requests.post(url=url, cookies=cookies, timeout=10).content.decode('utf-8'))

    if gpa_save is None:
        log = '欢迎使用GPA轮询系统！ 您当前GPA是{}'.format(gpa)
    elif gpa != gpa_save:
        change = '上升' if gpa > gpa_save else '下降'
        log = 'GPA变更: 您的GPA从{}{}为{}'.format(gpa_save, change, gpa)
    else:
        log = None
    return gpa, True, log


def check(cookies, save, cnt=0):
    all_courses, all_credits, gpa = get_report2(cookies)
    if save is None:
        if all_credits is not None:
            log = '获取成绩单成功, 您当前成绩单上显示的总学分为' + str(all_credits)
        else:
            if cnt > 4:
                log = '获取成绩单失败，请尝试再次启动程序!'
                return None, False, log
            else:
                return check(cookies, save, cnt + 1)
    elif all_credits is None:
        if cnt > 4:
            log = '获取成绩单失败，建议重新登陆！'
            all_credits = save
        else:
            return check(cookies, save, cnt + 1)
    elif save != all_credits:
        log = "成绩单更新了，快去看看吧!"
    else:
        log = None
    return all_credits, True, log


def main():
    # for debug
    with open('./cookies/cookies.json', 'r') as fp:
        cookies = json.load(fp)
    print(get_report2(requests.utils.cookiejar_from_dict(cookies['zhjw2'])))
    input('press enter to continue')


if __name__ == '__main__':
    main()
