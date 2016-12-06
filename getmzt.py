#模拟抓取妹子图网站上的图片，并按名称进行分类存储
#缺点：如果抓取到一半，程序停止执行，下次执行会重头开始抓取
#该文件只需调用Download文件中的request
import requests
from bs4 import  BeautifulSoup
import os
from Download import request    #用来抓取html文件


# def get_html(url):
#     """
#     获取要爬取网页的html代码
#     """
#     header={
#         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         'Accept-Encoding': 'gzip, deflate, sdch',
#         'Accept-Language': 'zh-CN,zh;q=0.8',
#         'Cache-Control': 'max-age=0',
#         'Connection': 'keep-alive',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'
#     }
#     response=requests.get(url,headers=header)
#     return response
#
# # def mkdir(self, path): ##这个函数创建文件夹
# #     path = path.strip()
# #     isExists = os.path.exists(os.path.join("G:\mzitu", path))
# #     if not isExists:
# #         print(u'建了一个名字叫做', path, u'的文件夹！')
# #         os.makedirs(os.path.join("G:\mzitu", path))
# #         return True
# #     else:
# #         print(u'名字叫做', path, u'的文件夹已经存在了！')
# #         return False
#
#
# def get_data(html_txt):
#     """
#     获取要求取得的数据
#     """
#     bs=BeautifulSoup(html_txt.text,"html.parser")
#     # body=bs.body    #获取html页面body部门的内容
#     # print(body)
#     all_a=bs.find("div",{"class":"all"}).find_all("a")
#     for a in all_a:
#         # print(a)                #此时已经获取标签<a>相关的全部内容
#         a_title=a.get_text()   #获取a标签的标题
#         a_link=a["href"]
#         #创建保存路径
#         path=str(a_title).strip().replace("?","_")   #存储文件夹的名字
#         os.makedirs(os.path.join("G:\mzitu", path)) ##创建一个存放套图的文件夹
#         os.chdir("G:\mzitu\\"+path) ##切换到上面创建的文件夹
#         # print(a_title,a_link)
#         content_text=get_html(a_link)    #进行内容页内容抓取，获取内容页的html代码
#         content_data=BeautifulSoup(content_text.text,"html.parser")    #为什么是10？由源代码可知，显示最后一页的span标签为第21个，考虑到标签的成对出现，故从10开始
#         max_span=content_data.find_all("span")[10].get_text()  #查找所有的span标签，并获取最后一个span的值，也就是对应的最多页数
#
#         for page in range(1,int(max_span)+1):
#             page_url=a_link+"/"+str(page)  #获取对应单个图片页面的url地址，下一步获取图片地址
#             # print(page_url)   #
#             image_html=get_html(page_url)
#             img_data=BeautifulSoup(image_html.text,"html.parser")
#             img_url=img_data.find("div",{"class":"main-image"}).find("img")["src"]   #找到对应的图片地址，下一步存储图片
#             # print(img_url)
#             image_name=img_url[-9:-4]   #获取图片名字，取图片地址的除图片格式外的后四位作为名字
#             img=get_html(img_url)   #获取图片内容
#             # print(img)
#             # print(type(img))
#             with open(image_name+".jpg","ab") as f:
#                 f.write(img.content)
#             # f=open(image_name+".jpg","ab")
#             # f.write(img.content)
#             # f.close()
#
#
# if __name__=="__main__":
#     url="http://www.mzitu.com/all"
#     html=get_html(url)
#     get_data(html)


#为了提高程序的复用性，我们使用类来实现该方法
class Meizt():
    # def get_html(self,url):     #获取网页源代码，如果请求的为多媒体文件，则返回二进制文件
    #     header={'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.235'}
    #     html=requests.get(url,headers=header)
    #     return html

    def mkdir(self,path):    #这个函数创建文件存储路径
        path=path.strip()    #根据路径来创建文件夹
        isExists=os.path.exists(os.path.join("G:\meizitu",path))   #判断该路径下的文件夹存在
        if not isExists:
            print(u"建立一个名字为",path,u"的文件夹")
            os.makedirs(os.path.join("G:\meizitu",path))
            return True
        else:
            print(path,u"文件夹已存在")
            return False

    def all_url(self,url):   #获取所有的链接地址
        html=request.get(url,3)    #调用get_html方法获取网页的源码
        all_a=BeautifulSoup(html.text,"html.parser").find("div",{"class":"all"}).find_all("a")   #获取a标签下所有内容
        for a in all_a:
            title=a.get_text()   #获取a标签中的标题，即为即将存储的文件夹名称
            print(u"开始保存：",title)
            path=str(title).replace("?","_")   #由于windows无法创建标题带？的文件夹，所以需将标题中含有的？换成——
            self.mkdir(path)   #调用刚刚创建的方法来创建路径
            os.chdir("G:\meizitu\\"+path)     #切换目录,静谧原文件中有点小问题，即改变目录的写法不对

            href=a["href"]  #获取链接
            self.html(href)   #调用html函数获取套图地址

    def html(self,href):     #该方法用于处理获取的套图地址
        html=request.get(href,3)   #a标签中的href链接    BeautifulSoup匹配span就不会匹配</span>
        max_pagenum=BeautifulSoup(html.text,"html.parser").find_all("span")[10].get_text()  #获取最大页码
        for page in range(1,int(max_pagenum)+1):
            page_url=href+"/"+str(page)     #单个图片的连接
            self.get_img(page_url)   #调用get_img函数获取图片地址

    def get_img(self,page_url):   #获取单个图片的地址
        img_html=request.get(page_url,3)
        #获取图片地址
        img_url=BeautifulSoup(img_html.text,"html.parser").find("div",{"class":"main-image"}).find("img")["src"]
        self.save_img(img_url)

    def save_img(self,img_url):    #存储图片
        img_name=img_url[-9:-4]   #获取图片连接除扩展名外的后五位作为存储的图片名称
        img=request.get(img_url,3)   #获取的图片的二进制文件
        with open(img_name+".jpg","ab") as f:
            f.write(img.content)

meizitu=Meizt()
meizitu.all_url("http://www.mzitu.com/all")






