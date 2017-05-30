
## evaluation output of aggED(snow14-Ifrim, Event Detection in Twitter using Aggressive Filtering and Hierarchical Tweet Clustering) with methics shown in (Aiello, 2013, Sensoring trending topics in Twitter)

import re
import os
import sys
import time
from collections import Counter

import numpy as np

import Levenshtein # pip install python-Levenshtein


def extractNewsWords(text):
    tabArr = text.split("\t")
    mandatoryWords = tabArr[0].split(";")
    if len(tabArr) > 1:
        optimalWords = ";".join([wstr for wstr in tabArr[1:] if len(wstr)>0]).split(";")
    else: optimalWords = []
    #print text
    #print mandatoryWords, optimalWords
    return mandatoryWords, optimalWords

    #text = re.sub(";", " ", text)
    #text = re.sub("\[\]", "", text)
    #return text.split()

# return None or matchedString
def wordMatch(gword, sword):
    gword = gword.strip()
    if gword[0] == "[" and gword[-1] == "]":
        gwords = gword.split(" ")
        match_each_gwords = [word for word in gwords if Levenshtein.ratio(word, sword) >= 0.8]
        if len(match_each_gwords) == 0: return None
        else: return " ".join(match_each_gwords)
    else:
        if Levenshtein.ratio(gword, sword) >= 0.8: return gword
        else: return None

def tClusterMatchNews_content(tWords, goldNews):
    tWords = [word.strip("@#") for word in tWords]
    matchedNews_c = []
    kpre = []
    krec = []
    for newsIdx, newsText in enumerate(goldNews):
        mandWords, optWords = extractNewsWords(newsText)

        mandMatched = set([nw for nw in mandWords for tw in tWords if wordMatch(nw, tw) is not None])
        commonWithOpt = set([tw for tw in tWords for nw in optWords if wordMatch(nw, tw) is not None])
        commonWithMand = set([tw for tw in tWords for nw in mandWords if wordMatch(nw, tw) is not None])

        if len(mandMatched) == len(mandWords):
            matchedNews_c.append(newsIdx)
            kpre_val = (len(commonWithMand) + len(commonWithOpt))*1.0/len(tWords)
            krec_val = (len(commonWithMand) + len(commonWithOpt))*1.0/(len(mandWords) + len(optWords))
            kpre.append(kpre_val)
            krec.append(krec_val)
            print len(mandWords),len(optWords), len(commonWithMand), len(commonWithOpt), kpre_val, krec_val
            print commonWithMand

    if len(matchedNews_c) == 0:
        return None, None, None
    return matchedNews_c, kpre, krec

def evalTClusters(tweetClusters, goldNews, outputDetail):
    trueCluster = []
    matchedNews = []
    kpreArr = []
    krecArr = []
    for outIdx, cluster in enumerate(tweetClusters):
        #cWords = cluster.lower().split(", ")
        cWords = cluster.lower().split(" ")

        matchedNews_c, kpre, krec = tClusterMatchNews_content(cWords, goldNews)

        if outputDetail:
            print "############################"
            print "1-** cluster", outIdx
            print cluster

        if matchedNews_c is None: continue

        trueCluster.append((outIdx, matchedNews_c))
        matchedNews.extend(matchedNews_c)
        kpreArr.extend(kpre)
        krecArr.extend(krec)

        if outputDetail:
            sortedNews = Counter(matchedNews_c).most_common()
            for idx, sim in sortedNews:
                print '-MNews', idx, sim, goldNews[idx]

    matchedNews = Counter(matchedNews)
    return len(trueCluster), len(matchedNews), kpreArr, krecArr


def outputEval(Nums):
    print "## Eval newsMatchedCluster", sum(Nums[0]), sum(Nums[1]), round(float(sum(Nums[0])*100)/sum(Nums[1]), 2)
    print "## Eval sysMatchedNews", sum(Nums[2]), sum(Nums[3]), round(float(sum(Nums[2])*100)/sum(Nums[3]), 2)

def outputEval_day(Nums):
    print "## newsPre", Nums[0][-1], Nums[1][-1], ("%.2f" %(Nums[0][-1]*100.0/Nums[1][-1])), "\t",
    print "## newsRecall", Nums[2][-1], Nums[3][-1], "\t", round(float(Nums[2][-1]*100)/Nums[3][-1], 2)


def evalOutputFAEvents(dayClusters, outputDays, devDays, testDays, topK_c, Kc_step, goldFA):
    outputDetail = False

    for sub_topK_c in range(Kc_step, topK_c+1, Kc_step):
        print "KC", sub_topK_c
        if sub_topK_c == topK_c: outputDetail = True

        dev_Nums = [[], [], [], []] # trueCNums, cNums, matchNNums, nNums 
        test_Nums = [[], [], [], []]
        for cItem in dayClusters:
            if cItem is None: continue
            day, texts_day, dataset_day, tweetClusters = cItem
            if tweetClusters is None: continue
            if day not in outputDays: continue

            sub_tweetClusters = tweetClusters[:sub_topK_c]
            goldNews = [item[1] for item in goldFA if item[0] == day]

            if outputDetail:
                print "## News in day", day
                for item in goldNews:
                    print item
                print "## Output details of Clusters in day", day

            trueCNum, matchNNum, kpreArr, krecArr = evalTClusters(sub_tweetClusters, texts_day, goldNews, outputDetail)
            print "## Keyword pre, rec", np.mean(kpreArr), np.mean(krecArr)

            if day in devDays:
                dev_Nums[0].append(trueCNum)
                dev_Nums[1].append(len(sub_tweetClusters))
                dev_Nums[2].append(matchNNum)
                dev_Nums[3].append(len(goldNews))
                if trueCNum > 0:
                    outputEval_day(dev_Nums)
            if day in testDays:
                test_Nums[0].append(trueCNum)
                test_Nums[1].append(len(sub_tweetClusters))
                test_Nums[2].append(matchNNum)
                test_Nums[3].append(len(goldNews))
                if trueCNum > 0:
                    outputEval_day(test_Nums)
                
        ##############

        ##############
        # output evaluation metrics_recall
        if sum(dev_Nums[1]) > 0:
            print "** Dev exp in topK_c", sub_topK_c
            outputEval(dev_Nums)
        if sum(test_Nums[1]) > 0:
            print "** Test exp in topK_c", sub_topK_c
            outputEval(test_Nums)
        ##############

def loadGold(filename):
    gold_topics = {}
    for item in os.listdir(filename): # eg_item = 7_11_2012_0_0.txt
        timeWindow = item[item.find("2012")+5:-4]
        gold_topics_timeWindow = open(filename+"/"+item, "r").readlines()
        gold_topics_timeWindow = [topic.strip() for topic in gold_topics_timeWindow]
        gold_topics[timeWindow] = gold_topics_timeWindow
    return gold_topics

def loadAggTopics(filename, gold_TW):
    aggTopics = open(filename, "r").readlines()
    sysTopics = {}
    for lineIdx in range(1, len(aggTopics)):

        arr = aggTopics[lineIdx].split("\t")
        #(_datetime, headline, words, tweetids, pictures) = arr
        timeWindow = arr[0].split(" ")[1] # 07-11-2012 20:20
        if not arr[0].startswith("07-11-2012"): continue
        timeWindow = "_".join([str(int(timeItem)) for timeItem in timeWindow.split(":")])
        if timeWindow not in gold_TW: continue

        result = arr[1] + " " + arr[2].replace(",", "")
        if timeWindow in sysTopics:
            sysTopics[timeWindow].append(result)
        else:
            sysTopics[timeWindow] = [result]

    return sysTopics


def evalResult(sysTopics, gold_topics):
    evalMetrics = []
    for timeWindow in sorted(sysTopics.keys()):
        tr = 0.0
        kp = 0.0
        kr = 0.0
        matchNNum = 0
        kpreArr = []
        krecArr = []

        topics = sysTopics[timeWindow]
        gold_topics_tw = gold_topics.get(timeWindow)
        print "----------------------------## timeWindow", timeWindow
        #print "-------------Sys"
        #for item in topics:
        #    print item
        print "-------------Gold"
        for item in gold_topics_tw:
            print item
            mandWords, optWords = extractNewsWords(item)
            print "Gold", mandWords, optWords

        trueCNum, matchNNum, kpreArr, krecArr = evalTClusters(topics, gold_topics_tw, True)

        tr = matchNNum*1.0/len(gold_topics_tw)
        if len(kpreArr) > 0: kp = np.mean(kpreArr)
        if len(krecArr) > 0: kr = np.mean(krecArr)
        metrics = [tr, kp, kr]
        print metrics
        evalMetrics.append(metrics)

    trs = [item[0] for item in evalMetrics]
    kps = [item[1] for item in evalMetrics]
    krs = [item[2] for item in evalMetrics]
    print "TR, KP, KR", np.mean(trs), np.mean(kps), np.mean(krs)

if __name__ == "__main__":
    print "Usage: python evaluation.py aggTopicsFilename goldTruthDir"
    gold_topics = loadGold(sys.argv[2])
    gold_TW = gold_topics.keys()
    print sorted(gold_TW)

    # load output of aggED
    sysTopics = loadAggTopics(sys.argv[1], gold_TW)


    evalResult(sysTopics, gold_topics)
