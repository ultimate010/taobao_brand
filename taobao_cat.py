#!/usr/bin/env python
#-*-coding:utf-8-*-
import time
import datetime
from fetcher import fetcher
import sys
import re

threadsNum = 16


def main():
    if len(sys.argv) != 4:
        print "Usage: python %s urlFile outfile skipNum 1> outfile 2>logFile" % sys.argv[0]
        exit(1)
    count = 0
    pattern = re.compile("rootCatId=([0-9]+)", re.M)
    f = fetcher(threads=threadsNum)
    fileout = open(sys.argv[2],'w')
    fileLog = open('taobao_cat.log','w')
    with open(sys.argv[1],'r') as fi:
        for line in fi:
            line = line.strip('\r\n')
            if(len(line) == 0):
                continue
            count += 1
            if(count < int(sys.argv[3])):
                continue
            line = line.decode('utf-8','ignore')
            arr = line.split('\t')
            if(count % 10 == 0):
                sys.stderr.write("%s:Doing %d %s\n" % (datetime.datetime.now(),count,arr[0].encode('utf-8')))
                fileLog.write("%s:Doing %d %s\n" % (datetime.datetime.now(),count,arr[0].encode('utf-8')))
                fileLog.flush()
            try:
                mystr = arr[0]
                for i in range(len(arr) - 1):
                    f.push(arr[i+1])
                while f.taskleft():
                    url , content = f.pop()
                    ans = pattern.findall(content)
                    for cat in ans:
                        mystr = mystr + "\t" + cat
                fileout.write("%s\n" % mystr.encode('utf-8','ignore'))
                fileout.flush()
                print ("%s\n" % mystr.encode('utf-8','ignore'))
            except Exception as err:
                sys.stderr.write("%s:%s\n" % (datetime.datetime.now(),err))

if __name__ == '__main__':
    main()
