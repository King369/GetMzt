#引进MongoDB数据库来实现不重复存储，
#通过判断数据库中是否存在该文件来进行去重存储，当程序停止执行后，下次执行程序会判断哪些已经存储完毕，不需要二次存储
#能够提高程序的效率，减少重复文件
#缺点：处理的图片量大时需要较长的时间，效率低下
#该文件执行需要调用Download文件中的request方法
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient    #导入MongoClient客户端
from Download import request    #用来抓取html文件
import os,datetime

class meizitu():
    def __init__(self):
        client=MongoClient()  #与MongoDB 建立连接，
        db=client["meizixiezhen"]   #选择一个数据库
        self.mzt_collection=db["meizitu"]
        self.title=""    #用来保存页面主题，也就是文件夹名称
        self.url=""     #用来保存页面地址
        self.img_urls=[]   #初始化列表，用来保存图片地址

    def all_url(self,url):     #用于获取页面链接
        html=request.get(url,3)    #Download里导入的模块request
        all_a=BeautifulSoup(html.text,"html.parser").find("div",{"class":"all"}).find_all("a")  #找到所有a标签的内容
        for a in all_a:
            title=a.get_text()    #获取a标签中的标题，用于文件夹名称
            self.title=title
            print(u"开始保存：",title)
            path=str(title).replace("?","_")
            self.mkdir(path)
            os.chdir("G:\meizt\\"+path)
            href=a["href"]  #获取a标签中的链接
            self.url=href   #将页面地址保存到self.url中
            if self.mzt_collection.find_one({"主题页面":href}):   #判断该页面是否在已经爬取过的页面中,由于在img一个方法中一个
            #完全爬取才会将其主题页面存入数据库
                print(u"这个页面已经爬取过")
            else:
                self.html(href)
    def html(self,url):   #用于获取单个图片链接
        html=request.get(url,3)
        max_span=BeautifulSoup(html.text,"html.parser").find_all("span")[10].get_text()   #获取最大页码
        page_num=0   #作为计数器，用来统计有多少页面被爬取过
        for page in range(1,int(max_span)+1):
            page_url=url+"/"+str(page)
            page_num+=1
            self.img(page_url,max_span,page_num)

    def img(self,page_url,max_span,page_num):   #获取图片地址
        img_html=request.get(page_url,3)
        img_url=BeautifulSoup(img_html.text,"html.parser").find("div",{"class":"main-image"}).find("img")["src"]
        self.img_urls.append(img_url)    #将每次获取的图片地址添加到初始化列表中
        if int(max_span)==page_num:     #已经爬取至最后一张图片
            self.save(img_url)
            post={
                "标题":self.title,
                "主题页面":self.url,
                "图片地址":self.img_urls,
                "获取时间":datetime.datetime.now()
            }
            self.mzt_collection.save(post)    #将post内容写入数据库
            print(u"插入数据库成功")
        else:
            self.save(img_url)     #保存单个图片地址

    def save(self,img_url):    #保存图片
        img_name=img_url[-9:-4]   #用图片地址的后五位作为图片名字
        img=request.get(img_url,3)   #获取图片
        with open(img_name+".jpg","ab") as f:
            f.write(img.content)

    def mkdir(self,path):
        path=path.strip()
        isExists=os.path.exists(os.path.join("G:\meizt",path))
        if not isExists:
            print(u"建立一个名字叫做",path,u"的文件夹")
            os.makedirs(os.path.join("G:\meizt",path))
            return True
        else:
            print(u"文件夹已存在")
            return False

mzt=meizitu()
mzt.all_url("http://www.mzitu.com/all")
