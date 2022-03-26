from bs4 import BeautifulSoup
import urllib.request, urllib.error
import json
import os
import xlwt
import requests

count = []  # 统计数量
picList = []  # 保存图片链接

head = {  # 模拟浏览器头部信息，向哔哩哔哩服务器发送消息
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
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
    print('正在抓取b站up主：' + title + '的动态....')
    return title


def getData(uid):
    datalist = []  # 逐一解析数据
    for page in range(0, 100):  # 调用获取页面信息的函数
        url = f"https://api.vc.bilibili.com/link_draw/v1/doc/doc_list?uid={uid}&page_num={page}&page_size=30&biz=all"
        html = askURL(url)  # 保存获取到的网页源码
        # print(html)       #测试网页源码

        dic = json.loads(html)  # 保存源码

        if len(dic.get("data").get("items")) == 0:  # 如果找不到数据就停止
            break

        item_list = dic.get("data").get("items")  # 返回的数据字典中信息在items中
        # print(item_list )
        # print("\n")

        # 逐一解析数据
        for item in item_list:
            data = []  # 保存一条动态的所有信息
            # 图片链接
            if len(item.get("pictures")[0].get("img_src")) != 0:
                picItem = item.get("pictures")[0].get("img_src")
                data.append(picItem)
                picList.append(picItem)
            else:
                data.append(' ')
                picList.append(' ')

            # 动态内容
            wordItem = item.get("description")
            data.append(wordItem)
            count.append(wordItem)

            # 浏览量数据
            viewItem = item.get("view")
            data.append(viewItem)

            # 点赞数据
            likeItem = item.get("like")
            data.append(likeItem)
            datalist.append(data)

    # print(datalist)   #测试
    # print(picList)
    return datalist


def download(datalist, uid, title, foldTitle):
    while True:
        ifDownloadData = input("要下载动态内容以表格形式保存到文件夹里吗？请输入是（y），否（n):")
        if ifDownloadData == 'y' or ifDownloadData == 'n':
            break
        else:
            print("请回答y or n！！！！！")
        continue

    while True:
        ifDownloadPic = input("要下载动态里面的图片到文件夹里吗？请输入是（y），否（n):")
        if ifDownloadPic == 'y' or ifDownloadPic == 'n':
            break
        else:
            print("请回答y or n！！！！！")
        continue

    if ifDownloadData and ifDownloadPic != "n":
        if ifDownloadData == "y":
            saveData(datalist, uid, title, foldTitle)  # 下载数据并保存
            print("--下载动态数据结束--")
        else:
            print("--动态数据未下载--")
        if ifDownloadPic == "y":
            savePic(picList, uid, title, foldTitle)  # 下载数据并保存
            print("--下载动态图片结束--")
        else:
            print("--动态图片未下载--")
    else:
        for i in range(0, 100):
            print("啥都不下你有病是吧？")


def saveData(datalist, uid, title, foldTitle):  # 保存图片到本地
    print("开始下载" + title + "的动态内容...")
    # folder_path = str("./output" + "/uid=" + uid + " " + title)       #设置默认路径为output子文件夹
    folder_path = str("./" + foldTitle + "/uid=" + uid + " " + title)  # 自由设置文件夹
    savepath = folder_path + "/uid=" + uid + " " + title + ".xls"
    if not os.path.exists(folder_path):  # 如果不存在这个路径
        os.makedirs(folder_path)  # 创建img目录和up主的uid子文件夹

    # 下载动态
    print(f"共有{len(count)}条动态，开始下载动态")
    book = xlwt.Workbook(encoding="utf-8", style_compression=0)  # 创建workbook对象
    sheet = book.add_sheet(title + '的Bilibili空间动态', cell_overwrite_ok=True)  # 创建工作表
    col = ("图片链接", "动态内容", "浏览量", "点赞数")
    for i in range(0, 4):
        sheet.write(0, i, col[i])  # 列名
    for i in range(len(count)):
        print("正在下载第%d条动态..." % (i + 1))
        data = datalist[i]
        for j in range(0, 4):
            sheet.write(i + 1, j, data[j])  # 写入数据

    book.save(savepath)


def savePic(picList, uid, title, foldTitle):
    print("开始下载" + title + "的动态图片...")

    # folder_path = str("./output" + "/uid=" + uid + " " + title)       #设置默认路径为output子文件夹

    folder_path = str("./" + foldTitle + "/uid=" + uid + " " + title)  # 自由设置文件夹
    if not os.path.exists(folder_path):  # 如果不存在这个路径
        os.makedirs(folder_path)  # 创建img目录和up主的uid子文件夹

    # 下载图片
    print(f"共有{len(picList)}张图片，开始下载图片...")
    for i in range(len(picList)):
        content = requests.get(
            picList[i], headers=head, verify=False
        ).content
        with open(f"{folder_path}/{i + 1}.jpg", "wb") as f:  # 开始写入
            f.write(content)
        print(f"第{i + 1}张图片正在下载中....")


def main():
    requests.packages.urllib3.disable_warnings()  # 不显示警告信息
    uid = str(input("请输入你要抓取的up主的uid:"))  # 用户id，up主空间url中的最后一串数字
    foldTitle = input("请输入你要保存的文件夹的名字:")  # 用户id，up主空间url中的最后一串数字
    title = getTitle(uid)  # 获取up主名字
    datalist = getData(uid)  # 获取数据
    download(datalist, uid, title, foldTitle)   # 下载内容


if __name__ == "__main__":
    main()
