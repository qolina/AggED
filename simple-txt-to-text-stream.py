#! /usr/bin/env python
# -*- coding: utf-8 -*- 

# What this code does:
# Given a Twitter stream in JSON format, extract corresponding text stream, using only English tweets and a subset of the JSON object fields (e.g., date, id, hashtags, urls, text)
# Example run:
# python extract-json-to-text-stream.py test-syria-tweets.json json-to-text-stream-syria.json.txt

import codecs
from datetime import datetime, timedelta
import json
#import requests
import os
import string
import sys
import time

def parse_simple_text_tweet(line):
    arr = line.strip().split("\t")

    tid = arr[6]
    text = arr[8]

    if len(tid) != 18:
     	return ['', '', '', [], [], []]

    date1 = arr[9][:arr[9].find("2012")+4] # 9:00 AM - 6 Nov 2012 from someplace
    # target format: Tue Feb 25 17:30:00 +0000 2014
    dateTemp = datetime.strptime(date1, "%I:%M %p - %d %b %Y")
    dateTemp += timedelta(hours=8)
    date2 = dateTemp.strftime("%a %b %d %H:%M:%S %Y")
    #print "-old", date1
    #print dateTemp
    #print "-new", date2

    nfollowers = 0
    nfriends = 0

    hashtags = []
    users = []
    urls = []
    
    for word in text.split():
        if word[0] == "@":  users.append(word[1:])
        if word[0] == "#":  hashtags.append(word[1:])
        if word.startswith("http"): urls.append(word)

    media_urls = [None]

    return [date2, tid, text, hashtags, users, urls, media_urls, nfollowers, nfriends]	    
    
# def follow_shortlinks(shortlinks):
#     """Follow redirects in list of shortlinks, return dict of resulting long URLs"""
#     links_followed = {}
#     for shortlink in shortlinks:
#         request_result = requests.get(shortlink)
#         links_followed[shortlink] = request_result.url
#     return links_followed
        
'''start main'''    
if __name__ == "__main__":
	file_timeordered_json_tweets = codecs.open(sys.argv[1], 'r', 'utf-8')
	fout = codecs.open(sys.argv[2], 'w', 'utf-8')

        tweetOrdered = {}
	#efficient line-by-line read of big files	
	for line in file_timeordered_json_tweets:
		try:
			[tweet_gmttime, tweet_id, text, hashtags, users, urls, media_urls, nfollowers, nfriends] = parse_simple_text_tweet(line)
# 		if not tweet_gmttime: continue
# 		fout.write(line)
 		#"created_at":"Mon Feb 17 14:14:44 +0000 2014"
			try:
				c = time.strptime(tweet_gmttime.replace("+0000",''), '%a %b %d %H:%M:%S %Y')
			except: 
				print "pb with tweet_gmttime", tweet_gmttime, line
				pass	
			tweet_unixtime = int(time.mktime(c))
                        if tweet_unixtime in tweetOrdered:
                            tweetOrdered[tweet_unixtime].append(str([tweet_unixtime, tweet_gmttime, tweet_id, text, hashtags, users, urls, media_urls, nfollowers, nfriends]))
                        else:
                            tweetOrdered[tweet_unixtime] = [str([tweet_unixtime, tweet_gmttime, tweet_id, text, hashtags, users, urls, media_urls, nfollowers, nfriends])]
			#fout.write(str([tweet_unixtime, tweet_gmttime, tweet_id, text, hashtags, users, urls, media_urls, nfollowers, nfriends]) + "\n")
		except: 
			#print "pb with tweet:", line
#			print sys.exc_info()[0], line
			pass
                #if len(tweetOrdered) == 10: break
 	file_timeordered_json_tweets.close()

        for item in sorted(tweetOrdered.items(), key = lambda a:a[0]):
            for subItem in item[1]:
                fout.write(subItem + "\n")
 	fout.close()
 
