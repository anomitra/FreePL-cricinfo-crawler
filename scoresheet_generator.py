import requests
import time
from BeautifulSoup import BeautifulSoup
import re
import pickle
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

base_url = 'http://www.espncricinfo.com/carlton-mid-triangular-series-2015/engine/current/match/754749.html'
player_dict={"Rohit Sharma":0}
html = crawl(base_url)
print "Page crawled."
parsed_html = BeautifulSoup(html)
bat_table=parsed_html.find("table",{ "class" : "batting-table innings" })
rows=bat_table.findAll("tr",{"class":None})



# BATTING TABLE PARSER


for row in rows:
	name=""
	batScore=0
	runs=0
	fields=row.findAll("td")
	for i in range(0,8):
		if(i==1):
			left="view the player profile for "
			right="\" "
			name = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)
			print name,
		if(i>=2 and i<=8):
			left=">"
			right="</td>"
			result = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)
			#print result,
			if(i==3):
				runs=int(result.strip())
				if(runs==0):
					batScore=batScore-5 #IMPACT DUCK
				batScore=batScore+runs #RUNS SCORE
				batScore=batScore+(runs/25)*10 #MILESTONE BONUS
			if(i==5):
				batScore=batScore+runs-int(result.strip()) #PACE BONUS
			if(i==7):
				batScore=batScore+int(result.strip())*2 #IMPACT SIXES
	#print"  BATSCORE:",batScore
	print ""
	player_dict[name]=batScore
print player_dict
#print rows[1].findAll("td")
#print bat_table
#print parsed_html
