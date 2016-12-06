#该程序执行之前需要先执行MongoQueue文件，清空数据库
#然后执行GetAllUrl将数据路列表进行初始化
#然后执行该程序，从数据库中取数据，并进行分类存储
import os
import time
import threading
import multiprocessing
from MongoQueue import MongoQueue
from Download import request
from bs4 import BeautifulSoup

SLEEP_TIME=1   #设置睡眠时间为1秒
def meizitu_crawler(max_threads=10):
    crawl_queue=MongoQueue('meinvxiezhenji', 'crawl_queue')   #获取队列里的URL
    def pageurl_crawler():
        while True:
            try:
                url=crawl_queue.pop()     #取出url
                print(url)
            except KeyError:
                print("队列没有数据")
                break
            else:
                img_urls=[]
                res=request.get(url,3)    #获取取出的url对应的html代码
                title=crawl_queue.pop_title(url)
                path=str(title).replace("?","_")
                mkdir(path)
                os.chdir("G:\Meizitu\\"+path)
                #获取最大页码
                max_span=BeautifulSoup(res.text,"html.parser").find("div",{"class":"pagenavi"}).find_all("span")[-2].get_text()
                for page in range(1,int(max_span)+1):
                    page_url=url+"/"+str(page)   #获取单个图片所在页面对应的url地址
                    #获取图片链接
                    img_url=BeautifulSoup(request.get(page_url,3).text,"html.parser").find("div",{"class":"main-image"}).find("img")["src"]
                    img_urls.append(img_url)
                    save(img_url)
                    crawl_queue.complete(url)  #设置为完成状态

    def save(url):
        name=url[-9:-4]   #取图片地址的后五位作为文件名
        print(u"开始保存",url)
        img=request.get(url,3)
        #多媒体文件写入，注意写入的方式，多媒体文件其实已二进制形式存储
        with open(name+".jpg","ab") as f:
            f.write(img.content)

    def mkdir(path):
        path=path.strip()
        isExist=os.path.exists(os.path.join("G:\Meizitu",path))    #不区分大小写
        if not isExist:
            print(u"建立一个名字为：",path,u"的文件夹")
            os.makedirs(os.path.join("G:\Meizitu",path))
            return True
        else:
            print(u"名字叫做",path,u"的文件夹已存在")
            return False

    threads=[]
    while threads or crawl_queue:
        """这里用crawl_queue就是前文的__bool__函数的作用，如果crawl_queue和
        threads有一个为真，说明没有下载完，继续下载"""
        for thread in threads:
            if not thread.is_alive():    #判断是否为空,不为空则删除，每次使用保证线程为空
                threads.remove(thread)

        while len(threads)<max_threads or crawl_queue.peek():
            thread=threading.Thread(target=pageurl_crawler)    #创建线程,目标pageurl_crawler
            thread.setDaemon(True)   #设置守护线程
            thread.start()   #启动线程
            threads.append(thread)   #添加进线程队列
        time.sleep(SLEEP_TIME)   #休息1秒

def process_crawler():
    #进程处理
    process=[]
    num_cpus=multiprocessing.cpu_count()
    print("将会启动的进程数为：",num_cpus)
    for i in range(num_cpus):
        p=multiprocessing.Process(target=meizitu_crawler)    #创建进程，目标meizitu_crawler
        p.start()   #启动进程
        process.append(p)

    for p in process:
        p.join()      #等待进程队列里面的进程结束

if __name__=="__main__":
    process_crawler()



