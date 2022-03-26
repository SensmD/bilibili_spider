import requests
# from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import urllib.request, urllib.error
import json
import os

head = {  # 模拟浏览器头部信息，向哔哩哔哩服务器发送消息
    "User-Agent": "luos",
    "cookie": "_uuid=4B7D3F0B-1CEE-896D-32DB-155F7EE36DD023801infoc; buvid3=53685CAD-F009-4818-BC6A-2B22EF351C5A13449infoc; bfe_id=018fcd81e698bbc7e0648e86bdc49e09"
}


# 用户代理，表示告诉哔哩哔哩服务器，我们是什么类型的机器，浏览器（本质上是告诉浏览器，我们可以接受什么水平的文件内容）


def askURL(url):
    # req = requests.get(url, headers=head)
    request = urllib.request.Request(url, headers=head)
    # html=req.text #创建一个网页代码字符串
    html = ""  # 创建网页源码的容器
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html) #测试是否保存好代码了
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    # print(html)
    return html


def getTitle(uid):  # 获取b站up主的用户名
    baseurl = f"https://space.bilibili.com/{uid}/dynamic"
    # print(baseurl)
    # 1.爬取网页
    bsurl = askURL(baseurl)
    bs = BeautifulSoup(bsurl, "html.parser")
    title = str(bs.title.string)
    title = title.replace("的个人空间_哔哩哔哩_Bilibili", "")
    print('正在抓取b站up主：' + title + '的主页图片....')
    return title


def getData(uid):
    datalist = []  # 逐一解析数据
    for page in range(0, 100):  # 调用获取页面信息的函数
        url = f"https://api.vc.bilibili.com/link_draw/v1/doc/doc_list?uid={uid}&page_num={page}&page_size=30&biz=all"
        html = askURL(url)  # 保存获取到的网页源码
        # print(html)       #测试网页源码

        dic = json.loads(html)  # 保存源码
        if len(dic.get("data").get("items")) == 0:
            break

        item_list = dic.get("data").get("items")  # 返回的数据字典中信息在items中
        # print(item_list )
        # print("\n")

        # 逐一解析图片数据
        for picItem in item_list:
            # item是图片链接
            picItem = picItem.get("pictures")[0].get("img_src")
            datalist.append(picItem)

    print(datalist)
    return datalist


# 保存图片到本地
def saveData(dataList, uid, title, foldtitle):
    # file_path = str("./imgs" + "/uid=" + uid + " " + title)       #设置默认路径为/imgs子文件夹
    file_path = str("./" + foldtitle + "/uid=" + uid + " " + title)  # 自由设置文件夹
    if not os.path.exists(file_path):  # 如果不存在这个路径
        os.makedirs(file_path)  # 创建img目录和up主的uid子文件夹

    print(f"共有{len(dataList)}张图片。")

    for i in range(len(dataList)):
        content = requests.get(
            dataList[i], headers=head, verify=False
        ).content

        with open(f"{file_path}/{i + 1}.jpg", "wb") as f:  # 开始写入
            f.write(content)
        print(f"第{i + 1}张图片正在下载中....")


def main():
    # 不显示警告信息
    requests.packages.urllib3.disable_warnings()
    uid = str(input("请输入你要抓取的up主的uid:"))  # 用户id，up主空间url中的最后一串数字
    foldTitle = input("请输入你要保存的文件夹的名字:")  # 用户id，up主空间url中的最后一串数字
    title = getTitle(uid)  # 获取up主名字
    dataList = getData(uid)  # 获取图片链接
    saveData(dataList, uid, title, foldTitle)  # 下载图片并保存


if __name__ == "__main__":
    main()
    print("--下载成功--")
