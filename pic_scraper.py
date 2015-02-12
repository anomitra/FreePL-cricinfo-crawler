import requests
import time
from BeautifulSoup import BeautifulSoup
import re
from time import sleep
import urllib

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

def urlify(base_url,arg):
	return str(str(base_url)+str(args))

pid=1
player_list=[]
i=1
url_list=["http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/814789.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/819741.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/816431.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/812413.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817409.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/816765.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/818117.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817901.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/818887.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817889.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817899.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/819825.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/819743.html","http://www.espncricinfo.com/icc-cricket-world-cup-2015/content/squad/817903.html"]
for url in url_list:
	html = crawl(url)
	print "Page crawled."
	parsed_html = BeautifulSoup(html)
	pics=parsed_html.findAll("div",{ "class" : "large-7 medium-7 small-7 columns" })
	for pic in pics:
		image=pic.find("img")
		print image
		base_url="http://www.espncricinfo.com/"
		left="src=\""
		right="\" alt="
		arg = re.search('%s(.*)%s' % (left, right), image)
		imgsrc=urlify(base_url,arg)
		print imgsrc
		urllib.urlretrieve(imgsrc,str(str(pid)+"jpg"))
		pid+=1
	i+=1