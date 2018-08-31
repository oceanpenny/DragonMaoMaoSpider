# encoding=utf-8
#to enable cluster, cookies needed to be accessed by different server, redis is good
#for security base64 or aes or any symmetric encryption algorithm

import json
import time
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import logging
import os
from approot import get_root
from DragonMaoMaoSpider.dao.redisdb import redis_cli
from base64 import b64encode, b64decode

dcap = dict(DesiredCapabilities.PHANTOMJS)
#dcap["phantomjs.page.settings.userAgent"] = (
#    "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
#)
logger = logging.getLogger(__name__)
logging.getLogger("selenium").setLevel(logging.WARNING)

vcode_png = os.path.join(get_root(),'tmp.png')
sina_acounts = [
    {'user': '15995010739', 'pwd': '214620abc'},
    {'user': '18323579862', 'pwd': '214620abc'},
    {'user': 'penghq_mail@163.com', 'pwd': '214620abc'},
    {'user': '1006068025@qq.com', 'pwd': '214620'}
]

#warning PhantomJS do not suport
def get_sina_cookie_from_cn(user, pwd):
    try:
        browser = webdriver.PhantomJS(desired_capabilities=dcap)
        browser.get("https://weibo.cn/login/")
        time.sleep(1)

        failure = 0
        while "微博" in browser.title and failure < 5:
            failure += 1
            browser.save_screenshot(vcode_png)
            username = browser.find_element_by_id('loginName')
            username.clear()
            username.send_keys(user)

            password = browser.find_element_by_id('loginPassword')
            password.clear()
            password.send_keys(pwd)
            try:
                vcode = browser.find_element_by_id('loginVCode')
                vcode.clear()
                code_txt = input("请查看路径下新生成的aa.png，然后输入验证码:")
                vcode.send_keys(code_txt)
            except Exception as e:
                pass
            login = browser.find_element_by_id('loginAction')
            login.click()
            time.sleep(3)

            if "我的首页" not in browser.title:
                time.sleep(4)
            if '未激活微博' in browser.page_source:
                return {}

        cookie = {}
        if "我的首页" in browser.title:
            for elem in browser.get_cookies():
                cookie[elem["name"]] = elem["value"]
            logger.warning("Get Cookie Success!( Account:%s )" % user)
        return json.dumps(cookie)
    except Exception as e:
        print(e)
        logger.warning("Failed %s!" % user)
        return ""
    finally:
        try:
            browser.quit()
            os.remove(vcode_png)
        except Exception as e:
            pass

#ex.key should include spider:cookies:user:pwd, base64 didnt contain '-',so we use -- as split
def initCookie(spiderName, acounts, method):
    for acount in acounts:
        encode_user = b64encode(acount['user'].encode('utf-8')).decode('utf-8')
        encode_pwd = b64encode(acount['pwd'].encode('utf-8')).decode('utf-8')
        if redis_cli.get("%s:Cookies:%s--%s" % (spiderName, encode_user, encode_pwd)) is None:
            cookie = method(acount['user'], acount['pwd'])
            if len(cookie) > 0:
                redis_cli.set("%s:Cookies:%s--%s" % (spiderName, encode_user, encode_pwd), cookie)
    #no cookies, no crwal
    if redis_cli.keys('%s:Cookies' % spiderName) is None:
        logger.warning('%s Cookies None' % spiderName)
        logger.warning("Stopping...")
        os.system("pause")

def updateCookie(accountText, spiderName, method):
    account = b64decode(accountText.split('--')[0].encode('utf-8')).decode('utf-8')
    password = b64decode(accountText.split('--')[1].encode('utf-8')).decode('utf-8')
    cookie = method(account, password)
    if len(cookie) > 0:
        logger.warning("The cookie of %s has been updated successfully!" % account)
        redis_cli.set("%s:Cookies:%s" % (spiderName, accountText), cookie)
    else:
        logger.warning("The cookie of %s updated failed! Remove it!" % accountText)
        removeCookie(accountText,  spiderName)

def removeCookie(accountText, spiderName):
    redis_cli.delete("%s:Cookies:%s" % (spiderName, accountText))
    # no cookies, no crwal
    if redis_cli.keys('%s:Cookies' % spiderName) is None:
        logger.warning('%s Cookies None' % spiderName)
        logger.warning("Stopping...")
        os.system("pause")

if __name__ == '__main__':
    encode_s = b64encode(sina_acounts[0]['user'].encode('utf-8')).decode('utf-8')
    decode_s = b64decode(encode_s).decode('utf-8')
    print(encode_s)
    print(decode_s)
    #initCookie('SinaSpider')
    updateCookie('MTU5OTUwMTA3Mzk=--MjE0NjIwYWJj','SinaSpider', get_sina_cookie_from_cn)
    #print(cookies)