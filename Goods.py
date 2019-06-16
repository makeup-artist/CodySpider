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

db_user="visitor"
db_pwd=""
db_host="rm-wz9e4pe6t92vh1t2gyo.mysql.rds.aliyuncs.com"

cody_base = "https://cody.apawn.top"
cody_login = "/api/user/login"
dior_base="https://www.dior.cn"
#口红
base_url="https://www.dior.cn/zh_cn/products/search?page=2&query=%E7%9C%BC%E5%A6%86"

inputDto = {
    "username": "123456789",
    "password": "123456789"
}
headers = {
    "Content-Type": "application/json"
}
response = requests.post(url=cody_base + cody_login, json=inputDto, headers=headers)
response.encoding = response.apparent_encoding
res = json.loads(response.text)
token = res["data"]["token"]

browser = webdriver.Chrome()
browser.get(base_url)
browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
# wait = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME,'grid-view-element is-product one-column legend-bottom')))
time.sleep(5)
html = etree.HTML(browser.page_source)
dior_urls=html.xpath('//li[@class="grid-view-element is-product one-column legend-bottom"]//a/@href')

conn = pymysql.connect(host=db_host, port=3306, user=db_user, password=db_pwd, db='cody', charset='utf8')
cursor = conn.cursor()
id=185
for i in dior_urls:
    product_url=dior_base+i
    browser.get(product_url)
    browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    html = etree.HTML(browser.page_source)
    name=html.xpath('//div[@class="product-titles"]//h1/@id')
    description=html.xpath('//div[@class="product-titles"]//h2/@id')
    details=html.xpath('//div[@class="product-tab-html"]/text()')
    pictures=html.xpath('//div[@class="image"]/img/@src')
    color_names = html.xpath('//span[@class="variation-option-infos-titles"]/span/text()')
    detail=' '.join(str.strip(str(i)) for i in details)
    detail.replace("\n","")
    type=3
    prices=html.xpath('//span[@class="variation-option-price"][1]//text()')
    try:
        price = float(prices[0].replace(" ", "").replace("￥", ""))
    except:
        price = random.uniform(100, 500)

    try:
        print(name[0],description[0],detail,price,pictures[0],color_names[0])
    except:
        continue


    sql_goods="insert into `goods`(id,name,picture,description,details,type,price) values (%s,%s,%s,%s,%s,%s,%s)"
    sql_picture="insert into `picture`(name,goods_id,url) values (%s,%s,%s)"
    cursor.execute(sql_goods,(id,str(name[0]),str(pictures[0]),str(description[0]),detail,type,price))
    for i, j in zip(pictures, color_names):
        cursor.execute(sql_picture, (j,id,i))
    id+=1
    conn.commit()

browser.close()
cursor.close()
conn.close()