import datetime
import csv
import random
import config_test
import os.path
import json


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


def dataFile(test_name, variaton):
	return ("./hist_data/" + test_name + "-" + variaton);

def generateIfNotThere(test_name, variaton, test_config):
	filename = dataFile(test_name, variaton)
	if(os.path.isfile(filename)): #nothing to do
		print("Data file already present [" + filename + "], not simulating a new one")
		return; 

	total_req = test_config.requests_history.adv*365;
	mdata = test_config.requests_history.months
	wdata = test_config.requests_history.weekdays
	sum_month = 1.0*sum(mdata)
	sum_weeks = 1.0*sum(wdata)
	
	baseDay = datetime.date.fromisoformat('2021-01-01').toordinal();
	all_data = []
	for d in range(365):
		date = datetime.date.fromordinal(baseDay+d)
		mi = date.month-1
		wi = date.weekday()
		req_to_gen = 1.0*total_req*(mdata[mi]/sum_month)*(wdata[wi]/sum_weeks)/(365/(12*7))
		req_to_gen = int( req_to_gen * random.gauss(1, test_config.requests_history.sigma) )
		mratio = test_config.customer_base.myopic_percentage*random.gauss(1,test_config.customer_base.sigma)
		for r in range(req_to_gen):
			#date, is_myopic, is_scouting, can_go_upto_price, price_offered
			ctype = 'm' if random.random() < mratio else 's'
			if ctype == 'm':
				ci = test_config.customer_base.myopic_info
				is_scouting = random.random() < ci.scoute_percentage/100.0
				can_go_upto_price = 10*round(ci.cental_price*(0.85 + random.random())/10)
				offered_price =  10*round(ci.cental_price*(0.75 + random.random()/2)/10)  #-- 0.75 -- 1.25
			else:
				ci = test_config.customer_base.strategic_info
				is_scouting = random.random() < ci.scoute_percentage/100.0	
				can_go_upto_price = round(ci.competition_price*(0.95 + random.random()/10))
				offered_price =  round(ci.competition_price*(0.9 + (random.random()*2)/10))  #-- 0.8 -- 1.2
			all_data.append({'date':baseDay+d, 'ctype': ctype, 'scout': is_scouting, 'cust_price': can_go_upto_price, 'offer': offered_price })

	res = {'data': all_data}
	with open(filename, 'w', encoding='utf8') as outfile:
		str_ = json.dumps(res, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
		outfile.write(str_)
	return res;

def load(test_name, variaton, test_config):
	generateIfNotThere(test_name, variaton, test_config)
	filename = dataFile(test_name, variaton)
	with open(filename, 'r') as fp:
		data = json.load(fp)
	return data;

	