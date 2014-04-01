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

socket.setdefaulttimeout(5) #设置5秒后连接超时

class fetcher:
    def __init__(self,threads):
        self.lock = Lock() #线程锁
        self.q_req = Queue() #任务队列
        self.q_ans = Queue() #完成队列
        self.threads = threads
        self.running = 0
        for i in range(threads):
            t = Thread(target=self.threadget)
            t.setDaemon(True)
            t.start()

    def __del__(self): #解构时需等待两个队列完成
        time.sleep(0.5)
        self.q_req.join()
        self.q_ans.join()

    def taskleft(self):
        return self.q_req.qsize()+self.q_ans.qsize()+self.running

    def push(self,req):
        self.q_req.put(req)

    def pop(self):
        data = self.q_ans.get()
        self.q_ans.task_done()
        return data
    def haveResult(self):
        return self.q_ans.qsize()

    def threadget(self):
        opener = httplib2.Http(".cache") #复用
        while True:
            req = self.q_req.get()
            self.lock.acquire() #要保证该操作的原子性，进入critical area
            self.running += 1
            self.lock.release()
            try:
                ans = self.get(req,opener)
            except Exception, what:
                sys.stderr.write("%s:%s\n" % (datetime.datetime.now(),what))
            self.q_ans.put((req,ans))
            self.lock.acquire() #要保证该操作的原子性，进入critical area
            self.running -= 1
            self.lock.release()
            self.q_req.task_done()
            time.sleep(1)

    def get(self,req,opener,retries=3):
        try:
            (resp_headers , data) = opener.request(req , "GET")
        except Exception , what:
            if retries>0:
                time.sleep(3)
                return self.get(req,opener,retries-1)
            else:
                sys.stderr.write("%s:GET FAIL\tREQ:%s\t%s\n"% (datetime.datetime.now(),req,what))
                return ''
        return data

if __name__ == "__main__":
    links = [ 'http://www.verycd.com/topics/%d/'%i for i in range(5420,5430) ]
    f = fetcher(threads=5)
    for url in links:
        f.push(url)
    while f.taskleft():
        time.sleep(1)
        url,content = f.pop()
        print url,len(content)
