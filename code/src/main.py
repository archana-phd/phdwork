import datetime
import csv
import random
import sys
import config_test
import history_data
import json
#import pricer
import copy
import lp_solve

#python -i main.py test_basic 1

def main(test_name, variation):
	print("Running test :" + test + "," + variation) 

	test_config = config_test.getTest(test_name)
	print(test_config)

	'''
	print("##----Generating historical data ---- ##");
	history_data.generateIfNotThere(test_name, variaton, test_config)

	[sp_myopic, sp_strategic] = sp_module.calculate(test_name, variaton)

	print("##----Generating/Locating historical data ----- ##");
	daily_target_slices = vwat.make_targets_slice(test_config)

	print("##----Solving LP and conducting experiments --- ##");
	for daily_target in daily_target_slices:
		prices_vector = pricer.calculate(daily_target, expected_num_requests, test_config.myopic_percentage, sp_myopic, sp_strategic);			

		real_requests = de_sim.getNumberOfRequests; 
		for i in range(real_requests):
			offered_price = pricer.getPriceFromVector( )
	'''

####### Script Startup: Argv processing and run #########
if(len(sys.argv) < 2):
	print(sys.argv[0] + " <test> ?variation")
	exit()
test = sys.argv[1]
variation = str(sys.argv[2] if(len(sys.argv)>=3) else 0);

#main(test, variation)

test_config = config_test.getTest("test_basic")
test_hist_data = history_data.load("test_basic", "1", test_config)	

def calc_sp(test_hist_data, ctype):
	ctype_hist_data = [x for x in test_hist_data['data'] if x['ctype'] == ctype]
	msp = {}
	for m in ctype_hist_data:
		val = copy.deepcopy(msp.get(m['offer'], [0, 0]))
		val[0] += 1.0
		val[1] += 1 if m['scout'] == False and m['offer'] <= m['cust_price'] else 0
		msp[m['offer']] = val

	prices = list(msp.keys())
	prices.sort()
	acc = [0, 0]
	sp = []
	for p in reversed(prices):
		acc = [ sum(x) for x in zip(acc,msp[p]) ]
		if p % 5 == 0:
			sp.append( [p, round(100.0*acc[1]/acc[0])/100 ] )
	sp = [ x for x in sp if x[1] > 0  ]
	return sp

def getProfile(hist_data):
	months = [0]*12
	weeks = [0]*7
	for x in hist_data:
		months[x['date']%12] += 1
		weeks[x['date']%7] += 1

	total = len(hist_data)
	M = round(1.0*len([x for x in hist_data if x['ctype']=='m'])/total*100)/100;
	months = [ round(100.0*x/total)/100 for x in months ]
	weeks = [ round(100.0*x/total)/100 for x in weeks ]
	return {'myopia': M, 'month_profile': months, 'weeks_profile':weeks}
	

sp_m = calc_sp(test_hist_data, 'm')
sp_s = calc_sp(test_hist_data, 's')
print("\nm\n:", sp_m )
print("\ns\n:", sp_s )
calculated_profile = getProfile(test_hist_data['data'])
print(calculated_profile)

baseDay = datetime.date.fromisoformat('2022-01-01').toordinal();
[total_qty, total_days] = [test_config.target.target_qty, test_config.target.period_days]

past_total_vol = len(test_hist_data['data']);
calc_adv = round(past_total_vol/365.0);

relative_target = [];
for i in range(total_days):
	d = datetime.date.fromordinal(baseDay+i)
	m = d.month-1
	w = d.weekday()
	relative_target.append( 100.0 * calculated_profile['month_profile'][m] * calculated_profile['weeks_profile'][w])

relative_target = [x/sum(relative_target) for x in relative_target ]
daily_target_qtys = [ round(total_qty * x) for x in relative_target ]
daily_expected_req = [ round(past_total_vol * x) for x in relative_target ]

delta = total_qty-sum(daily_target_qtys)
abs_delta = abs(delta);
for i in range(abs_delta):
	daily_target_qtys[i] += delta/abs_delta
	daily_target_qtys[i] = int(daily_target_qtys[i])


calc_req_vol = calc_adv;

day = 0;
target_sale_qty = daily_target_qtys[0];
expected_req_vol = daily_expected_req[0];

solution = lp_solve.solve(target_sale_qty, expected_req_vol, calculated_profile['myopia'] , sp_m, sp_s)
print(solution)

#lp
#Variables --> #of request for Price points .. req[i]
#Constraints --> 
	# Sum of ( req[i] ) <= expected_req_vol
	# Sum of ( sp[i]*req[i] ) <= target_qty
#Optimize
	# sum of ( req[i]*sp[i]*price[i] )






