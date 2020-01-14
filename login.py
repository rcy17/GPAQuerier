import requests  # to visit url
import json
from bs4 import BeautifulSoup
import os
from getpass import getpass


'''
warning: this module was finished when the author was just a newbie,
         so a stupid style is just in expectation
'''

re = []

# check directory first
if not os.path.isdir('./cache'):
    os.mkdir('./cache')
if not os.path.isdir('./cookies'):
    os.mkdir('./cookies')


def login(first=True):
    data = {
        "redict": "NO",
        "userName": None,
        "password": None,
        "x": "40",  # these two number is the clicked position of the login button in
        "y": "15"  # info login page, I have no idea why the developers send these
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '57',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'info.tsinghua.edu.cn',
        'Origin': 'http://info.tsinghua.edu.cn',
        'Pragma': 'no-cache',
        'Referer': 'http://info.tsinghua.edu.cn/index.jsp',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }
    if first:
        # login first
        data['userName'] = input("please input your username:")
        data['password'] = getpass("please input your password:")
        with open('./cache/account', 'w', encoding='utf-8') as fp:
            json.dump(data, fp)
    else:
        try:
            # load account data
            with open('./cache/account', 'r', encoding='utf-8') as fp:
                data = json.load(fp)
        except FileNotFoundError:
            return login(True)
    response_info = requests.post("https://info.tsinghua.edu.cn/Login", data=data, headers=headers,
                                  timeout=10)  # here we get info'home page
    response_login = response_info.history[0]  # find login's response to get cookies
    if 'Error' in response_login.headers['location']:
        print('username or password wrong, please try again!')
        return login(True)
    re.append(response_info)
    # print('Input right!')
    return response_login.cookies


def getCookies(cookies):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }

    all_cookies = {'login': requests.utils.dict_from_cookiejar(cookies)}

    # get from some url in order (to finish the complete login proccess?)

    url_get_ticket = "http://info.tsinghua.edu.cn/minichan/roamaction.jsp"

    response_finance = requests.get(url_get_ticket,
                                    cookies=cookies,
                                    headers=headers,
                                    params={'mode': 'local', 'id': '2002'},
                                    timeout=10
                                    )
    re.append(response_finance)
    all_cookies['finance'] = requests.utils.dict_from_cookiejar(response_finance.cookies)

    response_kyxxxt = requests.get(url_get_ticket,
                                   cookies=cookies,
                                   headers=headers,
                                   params={'mode': 'local', 'id': '2003'},
                                   timeout=10
                                   )
    re.append(response_kyxxxt)
    all_cookies['kyxxxt'] = requests.utils.dict_from_cookiejar(response_kyxxxt.history[1].cookies)

    response_jxgl = requests.get(url_get_ticket,
                                 cookies=cookies,
                                 headers=headers,
                                 params={'mode': 'local', 'id': '2005'},
                                 timeout=10
                                 )
    re.append(response_jxgl)
    # print(response_jxgl.text)
    all_cookies['jxgl'] = requests.utils.dict_from_cookiejar(response_jxgl.history[1].cookies)

    response_meta = requests.get(url_get_ticket,
                                 cookies=cookies,
                                 headers=headers,
                                 params={'mode': 'local', 'id': '2006'},
                                 timeout=10
                                 )
    re.append(response_meta)
    all_cookies['meta'] = requests.utils.dict_from_cookiejar(response_meta.history[1].cookies)

    response_exw = requests.get(url_get_ticket,
                                cookies=cookies,
                                headers=headers,
                                allow_redirects=False,
                                params={'id': '460'},
                                timeout=10
                                )
    re.append(response_exw)

    response_exw = requests.get(response_exw.next.url,
                                headers=response_exw.next.headers,
                                cookies=all_cookies['jxgl'],
                                timeout=10
                                )
    re.append(response_exw)

    # get zhjw cookies
    url = 'http://info.tsinghua.edu.cn/render.userLayoutRootNode.uP'

    response_html = requests.get(url, headers=headers, cookies=cookies, timeout=10)
    re.append(response_html)

    soup = BeautifulSoup(response_html.text, 'html.parser')
    nodes = soup.find_all('iframe')
    response_zhjw1 = requests.get(url=nodes[1]['src'], cookies=cookies, headers=headers, timeout=10)
    response_zhjw2 = requests.get(url=nodes[5]['src'], cookies=cookies, headers=headers, timeout=10)
    re.append(response_zhjw1)
    re.append(response_zhjw2)
    all_cookies['zhjw1'] = requests.utils.dict_from_cookiejar(response_zhjw1.history[0].cookies)
    all_cookies['zhjw2'] = requests.utils.dict_from_cookiejar(response_zhjw2.history[0].cookies)

    # now we get almost all cookies 
    with open('./cookies/cookies.json', 'w') as fp:
        json.dump(all_cookies, fp)
    print('web login successfully!')
    return all_cookies


def main():
    return getCookies(login(False))


if __name__ == '__main__':
    main()
