'''
| product | date |  clientFactor | quotedPrice | competitorPrice | ProductQuality (ratings, ) | productMarketState | costPrice | didSell | profit | p

Date | sectorial inflation index 
'''

#date to be represented by integer 


'''
Demmand distribution
	* WeekDay | Demand Ratio 
	* Month | Demand Ratio
Conversion Probability
	* Strategic Customer
		CompetionPrice Ratio | CompetitionQualityRatio | Probability 
	* Mayopic Customer
		Price | Inflationfactor | Probability 
Recent demand rate
	* ClientType | Request

Sales Objective:
	* 3000/month = 100 daily = or volume weighted distribution
Data Objective:
	*

average 
| product | period | clientType     | salePrice | item
p1          today    s1-south-asia    30          5
p1          today    s1-south-asia    29          7
p1          today    s1-south-asia    28          7

'''

import datetime
import csv
import random

def r():
	return random.random();

def findDate():
	pass;

def genCount(date):
	count = 50*int(
		10 + 
		(date.weekday()*r()+2)*5 + 
		int(date.month in (1,11,12))*r()*10 + 
		int(date.month in (2,4,10))*r()*5 + 
		r()*5
	)
	return count;

def genMayopiaFator():
	'''Most of the clients are not mayopic'''
	return round(1000*random.random()**16)/1000;

def genGompetionPrice():
	return round(max(random.gauss(1, 0.01), 0.98)*500);

def genQuotedPrice():
	return 500*(0.9+0.2*random.random());

data = [];


monthOrder = {};
monthSales = {};
weekdayOrder = {};
weekdaySakes = {};
myopiaSales = {};

baseDay = datetime.date.fromisoformat('2021-01-01').toordinal();
for d in range(365):
	date = datetime.date.fromordinal(baseDay+d)
	count = genCount(date);
	for x in range(count):
		cMyopiaFactor = genMayopiaFator();
		quotedPrice = genQuotedPrice()
		competionPrice = genGompetionPrice();
		ran = r();
		sold =  (max(cMyopiaFactor,0.1) * competionPrice / quotedPrice * ran ) > 0.1;
		#print( max(cMyopiaFactor,0.1) , competionPrice, quotedPrice, ran, max(cMyopiaFactor,0.1) * competionPrice / quotedPrice * ran, "\n")
		data.append([
			date.isoformat(),
			date.month,
			date.weekday(),
			cMyopiaFactor,
			quotedPrice, 
			competionPrice, 
			sold,
			ran
		]);

#C:\Users\Himanshu\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\Scripts

with open('eggs.csv', 'w', newline='') as csvfile:
	#writwe = csv.writer(csvfile, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	#writer
	csvfile.write("date,month,weekday,myopia,quotedPrice,competionPrice,sold,luck")
	for d in data:
		ds = [str(x) for x in d]
		csvfile.write('\n'+','.join(ds))
