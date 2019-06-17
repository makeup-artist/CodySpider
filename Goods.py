from selenium import webdriver
from lxml import etree
import requests
import json
import uuid
import pymysql
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random
import logging

logging.basicConfig(format='%(asctime)s - [line:%(lineno)d] - %(levelname)s: %(message)s',
                    level=logging.INFO)

db_user="visitor"
db_pwd=""
db_host="rm-wz9e4pe6t92vh1t2gyo.mysql.rds.aliyuncs.com"


type_dict={
    '唇妆':1,
    '底妆':2,
    '眼妆':3,
    '护肤':4,
    '香水':5
}
types={'唇妆','底妆','眼妆','护肤','香水'}
base_page_url="https://www.dior.cn/zh_cn/products/search?page={}&query={}"
base_url="https://www.dior.cn/zh_cn/products/search?query={}"
dior_base="https://www.dior.cn"


cody_base = "https://cody.apawn.top"
cody_login = "/api/user/login"
inputDto = {
    "username": "",
    "password": ""
}
headers = {
    "Content-Type": "application/json"
}
response = requests.post(url=cody_base + cody_login, json=inputDto, headers=headers)
response.encoding = response.apparent_encoding
res = json.loads(response.text)
token = res["data"]["token"]

browser = webdriver.Chrome()
conn = pymysql.connect(host=db_host, port=3306, user=db_user, password=db_pwd, db='cody', charset='utf8')
cursor = conn.cursor()
id=1
page=1

for type in types:

    type_url=base_url.format(type)
    # wait = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME,'grid-view-element is-product one-column legend-bottom')))
    browser.get(type_url)
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(5)
    html = etree.HTML(browser.page_source)
    dior_urls = html.xpath('//li[@class="grid-view-element is-product one-column legend-bottom"]//a/@href')
    logging.info("type={} page=1 len={} url={}".format(type,len(dior_urls),type_url))
    try:
        # 获取该类型所有产品url
        while browser.find_element_by_class_name("search-results-load-more"):
            page += 1
            page_url = base_page_url.format(page, type)
            browser.get(page_url)
            browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            time.sleep(5)
            html = etree.HTML(browser.page_source)
            logging.info("type={} page={} url={}".format(type,page, page_url))
            dior_urls += html.xpath('//li[@class="grid-view-element is-product one-column legend-bottom"]//a/@href')
            logging.info("type={} len={}".format(type, len(dior_urls)))
    except:
        page=1

    for i in dior_urls:
        product_url = dior_base + i
        logging.info("crawl url={}".format(product_url))
        browser.get(product_url)
        browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        html = etree.HTML(browser.page_source)
        name = html.xpath('//div[@class="product-titles"]//h1/@id')
        description = html.xpath('//div[@class="product-titles"]//h2/@id')
        details = html.xpath('//div[@class="product-tab-html"]/text()')
        pictures = html.xpath('//div[@class="generic-variations"]//div[@class="image"]/img/@src')
        first_picture=html.xpath('//li[@class="product-medias-grid-image"]//img/@src')
        color_names = html.xpath('//div[@class="generic-variations"]//label/text()')
        detail = ' '.join(str.strip(str(i)) for i in details)
        detail.replace("\n", "").replace('\r','')
        prices = html.xpath('//span[@class="variation-option-price"][1]//text()')
        try:
            price = float(prices[0].replace(" ", "").replace("￥", ""))
        except:
            price = random.uniform(100, 500)

        if len(name) and len(description):
            pass
        else:
            continue
        logging.info("name={} description={} detail={} price={} pictures={} color_names={} first_picture={}".format(name,description,detail,price,pictures,color_names,first_picture[0]))

        sql_goods = "insert into `goods`(id,name,picture,description,details,type,price) values (%s,%s,%s,%s,%s,%s,%s)"
        sql_picture = "insert into `picture`(name,goods_id,url) values (%s,%s,%s)"
        cursor.execute(sql_goods, (id, str(name[0]), str(first_picture[0]), str(description[0]), detail, type_dict[type], price))
        for i, j in zip(pictures, color_names):
            cursor.execute(sql_picture, (j, id, i))
        id += 1
        conn.commit()

browser.close()
cursor.close()
conn.close()
