import requests
import time
from BeautifulSoup import BeautifulSoup
import re
import pickle
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from time import sleep
import sys

""" HANDLES THE DISMISSAL DETAILS -- INCLUDING THE TYPE OF DISMISSAL AND THE PERPETRATORS"""

fielding_stats={}

def dismissal_handler(how_out):
	other=""
	bowler=""
	fieldingstat={"catches":0, "stumpings":0, "runouts":0}
	if(re.match('c.*b.*',how_out)):  #CATCH OUT
		left="c "
		right=" b "
		other = re.search('%s(.*)%s' % (left, right), how_out).group(1)
		left="b "
		bowler = re.search('%s(.*)' % (left), how_out).group(1)
		#print "CAUGHT ", other, bowler
		fieldingstat["catches"]=1
		other=other.strip()
		if other in fielding_stats:
			fielding_stats[other]["catches"]+=1
		else:
			fielding_stats[other]=fieldingstat
	if(re.match('lbw b.*',how_out)): #LEG BEFORE WICKET
		left="lbw b "
		bowler=re.search('%s(.*)' % (left), how_out).group(1)
		##print "LBW ",bowler
	if(re.match('b.*',how_out)): #BOWLED
		left="b "
		bowler=re.search('%s(.*)' % (left), how_out).group(1)
		#print "BOWLED ",bowler
	if(re.match('c & b .*',how_out)): #CAUGHT AND BOWLED
		left="c & b "
		bowler=re.search('%s(.*)' % (left), how_out).group(1)
		#print "CAUGHT+BOWLED ",bowler
		bowler=bowler.strip()
		fieldingstat["catches"]=1
		if bowler in fielding_stats:
			fielding_stats[bowler]["catches"]+=1
		else:
			fielding_stats[other]=fieldingstat
	if(re.match('st.*b.*',how_out)): #STUMPED
		left="st "
		right=" b "
		other = re.search('%s(.*)%s' % (left, right), how_out).group(1)
		left="b "
		fieldingstat["stumpings"]=1
		bowler = re.search('%s(.*)' % (left), how_out).group(1)
		#print "STUMPED ", other, bowler
		if other in fielding_stats:
			fielding_stats[other]["stumpings"]+=1
		else:
			fielding_stats[other]=fieldingstat
	if(re.match('run out.*',how_out)): #RUN OUT
		left="run out ("
		right=")"
		thrower = re.search('%s(.*)%s' % (left, right), how_out).group(1)
		#print thrower
		thrower=thrower.strip()
		thrower=thrower[1:len(thrower)-1]
		t=thrower.split('/')
		bowler=t[0].strip()
		fieldingstat["runouts"]=1
		if bowler in fielding_stats:
			fielding_stats[bowler]["runouts"]+=1
		else:
			fielding_stats[bowler]=fieldingstat
		##print t[0]
		if(len(t)==2):
			#print "RO2!"
			other=t[1].strip()
			##print other
		fieldingstat["runouts"]=1
		if other in fielding_stats:
			fielding_stats[other]["runouts"]+=1
		else:
			fielding_stats[other]=fieldingstat
		##print "RUN OUT",t[0],t[1]
	
	if(how_out.strip()=="not out"): #NOT OUT
		print "NOT OUT"
		
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
			
def scorecard_getter(URL):
	base_url = URL
	player_dict={"Ian Bell":0}
	html = crawl(base_url)
	print "Page crawled."
	parsed_html = BeautifulSoup(html)
	
	all_stats={} # STORES *ALL* THE STATS OF *ALL* THE PLAYERS INVOLVED IN THE MATCH
		
	bat_table=parsed_html.findAll("table",{ "class" : "batting-table innings" })
	
	for table in bat_table:
		rows=table.findAll("tr",{"class":None})
		
		# BATTING TABLE PARSER FOR BOTH INNINGS
		
		for row in rows:
			playerstatdict={"runsmade":0, "wickets":0, "ballsfaced":0, "fours":0, "sixes":0, "oversbowled":0, "maidenovers":0, "runsgiven":0, "dotsbowled":0, "mom":0, "dnb":0, "funscore":0, "catches":0, "stumpings":0, "runouts":0}
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
					right="<"
					#print "I IS ",i
					#print fields[i]
					result = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)
					#print result,
					if(i==2):
						dismissal_handler(result)
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
			#print ""
			if name in player_dict:
				player_dict[name]=player_dict[name]+batScore
			else:
				player_dict[name]=batScore
			#print name, "BAT,", batScore
		
			all_stats[name]=playerstatdict
			all_stats[name]["funscore"]+=batScore
	bowl_table=parsed_html.findAll("table",{ "class" : "bowling-table" })
	for table in bowl_table:
		rows=table.findAll("tr",{"class":None})
		
		# BOWLING TABLE PARSER FOR BOTH INNINGS
		
		for row in rows:
			playerstatdict={"runsmade":0, "wickets":0, "ballsfaced":0, "fours":0, "sixes":0, "oversbowled":0.0, "maidenovers":0, "runsgiven":0, "dotsbowled":0, "mom":0, "dnb":0, "funscore":0, "catches":0, "stumpings":0, "runouts":0}
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
						if(maidens>0):
							bowlScore=bowlScore+maidens*20 #IMPACT SCORE MAIDENS
						playerstatdict["maidenovers"]=maidens
					if(i==5):
						wickets=int(result.strip())
						bowlScore=bowlScore+wickets*20 #WICKETS SCORE
						bowlScore=bowlScore+(wickets-1)*10 #MILESTONE BONUS
						playerstatdict["wickets"]=wickets
					if(i==2):
						overs=float(result.strip()) #PACE BONUS
						ov=int(overs)
						balls=ov*6+int((overs-ov)*10)
						playerstatdict["oversbowled"]=overs
					if(i==4):
						runs=int(result.strip())
						bowlScore=bowlScore+int(1.5*balls-runs)
						#print balls,runs
						playerstatdict["runsgiven"]=runs
					if(i==7):
						dots=int(result.strip()) #IMPACT SCORE DOTS
						bowlScore=bowlScore+dots
						playerstatdict["dotsbowled"]=dots
					
			#print"  BATSCORE:",batScore
			#print ""
			if name in player_dict:
				player_dict[name]=player_dict[name]+bowlScore
			else:
				player_dict[name]=bowlScore
			#print name, "BOWL,", bowlScore
			
			if name in all_stats:
				all_stats[name]["oversbowled"]=playerstatdict["oversbowled"]
				all_stats[name]["maidenovers"]=playerstatdict["maidenovers"]
				all_stats[name]["runsgiven"]=playerstatdict["runsgiven"]
				all_stats[name]["wickets"]=playerstatdict["wickets"]
				all_stats[name]["dotsbowled"]=playerstatdict["dotsbowled"]
			else:
				all_stats[name]=playerstatdict
			all_stats[name]["funscore"]+=bowlScore
			
	#print player_dict
	#print "\n \n \n"
	dnblist=[]
	did_not_bat=parsed_html.findAll("div",{ "class" : "to-bat" })
	for innings in did_not_bat:
		lst=innings.findAll("span",{"class":"bold"})
		for plyr in lst:
			left="view the player profile for "
			right="\" "
			name = re.search('%s(.*)%s' % (left, right), str(plyr)).group(1)
			dnblist.append(name)
	print dnblist
	tbl=parsed_html.find("div",{ "class" : "match-information" })
	stts=tbl.findAll("div",{ "class" : "bold space-top-bottom-10"})
	momstr=str(stts[1])
	momstr=momstr.replace("\n"," ")
	#print momstr
	left="match   - <span class=\"normal\">"
	right="</span>"
	result = re.search('%s(.*)%s' % (left, right), momstr).group(0)
	left=">"
	right="<"
	result = re.search('%s(.*)%s' % (left, right), result).group(0)
	result=result[1:len(result)-1]
	#print result
	name=result.split(" ")
	mom_name=name[0]+name[1]
	#print mom_name
	
	
	# DNB AND MOM MODIFIER #
	for player in all_stats:
		if(all_stats[player]["ballsfaced"]==0):
			all_stats[player]["dnb"]=1
	print process.extractOne(mom_name,all_stats.keys())[0]
	all_stats[process.extractOne(mom_name,all_stats.keys())[0]]["mom"]=1
	
	#print all_stats
	#print fielding_stats
	
	print "-------TESTING--------"
	for player in fielding_stats:
		match=process.extractOne(player,all_stats.keys())
		if(match[1]==0): # DUMMY ROW
			continue
		print player,"!"
		matchstr=""
		# DEALING WITH THE KEEPER AND HIS BULLSHIT SYMBOL
		if(player[0].isalnum()==0):
			ctr=0
			for a in player:
				if(a==';'):
					matchstr=player[ctr+1:]
				ctr+=1
		# DEALING WITH SUBSTITUTES WHO SHOW UP ON THE PITCH AT RANDOM
		elif(player[0:3]=="sub"):
			continue
		else:
			matchstr=player
		print matchstr
		matchArr = process.extract(matchstr,all_stats.keys(),limit=2)
		ml=len(matchArr)
		if( matchArr[0][1]-matchArr[1][1]<=2 & ml==2 & len(matchstr)==2 ):
			print "Too close for comfort!"
			if(matchArr[0][0][0]==matchstr[1]):
				match=matchArr[0]
			elif(matchArr[1][0][0]==matchstr[1]):
				match=matchArr[1]
			print match
		else:
			match=matchArr[0]
		print matchstr,match
		if(match[1]>65): #CORRECT MATCH
			all_stats[match[0]]["catches"]=fielding_stats[player]["catches"]
			all_stats[match[0]]["stumpings"]=fielding_stats[player]["stumpings"]
			all_stats[match[0]]["runouts"]=fielding_stats[player]["runouts"]
		if(match[1]>10 and match[1]<65):
			matchArr = process.extract(matchstr,dnblist,limit=2)
			ml=len(matchArr)
			if( matchArr[0][1]-matchArr[1][1]<=2 & ml==2 & len(matchstr)==2 ):
				print "Too close for comfort!"
				if(matchArr[0][0][0]==matchstr[1]):
					match=matchArr[0]
				elif(matchArr[1][0][0]==matchstr[1]):
					match=matchArr[1]
				print match
			else:
				match=matchArr[0]
			matchstr=match[0]
			playerstatdict={"runsmade":0, "wickets":0, "ballsfaced":0, "fours":0, "sixes":0, "oversbowled":0.0, "maidenovers":0, "runsgiven":0, "dotsbowled":0, "mom":0, "dnb":0, "funscore":0, "catches":0, "stumpings":0, "runouts":0}
			all_stats[matchstr]=playerstatdict
			all_stats[matchstr]["catches"]=fielding_stats[player]["catches"]
			all_stats[matchstr]["stumpings"]=fielding_stats[player]["stumpings"]
			all_stats[matchstr]["runouts"]=fielding_stats[player]["runouts"]
			
	for x in all_stats:
	    all_stats[x]["funscore"]+= all_stats[x]["catches"]*10+all_stats[x]["stumpings"]*15+all_stats[x]["runouts"]*10
	all_stats.pop("&amp;",None)
	return all_stats
	#print "Man Of The Match: ",name
	#print name
	#print rows[1].findAll("td")
	#print bat_table
	#print parsed_html
	
MatchFinalStats=scorecard_getter(sys.argv[1])
print "\n\n\n\n\n\n"
for name in MatchFinalStats:
	print name," : ",MatchFinalStats[name]["funscore"]