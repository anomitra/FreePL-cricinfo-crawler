import requests
import time
from BeautifulSoup import BeautifulSoup
import re
import pickle
from time import sleep


""" CRAWLS AN URL """

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

""" HANDLES THE DISMISSAL DETAILS -- INCLUDING THE TYPE OF DISMISSAL AND THE PERPETRATORS"""

def dismissal_handler(how_out):
	fielding_stats={}
	other=""
	bowler=""
	l=[]
	fieldingstat={"catches":0, "stumpings":0, "runouts":0}
	if(re.match('c.*b.*',how_out)):  #CATCH OUT
		left="c "
		right=" b "
		other = re.search('%s(.*)%s' % (left, right), how_out).group(1)
		left="b "
		bowler = re.search('%s(.*)' % (left), how_out).group(1)
		print "CAUGHT ", other, bowler
		fieldingstat["catches"]=1
		other=other.strip()

	elif(re.match('lbw b.*',how_out)): #LEG BEFORE WICKET
		left="lbw b "
		bowler=re.search('%s(.*)' % (left), how_out).group(1)
		print "LBW ",bowler

	elif(re.match('b.*',how_out)): #BOWLED
		left="b "
		bowler=re.search('%s(.*)' % (left), how_out).group(1)
		print "BOWLED ",bowler

	elif(re.match('c & b .*',how_out)): #CAUGHT AND BOWLED
		left="c & b "
		bowler=re.search('%s(.*)' % (left), how_out).group(1)
		print "CAUGHT+BOWLED ",bowler
		bowler=bowler.strip()
		other=bowler
		fieldingstat["catches"]=1

	elif(re.match('st.*b.*',how_out)): #STUMPED
		left="st "
		right=" b "
		other = re.search('%s(.*)%s' % (left, right), how_out).group(1)
		left="b "
		fieldingstat["stumpings"]=1
		bowler = re.search('%s(.*)' % (left), how_out).group(1)
		print "STUMPED ", other, bowler

	elif(re.match('run out .*',how_out)): #RUN OUT
		left=how_out.index('(')
		right=how_out.index(')')
		
		throwers = how_out[left+1:right]
		
		t=throwers.split('/')
		
		print throwers,"thrower"
		fieldingstat["runouts"]=1
		if bowler in fielding_stats:
			fielding_stats[bowler]["runouts"]+=1
		else:
			fielding_stats[bowler]=fieldingstat
		if(len(t)==2):
			other2=t[1]
			f=fieldingstat.copy()
			f["runouts"]=1
			l.append([other,f])
		fieldingstat["runouts"]=1
		other=t[0]
		print "RUN OUT",t
	
	else: #NOT OUT
		print "NOT OUT"
	l.append([other,fieldingstat])
	return l


def score_data(base_url):
	#base_url = 'http://www.espncricinfo.com/carlton-mid-triangular-series-2015/engine/match/754751.html'
	all_stats={} # STORES *ALL* THE STATS OF *ALL* THE PLAYERS INVOLVED IN THE MATCH
	fielding_stats={}
	error=''
	try:
	    player_dict={}
	    html = crawl(base_url)
	    print "Page crawled."
	    parsed_html = BeautifulSoup(html)
	    bat_table=parsed_html.findAll("table",{ "class" : "batting-table innings" })

	    for table in bat_table:
		    rows=table.findAll("tr",{"class":None})
		    
		    # BATTING TABLE PARSER FOR BOTH INNINGS
		    
		    for row in rows:
			    playerstatdict={"runsmade":0, "wickets":0, "ballsfaced":0, "fours":0, "sixes":0,"oversbowled":0, "maidenovers":0, "runsgiven":0, "dotsbowled":0, "mom":0, "dnb":0, "funscore":0}
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
					    if(i==2):
						    d=dismissal_handler(result)
						    for entry in d:
							    name = entry[0]
							    stats = entry[1]
							    if name in fielding_stats:
								for key in stats:
								    fielding_stats[name][key]+=stats[key]
							    else:
								fielding_stats[name]=stats

					    if(i==3):
						    runs=int(result.strip())
						    if(runs==0):
							    batScore=batScore-5 #IMPACT DUCK
						    batScore=batScore+runs #RUNS SCORE
						    playerstatdict["runsmade"]=runs
						    batScore=batScore+(runs/25)*10 #MILESTONE BONUS
					    if(i==5):
						    batScore=batScore+runs-int(result.strip()) #PACE BONUS
						    playerstatdict["ballsfaced"]=int(result.strip())
					    if(i==6):
						    playerstatdict["fours"]=int(result.strip())
					    if(i==7):
						    batScore=batScore+int(result.strip())*2 #IMPACT SIXES
						    playerstatdict["sixes"]=int(result.strip())
			    #print"  BATSCORE:",batScore
			    print ""
			    if name in player_dict:
				    player_dict[name]=player_dict[name]+batScore
			    else:
				    player_dict[name]=batScore
			    #print name, "BAT,", batScore
		    
			    all_stats[name]=playerstatdict
	    bowl_table=parsed_html.findAll("table",{ "class" : "bowling-table" })
	    for table in bowl_table:
		    rows=table.findAll("tr",{"class":None})
		    
		    # BOWLING TABLE PARSER FOR BOTH INNINGS
		    
		    for row in rows:
			    playerstatdict={"runsmade":0, "wickets":0, "ballsfaced":0, "fours":0, "sixes":0, "oversbowled":0.0, "maidenovers":0, "runsgiven":0, "dotsbowled":0, "mom":0, "dnb":0, "funscore":0}
			    name=""
			    bowlScore=0
			    balls=0
			    fields=row.findAll("td")
			    for i in range(0,10):
				    if(i==1):
					    left="view the player profile for "
					    right="\" "
					    #print  name,
					    name = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)
				    if(i>=2 and i<=10):
					    left=">"
					    right="</td>"
					    result = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)
					    #print result,
					    if(i==3):
						    maidens=int(result.strip())
						    playerstatdict["maidenovers"]=maidens
					    if(i==5):
						    wickets=int(result.strip())
						    playerstatdict["wickets"]=wickets
					    if(i==2):
						    overs=float(result.strip())
						    playerstatdict["oversbowled"]=overs
					    if(i==4):
						    runs=int(result.strip())
						    playerstatdict["runsgiven"]=runs
					    if(i==7):
						    dots=int(result.strip()) 
						    playerstatdict["dotsbowled"]=dots
					    
			    #print"  BATSCORE:",batScore
			    print ""
			    if name in player_dict:
				    player_dict[name]=player_dict[name]+bowlScore
			    else:
				    player_dict[name]=bowlScore
			    print name, "BOWL,", bowlScore
			    
			    if name in all_stats:
				    all_stats[name]["oversbowled"]=playerstatdict["oversbowled"]
				    all_stats[name]["maidenovers"]=playerstatdict["maidenovers"]
				    all_stats[name]["runsgiven"]=playerstatdict["runsgiven"]
				    all_stats[name]["wickets"]=playerstatdict["wickets"]
				    all_stats[name]["dotsbowled"]=playerstatdict["dotsbowled"]
			    else:
				    all_stats[name]=playerstatdict
	except Exception as e:
	    error=e
	return [all_stats,fielding_stats,error]
	    
#print player_dict
print score_data('http://www.espncricinfo.com/carlton-mid-triangular-series-2015/engine/match/754751.html')
#print all_stats
#print fielding_stats
#print rows[1].findAll("td")
#print bat_table
#print parsed_html
