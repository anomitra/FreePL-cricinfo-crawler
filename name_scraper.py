import requests
import time
from BeautifulSoup import BeautifulSoup
import re
from time import sleep

def crawl(url):
	while True:
		try:
			print "trying to get URL... ",
			r=requests.get(url)
			print "Got URL!"
			return r.content
		except Exception as e:
			print e
			sleep(2)
			print "Retrying!!"

pid=1
player_list=[]
i=1
url_list=["http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/814789.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/819741.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/816431.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/812413.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817409.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/816765.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/818117.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817901.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/818887.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817889.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817899.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/819825.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/819743.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817903.html"]
for url in url_list:
	html = crawl(url)
	print "Page crawled."
	parsed_html = BeautifulSoup(html)
	names=parsed_html.findAll("h3",{ "class" : None })
	print names
	for name in names:
		print pid,
		file=open("player1.csv","a")
		file.write(str(pid))
		file.write(",")
		pid+=1
		nametext=name.find('a').text
		lst=nametext.split(' ')
		print lst
		file.write(str(str(lst[0])+","))
		if(1<len(lst)):
			file.write(str(lst[1]))
		file.write(str(","+str(i)+"\n"))
		file.write("\n")
		file.close()
	i+=1