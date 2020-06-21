import json
listy=[{"steamid":0,"gameid":'NULL',"playtime":'NULL',"expense":0,"state":'NULL',"city":'NULL',"coordinates":'NULL'}]
with open('appinfo.json','r') as f:
	appinfo = json.load(f)
with open('updated.json','r') as f:
	for d in f:
		data1=d.replace('\n','')
		data2 = data1.split(',')
		price=0
		for i in appinfo:
			if i['appid'] == int(data2[1]):
				price += i['Price']
		if data2[0] == listy[-1]['steamid']:
			x = listy[-1]['gameid']
			y = listy[-1]['playtime']
			z = listy[-1]['expense']
			x = x + "," + data2[1]
			y = y + "," + data2[3]
			z = z + price
			listy[-1]['gameid'] = x
			listy[-1]['playtime'] = y
			listy[-1]['expense'] = z
			print(listy[-1])

		else:	 
			dicty= dict(steamid=data2[0],gameid=data2[1],playtime=data2[3],expense=price,state=data2[6],city=data2[8],coordinates=data2[9])
			listy.append(dicty)
			print(dicty)
with open('final.json','w') as fp:
	json.dump(listy,fp)