import requests
from lxml import etree
from config_spider import *
def get_r(url):
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0',
             'Cookie':config_cookie}
    r=requests.get(url,headers=headers)
    r.encoding='utf-8'
    text=r.text.replace('\\r','').replace('\\t','').replace('\\n','\n').replace('<script>','').replace('\\','')
    print(text)
    

html=get_r('https://d.weibo.com')
