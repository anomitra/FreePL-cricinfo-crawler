{"changed":true,"filter":false,"title":"scoresheet_generator.py","tooltip":"/scoresheet_generator.py","value":"import requests\nimport time\nfrom BeautifulSoup import BeautifulSoup\nimport re\nimport pickle\nfrom time import sleep\n\n\"\"\" HANDLES THE DISMISSAL DETAILS -- INCLUDING THE TYPE OF DISMISSAL AND THE PERPETRATORS\"\"\"\n\nfielding_stats={}\n\ndef dismissal_handler(how_out):\n\tother=\"\"\n\tbowler=\"\"\n\tfieldingstat={\"catches\":0, \"stumpings\":0, \"runouts\":0}\n\tif(re.match('c.*b.*',how_out)):  #CATCH OUT\n\t\tleft=\"c \"\n\t\tright=\" b \"\n\t\tother = re.search('%s(.*)%s' % (left, right), how_out).group(1)\n\t\tleft=\"b \"\n\t\tbowler = re.search('%s(.*)' % (left), how_out).group(1)\n\t\tprint \"CAUGHT \", other, bowler\n\t\tfieldingstat[\"catches\"]=1\n\t\tother=other.strip()\n\t\tif other in fielding_stats:\n\t\t\tfielding_stats[other][\"catches\"]+=1\n\t\telse:\n\t\t\tfielding_stats[other]=fieldingstat\n\tif(re.match('lbw b.*',how_out)): #LEG BEFORE WICKET\n\t\tleft=\"lbw b \"\n\t\tbowler=re.search('%s(.*)' % (left), how_out).group(1)\n\t\tprint \"LBW \",bowler\n\tif(re.match('b.*',how_out)): #BOWLED\n\t\tleft=\"b \"\n\t\tbowler=re.search('%s(.*)' % (left), how_out).group(1)\n\t\tprint \"BOWLED \",bowler\n\tif(re.match('c & b .*',how_out)): #CAUGHT AND BOWLED\n\t\tleft=\"c & b \"\n\t\tbowler=re.search('%s(.*)' % (left), how_out).group(1)\n\t\tprint \"CAUGHT+BOWLED \",bowler\n\t\tbowler=bowler.strip()\n\t\tfieldingstat[\"catches\"]=1\n\t\tif bowler in fielding_stats:\n\t\t\tfielding_stats[bowler][\"catches\"]+=1\n\t\telse:\n\t\t\tfielding_stats[other]=fieldingstat\n\tif(re.match('st.*b.*',how_out)): #STUMPED\n\t\tleft=\"st \"\n\t\tright=\" b \"\n\t\tother = re.search('%s(.*)%s' % (left, right), how_out).group(1)\n\t\tleft=\"b \"\n\t\tfieldingstat[\"stumpings\"]=1\n\t\tbowler = re.search('%s(.*)' % (left), how_out).group(1)\n\t\tprint \"STUMPED \", other, bowler\n\t\tif other in fielding_stats:\n\t\t\tfielding_stats[other][\"stumpings\"]+=1\n\t\telse:\n\t\t\tfielding_stats[other]=fieldingstat\n\tif(re.match('run out.*',how_out)): #RUN OUT\n\t\tleft=\"run out (\"\n\t\tright=\")\"\n\t\tthrower = re.search('%s(.*)%s' % (left, right), how_out).group(1)\n\t\t#print thrower\n\t\tthrower=thrower.strip()\n\t\tthrower=thrower[1:len(thrower)-1]\n\t\tt=thrower.split('/')\n\t\tbowler=t[0].strip()\n\t\tfieldingstat[\"runouts\"]=1\n\t\tif bowler in fielding_stats:\n\t\t\tfielding_stats[bowler][\"runouts\"]+=1\n\t\telse:\n\t\t\tfielding_stats[bowler]=fieldingstat\n\t\t#print t[0]\n\t\tif(len(t)==2):\n\t\t\tother=t[1].strip()\n\t\t\t#print other\n\t\tfieldingstat[\"runouts\"]=1\n\t\tif other in fielding_stats:\n\t\t\tfielding_stats[other][\"runouts\"]+=1\n\t\telse:\n\t\t\tfielding_stats[other]=fieldingstat\n\t\t#print \"RUN OUT\",t[0],t[1]\n\t\n\tif(how_out.strip()==\"not out\"): #NOT OUT\n\t\tprint \"NOT OUT\"\n\t\t\n\"\"\" CRAWLS AN URL \"\"\"\n\ndef crawl(url):\n\twhile True:\n\t\ttry:\n\t\t\tprint \"trying to get URL... \",\n\t\t\tr=requests.get(url)\n\t\t\tprint \"Got URL!\"\n\t\t\treturn r.content\n\t\texcept Exception as e:\n\t\t\tprint e\n\t\t\tsleep(2)\n\t\t\tprint \"Retrying!!\"\n\nbase_url = 'http://www.espncricinfo.com/carlton-mid-triangular-series-2015/engine/match/754751.html'\nplayer_dict={\"Ian Bell\":0}\nhtml = crawl(base_url)\nprint \"Page crawled.\"\nparsed_html = BeautifulSoup(html)\n\nall_stats={} # STORES *ALL* THE STATS OF *ALL* THE PLAYERS INVOLVED IN THE MATCH\n\t\nbat_table=parsed_html.findAll(\"table\",{ \"class\" : \"batting-table innings\" })\n\nfor table in bat_table:\n\trows=table.findAll(\"tr\",{\"class\":None})\n\t\n\t# BATTING TABLE PARSER FOR BOTH INNINGS\n\t\n\tfor row in rows:\n\t\tplayerstatdict={\"runsmade\":0, \"wickets\":0, \"ballsfaced\":0, \"fours\":0, \"sixes\":0, \"oversbowled\":0, \"maidenovers\":0, \"runsgiven\":0, \"dotsbowled\":0, \"mom\":0, \"dnb\":0, \"funscore\":0}\n\t\tname=\"\"\n\t\tbatScore=0\n\t\truns=0\n\t\tfields=row.findAll(\"td\")\n\t\tfor i in range(0,8):\n\t\t\tif(i==1):\n\t\t\t\tleft=\"view the player profile for \"\n\t\t\t\tright=\"\\\" \"\n\t\t\t\tname = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)\n\t\t\tif(i>=2 and i<=8):\n\t\t\t\tleft=\">\"\n\t\t\t\tright=\"</td>\"\n\t\t\t\tresult = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)\n\t\t\t\t#print result,\n\t\t\t\tif(i==2):\n\t\t\t\t\tdismissal_handler(result)\n\t\t\t\tif(i==3):\n\t\t\t\t\truns=int(result.strip())\n\t\t\t\t\tif(runs==0):\n\t\t\t\t\t\tbatScore=batScore-5 #IMPACT DUCK\n\t\t\t\t\tbatScore=batScore+runs #RUNS SCORE\n\t\t\t\t\tplayerstatdict[\"runsmade\"]=runs\n\t\t\t\t\tbatScore=batScore+(runs/25)*10 #MILESTONE BONUS\n\t\t\t\tif(i==5):\n\t\t\t\t\tbatScore=batScore+runs-int(result.strip()) #PACE BONUS\n\t\t\t\t\tplayerstatdict[\"ballsfaced\"]=int(result.strip())\n\t\t\t\tif(i==6):\n\t\t\t\t\tplayerstatdict[\"fours\"]=int(result.strip())\n\t\t\t\tif(i==7):\n\t\t\t\t\tbatScore=batScore+int(result.strip())*2 #IMPACT SIXES\n\t\t\t\t\tplayerstatdict[\"sixes\"]=int(result.strip())\n\t\t#print\"  BATSCORE:\",batScore\n\t\tprint \"\"\n\t\tif name in player_dict:\n\t\t\tplayer_dict[name]=player_dict[name]+batScore\n\t\telse:\n\t\t\tplayer_dict[name]=batScore\n\t\t#print name, \"BAT,\", batScore\n\t\n\t\tall_stats[name]=playerstatdict\nbowl_table=parsed_html.findAll(\"table\",{ \"class\" : \"bowling-table\" })\nfor table in bowl_table:\n\trows=table.findAll(\"tr\",{\"class\":None})\n\t\n\t# BOWLING TABLE PARSER FOR BOTH INNINGS\n\t\n\tfor row in rows:\n\t\tplayerstatdict={\"runsmade\":0, \"wickets\":0, \"ballsfaced\":0, \"fours\":0, \"sixes\":0, \"oversbowled\":0.0, \"maidenovers\":0, \"runsgiven\":0, \"dotsbowled\":0, \"mom\":0, \"dnb\":0, \"funscore\":0}\n\t\tname=\"\"\n\t\tbowlScore=0\n\t\tballs=0\n\t\tfields=row.findAll(\"td\")\n\t\tfor i in range(0,10):\n\t\t\tif(i==1):\n\t\t\t\tleft=\"view the player profile for \"\n\t\t\t\tright=\"\\\" \"\n\t\t\t\t#print  name,\n\t\t\t\tname = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)\n\t\t\tif(i>=2 and i<=10):\n\t\t\t\tleft=\">\"\n\t\t\t\tright=\"</td>\"\n\t\t\t\tresult = re.search('%s(.*)%s' % (left, right), str(fields[i])).group(1)\n\t\t\t\t#print result,\n\t\t\t\tif(i==3):\n\t\t\t\t\tmaidens=int(result.strip())\n\t\t\t\t\tif(maidens>0):\n\t\t\t\t\t\tbowlScore=bowlScore+maidens*20 #IMPACT SCORE MAIDENS\n\t\t\t\t\tplayerstatdict[\"maidenovers\"]=maidens\n\t\t\t\tif(i==5):\n\t\t\t\t\twickets=int(result.strip())\n\t\t\t\t\tbowlScore=bowlScore+wickets*20 #WICKETS SCORE\n\t\t\t\t\tbowlScore=bowlScore+(wickets-1)*10 #MILESTONE BONUS\n\t\t\t\t\tplayerstatdict[\"wickets\"]=wickets\n\t\t\t\tif(i==2):\n\t\t\t\t\tovers=float(result.strip()) #PACE BONUS\n\t\t\t\t\tov=int(overs)\n\t\t\t\t\tballs=ov*6+int((overs-ov)*10)\n\t\t\t\t\tplayerstatdict[\"oversbowled\"]=overs\n\t\t\t\tif(i==4):\n\t\t\t\t\truns=int(result.strip())\n\t\t\t\t\tbowlScore=bowlScore+int(1.5*balls-runs)\n\t\t\t\t\t#print balls,runs\n\t\t\t\t\tplayerstatdict[\"runsgiven\"]=runs\n\t\t\t\tif(i==7):\n\t\t\t\t\tdots=int(result.strip()) #IMPACT SCORE DOTS\n\t\t\t\t\tbowlScore=bowlScore+dots\n\t\t\t\t\tplayerstatdict[\"dotsbowled\"]=dots\n\t\t\t\t\n\t\t#print\"  BATSCORE:\",batScore\n\t\tprint \"\"\n\t\tif name in player_dict:\n\t\t\tplayer_dict[name]=player_dict[name]+bowlScore\n\t\telse:\n\t\t\tplayer_dict[name]=bowlScore\n\t\tprint name, \"BOWL,\", bowlScore\n\t\t\n\t\tif name in all_stats:\n\t\t\tall_stats[name][\"oversbowled\"]=playerstatdict[\"oversbowled\"]\n\t\t\tall_stats[name][\"maidenovers\"]=playerstatdict[\"maidenovers\"]\n\t\t\tall_stats[name][\"runsgiven\"]=playerstatdict[\"runsgiven\"]\n\t\t\tall_stats[name][\"wickets\"]=playerstatdict[\"wickets\"]\n\t\t\tall_stats[name][\"dotsbowled\"]=playerstatdict[\"dotsbowled\"]\n\t\telse:\n\t\t\tall_stats[name]=playerstatdict\n\t\t\n\t\t\n#print player_dict\nprint \"\\n \\n \\n\"\n\n# DNB MODIFIER #\nfor player in all_stats:\n\tif(player[\"ballsfaced\"]==0):\n\t\tplayer[\"dnb\"]=1\n\nprint all_stats\nprint fielding_stats\n#print rows[1].findAll(\"td\")\n#print bat_table\n#print parsed_html\n","undoManager":{"mark":-20,"position":100,"stack":[[{"group":"doc","deltas":[{"start":{"row":227,"column":14},"end":{"row":227,"column":17},"action":"remove","lines":["all"]},{"start":{"row":227,"column":14},"end":{"row":227,"column":23},"action":"insert","lines":["all_stats"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":23},"end":{"row":227,"column":24},"action":"insert","lines":[":"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":24},"end":{"row":228,"column":0},"action":"insert","lines":["",""]},{"start":{"row":228,"column":0},"end":{"row":228,"column":1},"action":"insert","lines":["\t"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":1},"end":{"row":228,"column":2},"action":"insert","lines":["i"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":2},"end":{"row":228,"column":3},"action":"insert","lines":["f"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":3},"end":{"row":228,"column":4},"action":"insert","lines":["("]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":3},"end":{"row":228,"column":4},"action":"remove","lines":["("]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":3},"end":{"row":228,"column":4},"action":"insert","lines":["("]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":4},"end":{"row":228,"column":5},"action":"insert","lines":["p"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":5},"end":{"row":228,"column":6},"action":"insert","lines":["l"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":6},"end":{"row":228,"column":7},"action":"insert","lines":["a"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":7},"end":{"row":228,"column":8},"action":"insert","lines":["y"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":8},"end":{"row":228,"column":9},"action":"insert","lines":["e"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":9},"end":{"row":228,"column":10},"action":"insert","lines":["r"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":10},"end":{"row":228,"column":11},"action":"insert","lines":["["]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":11},"end":{"row":228,"column":12},"action":"insert","lines":["\""]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":12},"end":{"row":228,"column":13},"action":"insert","lines":["b"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":13},"end":{"row":228,"column":14},"action":"insert","lines":["l"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":13},"end":{"row":228,"column":14},"action":"remove","lines":["l"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":13},"end":{"row":228,"column":14},"action":"insert","lines":["a"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":14},"end":{"row":228,"column":15},"action":"insert","lines":["l"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":15},"end":{"row":228,"column":16},"action":"insert","lines":["l"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":16},"end":{"row":228,"column":17},"action":"insert","lines":["s"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":12},"end":{"row":228,"column":17},"action":"remove","lines":["balls"]},{"start":{"row":228,"column":12},"end":{"row":228,"column":22},"action":"insert","lines":["ballsfaced"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":22},"end":{"row":228,"column":23},"action":"insert","lines":["\""]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":23},"end":{"row":228,"column":24},"action":"insert","lines":["]"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":24},"end":{"row":228,"column":25},"action":"insert","lines":[" "]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":25},"end":{"row":228,"column":26},"action":"insert","lines":["e"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":26},"end":{"row":228,"column":27},"action":"insert","lines":["q"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":27},"end":{"row":228,"column":28},"action":"insert","lines":["u"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":28},"end":{"row":228,"column":29},"action":"insert","lines":["a"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":29},"end":{"row":228,"column":30},"action":"insert","lines":["l"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":30},"end":{"row":228,"column":31},"action":"insert","lines":["s"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":31},"end":{"row":228,"column":32},"action":"insert","lines":[" "]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":31},"end":{"row":228,"column":32},"action":"remove","lines":[" "]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":30},"end":{"row":228,"column":31},"action":"remove","lines":["s"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":29},"end":{"row":228,"column":30},"action":"remove","lines":["l"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":28},"end":{"row":228,"column":29},"action":"remove","lines":["a"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":27},"end":{"row":228,"column":28},"action":"remove","lines":["u"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":26},"end":{"row":228,"column":27},"action":"remove","lines":["q"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":25},"end":{"row":228,"column":26},"action":"remove","lines":["e"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":24},"end":{"row":228,"column":25},"action":"remove","lines":[" "]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":24},"end":{"row":228,"column":25},"action":"insert","lines":["="]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":25},"end":{"row":228,"column":26},"action":"insert","lines":["="]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":26},"end":{"row":228,"column":27},"action":"insert","lines":[" "]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":26},"end":{"row":228,"column":27},"action":"remove","lines":[" "]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":26},"end":{"row":228,"column":27},"action":"insert","lines":["0"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":27},"end":{"row":228,"column":28},"action":"insert","lines":[")"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":28},"end":{"row":228,"column":29},"action":"insert","lines":[":"]}]}],[{"group":"doc","deltas":[{"start":{"row":228,"column":29},"end":{"row":229,"column":0},"action":"insert","lines":["",""]},{"start":{"row":229,"column":0},"end":{"row":229,"column":2},"action":"insert","lines":["\t\t"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":2},"end":{"row":229,"column":3},"action":"insert","lines":["p"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":3},"end":{"row":229,"column":4},"action":"insert","lines":["l"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":4},"end":{"row":229,"column":5},"action":"insert","lines":["a"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":5},"end":{"row":229,"column":6},"action":"insert","lines":["y"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":6},"end":{"row":229,"column":7},"action":"insert","lines":["e"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":7},"end":{"row":229,"column":8},"action":"insert","lines":["r"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":8},"end":{"row":229,"column":9},"action":"insert","lines":["["]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":9},"end":{"row":229,"column":10},"action":"insert","lines":["\""]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":10},"end":{"row":229,"column":11},"action":"insert","lines":["d"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":11},"end":{"row":229,"column":12},"action":"insert","lines":["n"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":10},"end":{"row":229,"column":12},"action":"remove","lines":["dn"]},{"start":{"row":229,"column":10},"end":{"row":229,"column":13},"action":"insert","lines":["dnb"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":13},"end":{"row":229,"column":14},"action":"insert","lines":["]"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":14},"end":{"row":229,"column":15},"action":"insert","lines":["="]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":15},"end":{"row":229,"column":16},"action":"insert","lines":["1"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":16},"end":{"row":230,"column":0},"action":"insert","lines":["",""]},{"start":{"row":230,"column":0},"end":{"row":230,"column":2},"action":"insert","lines":["\t\t"]}]}],[{"group":"doc","deltas":[{"start":{"row":230,"column":1},"end":{"row":230,"column":2},"action":"remove","lines":["\t"]}]}],[{"group":"doc","deltas":[{"start":{"row":230,"column":0},"end":{"row":230,"column":1},"action":"remove","lines":["\t"]}]}],[{"group":"doc","deltas":[{"start":{"row":226,"column":0},"end":{"row":227,"column":0},"action":"insert","lines":["",""]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":0},"end":{"row":227,"column":1},"action":"insert","lines":["/"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":1},"end":{"row":227,"column":2},"action":"insert","lines":["*"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":2},"end":{"row":227,"column":3},"action":"insert","lines":[" "]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":3},"end":{"row":227,"column":4},"action":"insert","lines":["D"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":4},"end":{"row":227,"column":5},"action":"insert","lines":["N"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":5},"end":{"row":227,"column":6},"action":"insert","lines":["B"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":6},"end":{"row":227,"column":7},"action":"insert","lines":[" "]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":7},"end":{"row":227,"column":8},"action":"insert","lines":["M"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":8},"end":{"row":227,"column":9},"action":"insert","lines":["O"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":9},"end":{"row":227,"column":10},"action":"insert","lines":["D"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":10},"end":{"row":227,"column":11},"action":"insert","lines":["I"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":11},"end":{"row":227,"column":12},"action":"insert","lines":["F"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":12},"end":{"row":227,"column":13},"action":"insert","lines":["I"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":13},"end":{"row":227,"column":14},"action":"insert","lines":["E"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":14},"end":{"row":227,"column":15},"action":"insert","lines":["R"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":15},"end":{"row":227,"column":16},"action":"insert","lines":[" "]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":16},"end":{"row":227,"column":17},"action":"insert","lines":["*"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":17},"end":{"row":227,"column":18},"action":"insert","lines":["/"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":1},"end":{"row":227,"column":2},"action":"remove","lines":["*"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":0},"end":{"row":227,"column":1},"action":"remove","lines":["/"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":0},"end":{"row":227,"column":1},"action":"insert","lines":["#"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":16},"end":{"row":227,"column":17},"action":"remove","lines":["/"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":15},"end":{"row":227,"column":16},"action":"remove","lines":["*"]}]}],[{"group":"doc","deltas":[{"start":{"row":227,"column":15},"end":{"row":227,"column":16},"action":"insert","lines":["#"]}]}],[{"group":"doc","deltas":[{"start":{"row":225,"column":15},"end":{"row":226,"column":0},"action":"remove","lines":["",""]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":13},"end":{"row":229,"column":14},"action":"insert","lines":["\""]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":17},"end":{"row":230,"column":0},"action":"remove","lines":["",""]}]}],[{"group":"doc","deltas":[{"start":{"row":225,"column":0},"end":{"row":225,"column":15},"action":"remove","lines":["print all_stats"]}]}],[{"group":"doc","deltas":[{"start":{"row":229,"column":17},"end":{"row":230,"column":0},"action":"insert","lines":["",""]},{"start":{"row":230,"column":0},"end":{"row":230,"column":2},"action":"insert","lines":["\t\t"]}]}],[{"group":"doc","deltas":[{"start":{"row":230,"column":1},"end":{"row":230,"column":2},"action":"remove","lines":["\t"]}]}],[{"group":"doc","deltas":[{"start":{"row":230,"column":0},"end":{"row":230,"column":1},"action":"remove","lines":["\t"]}]}],[{"group":"doc","deltas":[{"start":{"row":230,"column":0},"end":{"row":231,"column":0},"action":"insert","lines":["",""]}]}],[{"group":"doc","deltas":[{"start":{"row":231,"column":0},"end":{"row":231,"column":15},"action":"insert","lines":["print all_stats"]}]}]]},"ace":{"folds":[],"scrolltop":2504.5,"scrollleft":0,"selection":{"start":{"row":229,"column":17},"end":{"row":229,"column":17},"isBackwards":false},"options":{"guessTabSize":true,"useWrapMode":false,"wrapToView":true},"firstLineState":{"row":177,"state":"start","mode":"ace/mode/python"}},"timestamp":1423674374586}