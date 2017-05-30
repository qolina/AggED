
import sys
from datetime import datetime
import codecs
import time



tweetfilename = sys.argv[1]
idfilename = sys.argv[2]
ids = open(idfilename, "r").readlines()
ids = [item.strip() for item in ids]

file_tweets = open(tweetfilename, "r").readlines()
for lineIdx, line in enumerate(file_tweets):
    if lineIdx > 1000000: continue
    if lineIdx < 600000: continue
    print lineIdx, line
    arr = line.strip().split("\t")
    tid = arr[6]
    if tid not in ids: continue

    date1 = arr[9][:arr[9].find("2012")+4] # 9:00 AM - 6 Nov 2012 from someplace
    if not date1[0].isdigit(): print date1
    # target format: Tue Feb 25 17:30:00 +0000 2014
    dateStr = time.strptime(date1, "%I:%M %p - %d %b %Y")
    date2 = time.strftime("%a %b %d %H:%M:%S %Y", dateStr)

    hour = time.strftime("%H", dateStr)
    mins = time.strftime("%M", dateStr)
    twStr = str(int(hour))+"_"+str(int(mins))
    if twStr != "0_0":
        print "-time no", twStr
    else:
        print "-time yes", twStr

