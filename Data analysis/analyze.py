import json
import matplotlib.pyplot as plt
import numpy as np
states={'ACT':{},'NSW':{},'NT':{},'QLD':{},'SA':{},'TAS':{},'VIC':{},'WA':{},'NULL':{}}

with open('final2.json','r')as f:
	data=json.load(f)
for x in data:
	if x['state'] == 'NULL':
		continue
	else:
		state = states[x['state']]
		city = x['city']
		gameid = x['gameid']
		playtime = x['playtime']
		expense = x['expense']
		state[city] = {'gameid':gameid,'playtime':playtime,'expense':expense}
cities=[]
playtimes = []
gamestates=[]
stateplaytimes=[]
expense = []
allgames=[]
allplays=[]
for x in states:
	for y in states[x]:
		if y =='NULL':
			continue
		else:
			indplaytimes = []
			indgames = []
			cities.append(y)
			expense.append(int(states[x][y]['expense'])*10)
			temp = states[x][y]['playtime'].replace('NULL,','')
			temp2 = states[x][y]['gameid'].replace('NULL','')
			gameids = temp2.split(',')
			playtime = temp.split(',')
			final =0
			for (i,j) in zip(playtime,gameids):
				if i == 'NULL':
					continue
				else:
					indplaytimes.append(int(i))
					indgames.append(j)
					final = final + int(i)
			allgames.append(indgames)
			allplays.append(indplaytimes)
			playtimes.append(final)

plotting=[]
stateexpenses=[]
for x in states:
	totgametime=0
	totexpense =0
	city=[]
	for y in states[x]:
		if y in cities:
			index = cities.index(y)
			city.append(index)
			totgametime = totgametime + playtimes[index]
			totexpense = totexpense + expense[index]
			continue		
	gamestates.append(x)
	stateplaytimes.append(totgametime)
	stateexpenses.append(totexpense)
	plotting.append(city)

gamestates = gamestates[:-1]
stateplaytimes = stateplaytimes[:-1]
plotting = plotting[:-1]
stateexpenses = stateexpenses[:-1]

#print(gamestates)
#print(stateexpenses)
#print(stateplaytimes)
#print(cities)
#print(playtimes)
#print(expense)
#print(allgames)
#print(allplays)

top5allgames=[]
top5allplays=[]
playtimecities=[]
expensecities=[]
playtimes2 = np.array(playtimes)
expense2 = np.array(expense)

ind = np.argpartition(playtimes2,-5)[-5:]
ind2 = np.argpartition(expense2,-5)[-5:]
for (x,y) in zip(ind,ind2):
	playtimecities.append(cities[x])
	expensecities.append(cities[x])
top5playtimes=playtimes2[ind]
top5expense=expense2[ind2]

"""for (i,j) in zip (allgames,allplays):
	if len(i) >= 5:
		ind = np.argpartition(j, -5)[-5:]
		top5allgames.append(i[ind].tolist())
		top5allplays.append(j[ind].tolist())	
	else:
		top5allgames.append(i.tolist())
		top5allplays.append(j.tolist())

print(top5allgames)
print(top5allplays)"""

#print(playtimecities)
#print(top5playtimes)
#print(expensecities)
#print(top5expense)
#print(gamestates)
#print(stateplaytimes)
#print(stateexpenses)
print(allgames)
print(allplays)
citytopgame=[]
citytopplaytime=[]
for (b,a) in zip(allgames,allplays):
	if not a:
		continue
	m=max(a)
	index = [i for i, j in enumerate(a) if j == m]
	citytopplaytime.append(m)
	citytopgame.append(b[index[0]])
print(cities)
print(citytopgame)
print(citytopplaytime)

topcities=[]
topgames=[]
topplaytimes=[]
top5cityplaytimes = np.array(citytopplaytime)
ind = np.argpartition(citytopplaytime,-5)[-5:]
for i in ind:
	topcities.append(cities[i])
	topgames.append(citytopgame[i])
	topplaytimes.append(citytopplaytime[i])

print(topcities)
print(topgames)
print(topplaytimes)


x_pos = [i for i, _ in enumerate(gamestates)]
plt.barh(x_pos,stateplaytimes,color = 'b')
plt.ylabel("States")
plt.xlabel("Playtimes")
plt.title("Game time of States in hours")
plt.yticks(x_pos,gamestates)
plt.xticks(np.arange(0,3000000,500000),('0','500k','1Mil','1.5Mil','2Mil','2.5Mil'))
plt.show()


x_pos = [i for i, _ in enumerate(gamestates)]
plt.barh(x_pos,stateexpenses,color = 'b')
plt.ylabel("States")
plt.xlabel("Amount Spent")
plt.title("Amount each state spends on Games")
plt.yticks(x_pos,gamestates)
plt.xticks(np.arange(0,400000,50000),('0','50k','100k','150k','200k','250k','300k','350k'))
plt.show()


x_pos = [i for i, _ in enumerate(expensecities)]
plt.bar(x_pos,top5expense,color = 'b')
plt.xlabel("Cities")
plt.ylabel("Time spent in hours")
plt.title("Top 5 cities and their most played games")
plt.xticks(x_pos,expensecities)
plt.show()




x_pos = [i for i, _ in enumerate(topcities)]
plt.bar(x_pos,topplaytimes,color = 'b')
plt.xlabel("Cities")
plt.ylabel("Time spent in hours")
plt.title("Top 5 cities and their most played games")
plt.xticks(x_pos,topcities)
plt.show()



with open('schooldrop.json','r',encoding='utf-8') as f:
	data = json.load(f)
sety=data['features']
city=[]
state=[]
dropped=[]
for x in sety:
	city.append(x['properties']['lga_name'])
	dropped.append(x['properties']['no_sch_yr_10_less_1_count'])
	state.append(x['properties']['ste_name'])
#print(state)
#print(city)
#print(dropped)
i1 = [i for i, x in enumerate(state) if x == 'nsw']
i2 = [i for i, x in enumerate(state) if x == 'vic']
i3 = [i for i, x in enumerate(state) if x == 'qld']
i4 = [i for i, x in enumerate(state) if x == 'sa']
i5 = [i for i, x in enumerate(state) if x == 'wa']
i6 = [i for i, x in enumerate(state) if x == 'tas']
i7 = [i for i, x in enumerate(state) if x == 'nt']
finaldropped=[]
finalstate=[]
droppy = 0
for x in i1:
	droppy += dropped[x]
finaldropped.append(droppy)
finalstate.append('NSW')
for x in i7:
	droppy += dropped[x]
finaldropped.append(droppy)
finalstate.append('NT')
for x in i3:
	droppy += dropped[x]
finaldropped.append(droppy)
finalstate.append('QLD')
for x in i4:
	droppy += dropped[x]
finaldropped.append(droppy)
finalstate.append('SA')
for x in i6:
	droppy += dropped[x]
finaldropped.append(droppy)
finalstate.append('TAS')
droppy = 0
for x in i2:
	droppy += dropped[x]
finaldropped.append(droppy)
finalstate.append('VIC')
droppy = 0


for x in i5:
	droppy += dropped[x]
finaldropped.append(droppy)
finalstate.append('WA')

plotstate=gamestates[1:]
plottime = stateplaytimes[1:]
#print(finalstate)
#print(finaldropped)
barWidth = 0.25

r1 = np.arange(len(plottime))
r2 = [x + barWidth for x in r1]
plt.bar(r1, plottime, color='blue', width=barWidth, edgecolor='white', label='Number of People who play games')
plt.bar(r2, finaldropped, color='red', width=barWidth, edgecolor='white', label='Number of people who dropped out of school')
plt.xlabel('States', fontweight='bold')
plt.xticks([r + barWidth for r in range(len(plottime))], ['NSW', 'NT', 'QLD', 'SA', 'TAS','VIC','WA'])
plt.yticks(np.arange(0,4000000,500000),('0','500k','1Mil','1.5Mil','2.5Mil','3Mil','3.5Mil','4Mil'))
plt.legend()
plt.show()



