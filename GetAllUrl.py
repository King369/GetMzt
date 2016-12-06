#初始化数据库，并将信息写入数据库：将所有的页面的url信息写入数据库
from Download import request
from MongoQueue import MongoQueue
from bs4 import BeautifulSoup

#初始化数据库队列并命名
spider_queue=MongoQueue("meizixiezhenji","crawl_queue")
def start(url):
    res=request.get(url,3)
    data=BeautifulSoup(res.text,"html.parser")
    all_a=data.find("div",class_="all").find_all("a")
    for a in all_a:
        title=a.get_text()
        url=a["href"]
        spider_queue.push(url,title)
        #将地址信息插入数据库队列中

if __name__=="__main__":
    start("http://www.mzitu.com/all")


# spider_queue = MongoQueue('meinvxiezhenji', 'crawl_queue')
# def start(url):
#     response = request.get(url, 3)
#     Soup = BeautifulSoup(response.text, 'html.parser')
#     all_a = Soup.find('div', class_='all').find_all('a')
#     for a in all_a:
#         title = a.get_text()
#         url = a['href']
#         spider_queue.push(url, title)
#     """上面这个调用就是把URL写入MongoDB的队列了"""
#
# if __name__ == "__main__":
#     start('http://www.mzitu.com/all')