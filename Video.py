from selenium import webdriver
from lxml import etree
import requests
import json
import oss2
import uuid
import pymysql

auth = oss2.Auth('', '')
image_bucket = oss2.Bucket(auth, 'oss-cn-shenzhen.aliyuncs.com', 'imageszcody')
video_bucket = oss2.Bucket(auth, 'oss-cn-shenzhen.aliyuncs.com', 'videoszcody')
base_url = "https://www.videofk.com/query?keyword=%E5%A6%86"
cody_base = "https://cody.apawn.top"
# cody_base = "http://127.0.0.1:8888"
cody_login = "/api/user/login"
cody_img = "/api/upload/image"
cody_video = "/api/upload/video"
video_add="/api/video/add"

db_user="visitor"
db_pwd=""
db_host="rm-wz9e4pe6t92vh1t2gyo.mysql.rds.aliyuncs.com"

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
uploadHeaders = {
    "Authorization": token,
    "Content-Type": "multipart/form-data"
}
common_headers={
    "Authorization": token,
    "Content-Type":"application/json"
}
browser = webdriver.Chrome()
browser.get(base_url)
browser.execute_script('window.scrollTo(0, document.body.scrollHeight)')
html = etree.HTML(browser.page_source)
titles = html.xpath('//div[@class="img"]//img/@alt')
img_path = html.xpath('//div[@class="img"]//img/@data-img')
video_path = html.xpath('//div[@class="img"]/a[@class="download"]/@data-video')

image_base = "imageszcody.oss-cn-shenzhen.aliyuncs.com/"
video_base = "videoszcody.oss-cn-shenzhen.aliyuncs.com/"

conn = pymysql.connect(host=db_host, port=3306, user=db_user, password=db_pwd, db='cody', charset='utf8')
cursor = conn.cursor()

for i, j, k in zip(titles, img_path, video_path):
    i = i.replace("<span class=red>", "").replace("</span>", "")
    # imageSource = requests.get(j)
    # videoSource = requests.get(k)
    # filename = str(uuid.uuid1())
    # cid1 = oss2.CaseInsensitiveDict()
    # cid2 = oss2.CaseInsensitiveDict()
    # cid1['content-type'] = 'image/jpeg'
    # cid2['content-type'] = 'video/mp4'
    # image_bucket.put_object(uuid, imageSource, headers=cid1)
    # video_bucket.put_object(uuid, videoSource, headers=cid2)
    # print(image_base + filename)
    # print(video_base + filename)

    # file = open("C:\\Users\\hasee\\Desktop\\3344.jpg", 'rb')
    # file_payload = {
    #     "multipartFile":  (filename, open("C:/Users/hasee/Desktop/3344.jpg",'rb'),"image/jpeg")
    # }
    # response = requests.post(cody_base + cody_img, data=file_payload, headers=uploadHeaders)
    # response.encoding = response.apparent_encoding
    # print(response.text)
    videoAddInDto={
        "cover": j,
        "title": i,
        "url": k
    }
    response=requests.post(url=cody_base+video_add,headers=common_headers,data=json.dumps(videoAddInDto))
    response.encoding = response.apparent_encoding
    print(response.text)

browser.close()
conn.commit()
cursor.close()
conn.close()