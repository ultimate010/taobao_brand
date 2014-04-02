#!/usr/bin/env python
#-*-coding:utf-8-*-
import httplib2
from threading import Thread,Lock
from Queue import Queue
import time
import datetime
from gzip import GzipFile
import socket
import sys

socket.setdefaulttimeout(3) #设置5秒后连接超时

class fetcher:
    def __init__(self,threads):
        self.lock = Lock() #线程锁
        self.q_req = Queue() #任务队列
        self.q_ans = Queue() #完成队列
        self.threads = threads
        self.running = 0
        for i in range(threads):
            t = Thread(target=self.threadget,args=(i , ))
            t.setDaemon(True)
            t.start()

    def __del__(self): #解构时需等待两个队列完成
        time.sleep(0.5)
        self.q_req.join()
        self.q_ans.join()

    def taskleft(self):
        sys.stderr.write("req:%d\tans:%d\trunning:%d\n" % (self.q_req.qsize(),self.q_ans.qsize(),self.running))
        #return self.q_req.qsize()+self.q_ans.qsize()+self.running

    def push(self,req):
        self.q_req.put(req)

    def pop(self):
        data = self.q_ans.get()
        self.q_ans.task_done() #ans finish
        return data
    def haveResult(self):
        return self.q_ans.qsize()

    def threadget(self,myId):
        opener = httplib2.Http(".cache",timeout = 3) #复用
        while True:
            req = self.q_req.get()
            self.lock.acquire() #要保证该操作的原子性，进入critical area
            sys.stderr.write("myId:%d\tEnter lock to get req\n"%(myId))
            self.running += 1
            self.lock.release()
            sys.stderr.write("myId:%d\tOut lock to get req\n"%(myId))
#            try:
            ans = self.get(myId,req,opener)
            if ans == '':
                sys.stderr.write("myId:%d\t%s:no ans\n"%(myId,req))
            else:
                sys.stderr.write("myId:%d\t%s:Get ans\n"%(myId,req))
#            except Exception, what:
#                sys.stderr.write("myId:%d\t%s:%s\n" % (myId,datetime.datetime.now(),what))
            self.q_ans.put((req,ans))
            self.lock.acquire() #要保证该操作的原子性，进入critical area
            sys.stderr.write("myId:%d\tEnter lock to put ans\n"%(myId))
            self.running -= 1
            self.lock.release()
            self.q_req.task_done() #req finish
            sys.stderr.write("myId:%d\tOut lock to put ans\n"%(myId))
            time.sleep(1)

    def get(self,myId,req,opener,retries=3):
        try:
            (resp_headers , data) = opener.request(req , "GET")
        except Exception , what:
            if retries>0:
                time.sleep(3)
                return self.get(myId,req,opener,retries-1)
            else:
                sys.stderr.write("myId:%d:\t%s:GET FAIL\tREQ:%s\t%s\n"% (myId,datetime.datetime.now(),req,what))
                return ''
        return data

if __name__ == "__main__":
    links = [ 'http://www.verycd.com/topics/%d/'%i for i in range(5420,5430) ]
    f = fetcher(threads=5)
    count = 0
    for url in links:
        f.push(url)
        count += 1
    while count > 0:

        f.taskleft()
        time.sleep(1)
        url,content = f.pop()
        count -= 1
        print url,len(content)
