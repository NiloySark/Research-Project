import json
count = 0
data=[]
with open('Aus.json','r',encoding = 'utf-8') as f:
		citydata = json.load(f)

updated = open ("updated.json",'w') 
states = citydata["states"]
with open('games1.json','r',encoding = 'utf-8') as f:
	next(f)
	for d in f:		
		data1=d.replace('\n','')		
		data2 = data1.split(',')
		city_id = data2[7]
		if city_id == 'NULL':
			data1 = data1 +",NULL,NULL"
			print(data1)
			updated.write(data1)
			updated.write("\n")
		for y in states:
			cities = states[y]['cities']
			if city_id in cities:
				citydetails = cities[city_id]
				
				data1 = data1 + ","+citydetails['name']+","+citydetails['coordinates']
				updated.write(data1)
				updated.write("\n")
				print(data1)