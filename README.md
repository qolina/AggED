# AggED
This project is an modified version of codes in (Ifrim, 2014, SNOW2014) Event Detection in Twitter using Aggressive Filtering and Hierarchical Tweet clustering.

1. previous preprocessing: json-to-stream.py to convert json format time ordered tweets to text stream used in following procedures.
	Been modified to simple-to-stream.py as we using different downloading tool in different format.
	Note: all tweets' published time are changed to 8 hours later (+8hours), as the time is different to those provided by (Aiello, 2013)

2. use twitter-topics-from-stream.py to obtain topics.
	modifications: allow topic detection in certain time period.
	Bugs found:[Line 761-764] when weighting each term using df in previous time window, dfVocTimeWindow is cleared for every 4 time window.

3. use evaluation for topic recall, keyword precision, keyword recall metrics, which are used in (Aiello, 2013, IEEE Tranc on Multimedia) Sensoring trending topics in twitter .
