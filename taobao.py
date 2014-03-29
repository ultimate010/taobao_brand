#-*- coding: utf-8 -*-


import requests
import sys
import time
import datetime
import lxml.html as H

TAOBAO_REQ_URL = 'http://s.taobao.com/search'
TAOBAO_XPATH = '//div[@class="tb-content"]/div/div/div/h3/a/@href'
ferr = None


def getTaobao(word,retry = 3):
    time.sleep(3)
    if --retry > 0:
        try:
            par = {'q' : word }
            req = requests.get(TAOBAO_REQ_URL,params = par,timeout = 5)
            if req.status_code != requests.codes.ok:
                yield getTaobao(word,--retry)
            dom_words = H.fromstring(req.text)
            html_words = dom_words.xpath(TAOBAO_XPATH)
            if len(html_words) == 0:
                ferr.write('%s:NO RESULT:%s\n' % (datetime.datetime.now(),word.encode('utf-8','ignore')))
            for word in html_words:
                yield word
        except Exception as err:
            sys.stderr.write("%s:ERR:%s " % (datetime.datetime.now(),err))
    else:
        ferr.write('%s:CAN GET:%s\n' % (datetime.datetime.now(),word.encode('utf-8','ignore')))

def main():
    if len(sys.argv) != 3:
        print "Usage :python %s querryFile skipNum 1> outFile 2> logFile" % sys.argv[0]
        exit(1)
    global ferr
    count = 0
    ferr = open('fail.txt','w')
    with open(sys.argv[1],'r') as myInput:
        for line in myInput:
            line = line.strip('\r\n')
            if len(line) == 0:
                continue
            line = line.decode('utf-8','ignore')
            arr = line.split('/')
            mylist = []
            count += 1
            if(count < int(sys.argv[2])):
                continue
            if(count % 10 == 0):
                sys.stderr.write("%s:Doing %d %s\n" % (datetime.datetime.now(),count,line.encode('utf-8')))
            try:
                if len(arr) > 1:
                    words = getTaobao(arr[1]) #先看中文
                    for word in words:
                        mylist.append(word)
                    if len(mylist) == 0:
                        words = getTaobao(arr[0]) #再看英文
                else:
                    words = getTaobao(arr[0])
                mystr = line+"\t"
                for word in words:
                    mylist.append(word)
                mystr = mystr + "\t".join(mylist)
                if len(mylist) > 0:
                    print mystr.encode('utf-8','ignore')
            except Exception as err:
                sys.stderr.write("%s:ERR:%s " % (datetime.datetime.now(),err))


if __name__ == "__main__":
    main()

