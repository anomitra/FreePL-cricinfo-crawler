import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

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
		print "CAUGHT ", other, bowler
		fieldingstat["catches"]=1
		other=other.strip()
		if other in fielding_stats:
			fielding_stats[other]["catches"]+=1
		else:
			fielding_stats[other]=fieldingstat
	if(re.match('lbw b.*',how_out)): #LEG BEFORE WICKET
		left="lbw b "
		bowler=re.search('%s(.*)' % (left), how_out).group(1)
		print "LBW ",bowler
	if(re.match('b.*',how_out)): #BOWLED
		left="b "
		bowler=re.search('%s(.*)' % (left), how_out).group(1)
		print "BOWLED ",bowler
	if(re.match('c & b .*',how_out)): #CAUGHT AND BOWLED
		left="c & b "
		bowler=re.search('%s(.*)' % (left), how_out).group(1)
		print "CAUGHT+BOWLED ",bowler
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
		print "STUMPED ", other, bowler
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
		#print t[0]
		if(len(t)==2):
			other=t[1].strip()
			#print other
		fieldingstat["runouts"]=1
		if other in fielding_stats:
			fielding_stats[other]["runouts"]+=1
		else:
			fielding_stats[other]=fieldingstat
		#print "RUN OUT",t[0],t[1]
	
	if(how_out.strip()=="not out"): #NOT OUT
		print "NOT OUT"

dismissal_handler("run out (Bopara/Jordan)")
lst=['Steven Smith', 'Brendan McCullum', 'Nathan McCullum', 'Rohan Sharma', 'Jos Buttler', 'Eoin Morgan', 'Mitchell Starc', 'Ravi Bopara', 'James Faulkner', 'Chris Woakes', 'David Warner', 'Moeen Ali', 'Pat Cummins', 'Joe Root', 'Xavier Doherty', 'Glenn Maxwell', 'Ian Bell', 'Aaron Finch', 'Steven Finn', 'George Bailey', 'Chris Jordan', 'Shane Watson']
print process.extractOne("Langeveldt",lst)