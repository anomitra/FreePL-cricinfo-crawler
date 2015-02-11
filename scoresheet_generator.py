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

base_url = 'http://www.espncricinfo.com/carlton-mid-triangular-series-2015/engine/match/754751.html'
player_dict={"Ian Bell":0}
html = crawl(base_url)
print "Page crawled."
parsed_html = BeautifulSoup(html)
bat_table=parsed_html.findAll("table",{ "class" : "batting-table innings" })
for table in bat_table:
	rows=table.findAll("tr",{"class":None})
	
	# BATTING TABLE PARSER FOR BOTH INNINGS
	
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
		if name in player_dict:
			player_dict[name]=player_dict[name]+batScore
		else:
			player_dict[name]=batScore
		print name, "BAT,", batScore

bowl_table=parsed_html.findAll("table",{ "class" : "bowling-table" })
for table in bowl_table:
	rows=table.findAll("tr",{"class":None})
	
	# BOWLING TABLE PARSER FOR BOTH INNINGS
	
	for row in rows:
		name=""
		bowlScore=0
		balls=0
		fields=row.findAll("td")
		for i in range(0,10):
			if(i==1):
				left="view the player profile for "
				right="\" "
				print  name,
				name = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)
			if(i>=2 and i<=10):
				left=">"
				right="</td>"
				result = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)
				#print result,
				if(i==3):
					maidens=int(result.strip())
					if(maidens>0):
						bowlScore=bowlScore+maidens*20 #IMPACT SCORE MAIDENS
				if(i==5):
					wickets=int(result.strip())
					bowlScore=bowlScore+wickets*20 #WICKETS SCORE
					bowlScore=bowlScore+(wickets-1)*10 #MILESTONE BONUS
				if(i==2):
					overs=float(result.strip()) #PACE BONUS
					ov=int(overs)
					balls=ov*6+int((overs-ov)*10)
				if(i==4):
					runs=int(result.strip())
					bowlScore=bowlScore+int(1.5*balls-runs)
					print balls,runs
				if(i==7):
					dots=int(result.strip()) #IMPACT SCORE DOTS
					bowlScore=bowlScore+dots
				
		#print"  BATSCORE:",batScore
		print ""
		if name in player_dict:
			player_dict[name]=player_dict[name]+bowlScore
		else:
			player_dict[name]=bowlScore
		print name, "BOWL,", bowlScore
print player_dict
#print rows[1].findAll("td")
#print bat_table
#print parsed_html
