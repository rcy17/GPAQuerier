from requests import get, post
from bs4 import BeautifulSoup as bs
from json import load

cookies = {}
data = {}
refer = {}

NOTHING = 0
RESPONSE = 1
JSON = 2


def initialize():
    global cookies
    global data
    global refer
    with open('cookies.json', 'r') as fp:
        cookies = load(fp)
    with open('data.json', 'r') as fp:
        data['aoData'] = fp.read()
    with open('result.json', 'r', encoding='utf-8') as fp:
        refer = load(fp)


def query():
    global refer
    result = NOTHING
    url = 'http://jxgl.cic.tsinghua.edu.cn/jxpg/f/zzy/zzyxs/lqqk'
    node = bs(get(url, cookies=cookies).text, 'html.parser').find('title')
    if node.text != '错误页面':
        result |= RESPONSE
    url = 'http://jxgl.cic.tsinghua.edu.cn/jxpg/b/zzy/zzyxs/sqjl'
    re = post(url=url, cookies=cookies, data=data).json()
    if re['result'] == 'success':
        if re != refer:
            result |= JSON
            refer = re
    else:
        print('query json failed!')
    return result


if __name__ == '__main__':
    initialize()
    print(query())

