import os
import time
from pytz import timezone
from datetime import datetime
from json import load
from smtplib import SMTP
from email.message import EmailMessage
import threading
import report
import login


PRINT_LOG = True
QUERY_INTERVAL = 20     # query interval (s)
tz = timezone('Asia/Shanghai')
suffix = '@mails.tsinghua.edu.cn'
receiver = None     # None will send email to the sender
send_to_self = receiver is None


def report_query(log):
    log = '{}: {}'.format(time_str(), log)
    if PRINT_LOG:
        print(log)
    try:
        with open('./cache/account', 'r', encoding='utf-8') as fp:
            data = load(fp)
        global receiver
        sender = data['userName'] + suffix
        if send_to_self:
            receiver = sender
        # try 3 times
        times = 5
        for i in range(times):
            try:
                with SMTP('smtp.tsinghua.edu.cn') as s:
                    s.ehlo()
                    s.starttls()
                    s.login(sender, data['password'])
                    msg = EmailMessage()
                    msg.set_content(log)
                    msg['From'] = sender
                    msg['To'] = receiver
                    msg['Subject'] = 'GPA Querier'
                    s.send_message(msg)
                    print('send email successfully!')
                break
            except Exception as e:
                if i < times - 1:
                    continue
                else:
                    raise e
    except Exception as e:
        print('Error:', e)
        return False
    return True


def time_str(stamp=None):
    if stamp is None:
        stamp = time.time()
    return datetime.fromtimestamp(stamp, tz=tz).strftime('%Y/%m/%d %H:%M:%S')


def start_query(cnt=0):
    try:
        cookie_jxgl, cookie_zhjw = report.get_cookie(login.main())
    except Exception as e:
        print(e)
        print('轮询系统登录失败!')
        return start_query(cnt)
    gpa_save, flag, query_log = report.query(cookie_jxgl, None)
    credits_save, flag, check_log = report.check(cookie_zhjw, None)
    if '失败' in query_log or '失败' in check_log:
        print('轮询系统第{}次启动失败！'.format(cnt))
        return start_query(cnt + 1)
    else:
        print(query_log)
        print(check_log)
    threading.Timer(1, query, [None, None, cookie_jxgl, cookie_zhjw]).start()
    return 0


def query(gpa_save, credits_save, cookie_jxgl, cookie_zhjw, cnt=0):
    def fail_process():
        if cnt < 2:
            threading.Timer(10, query, [gpa_save, credits_save, cookie_jxgl, cookie_zhjw, cnt + 1]).start()
        else:
            start_query(cnt=0)
        return

    try:
        gpa_save, flag, query_log = report.query(cookie_jxgl, gpa_save)
        credits_save, flag, check_log = report.check(cookie_zhjw, credits_save)
    except Exception as e:
        print(e)
        return fail_process()
    if query_log:
        if '失败' in query_log:
            return fail_process()
        report_query(query_log)
    if check_log:
        if '失败' in check_log:
            return fail_process()
        report_query(check_log)

    threading.Timer(QUERY_INTERVAL, query, [gpa_save, credits_save, cookie_jxgl, cookie_zhjw]).start()
    return


if __name__ == '__main__':
    if not os.path.isdir('./cache'):
        os.mkdir('./cache')
    start_query()
