#1、多进程中，进程之间是不能相互通信的
#2、设置爬取状态，用来告知不同的进程是否需要爬取
from datetime import datetime,timedelta
from pymongo import MongoClient,errors

class MongoQueue():
    OUTSTANDING=1   #初始状态
    PROCESSING=2    #正在被抓取
    COMPLETE=3      #抓取完成

    def __init__(self,db,collection,timeout=300):  #初始化数据库，包含数据库、集合
        self.client=MongoClient()    #创建类的对象
        self.Client=self.client[db]    #创建数据库
        self.db=self.Client[collection]   #创建集合
        self.timeout=timeout

    def __bool__(self):
        """
        如果下面的表达式为真，那么整个类为真
        $ne的意思是不匹配:即如果有装填不是COMPLETE的，则返回真
        """
        record=self.db.find_one(
                {"status":{"$ne":self.COMPLETE}}
        )
        return True if record else False

    def push(self,url,title):    #添加新的url到队列
        try:
            self.db.insert({"_id":url,"status":self.OUTSTANDING,"主题":title})
            print(url,"插入成功")
        except errors.DuplicateKeyError as e:
            print(url,"已经存在于队列中了")
            pass

    def push_imgurl(self,url,title):  #添加图片地址到队列
        try:
            self.db.insert({"_id":title,"statue":self.OUTSTANDING,"url":url})
            print("图片地址插入成功")
        except errors.DuplicateKeyError as e:
            print(url,"图片已经存在")
            pass

    def pop(self):
        """
        查询队列中状态为OUTSTANDING的值，先查询后更改状态为PROCESSING,并记录时间
        """
        record=self.db.find_and_modify(
            query={"status":self.OUTSTANDING},
            update={"$set":{"status":self.PROCESSING,"timestamp":datetime.now()}}
        )
        if record:
            return record["_id"]    #返回更改装填的URL
        else:
            self.repair()    #重置状态为OUTSTANDING
            raise KeyError

    def pop_title(self,url):
        record=self.db.find_one({"_id":url})
        return record["主题"]

    def peek(self):
        """
        取出状态为OUTSTANDING的内容，并返回URL
        """
        record=self.db.find_one({"status":self.OUTSTANDING})
        if record:      #如果查询到状态为OUTSTANDING，则返回URL
            return record["_id"]


    def complete(self,url):
        """
        更新已完成的URL
        """
        self.db.update({"_id":url},{"$set":{"status":self.COMPLETE}})

    def repair(self):
        """
        重置状态，将状态表示转换为OUTSTANDING    $lt用于比较
        """
        record=self.db.find_and_modify(
            query={
                "timestamp":{"$lt":datetime.now()-timedelta(seconds=self.timeout)},
                "status":{"$ne":self.COMPLETE}      #如果装填不是完成，就重置
            },
            update={"$set":{"status":self.OUTSTANDING}}
        )
        if record:
            print("重置URL状态",record["_id"])

    def clear(self):
        """
        删除数据库
        """
        self.db.drop()


