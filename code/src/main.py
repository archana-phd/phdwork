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
#total_qty =  int(total_qty/5);
#total_days = 1
#total_qty = 400

past_total_vol = len(test_hist_data['data']);
calc_adv = round(past_total_vol/365.0);
total_expected_req = calc_adv*total_days;

relative_target = [];
for i in range(total_days):
	d = datetime.date.fromordinal(baseDay+i)
	m = d.month-1
	w = d.weekday()
	relative_target.append( 100.0 * calculated_profile['month_profile'][m] * calculated_profile['weeks_profile'][w])

relative_target = [x/sum(relative_target) for x in relative_target ]
daily_target_qtys = [ round(total_qty * x) for x in relative_target ]
daily_expected_req = [ round(total_expected_req * x) for x in relative_target ]

delta = total_qty-sum(daily_target_qtys)
abs_delta = abs(delta);
for i in range(abs_delta):
	daily_target_qtys[i] += delta/abs_delta
	daily_target_qtys[i] = int(daily_target_qtys[i])




#lp
#Variables --> #of request for Price points .. req[i]
#Constraints --> 
	# Sum of ( req[i] ) <= expected_req_vol
	# Sum of ( sp[i]*req[i] ) <= target_qty
#Optimize
	# sum of ( req[i]*sp[i]*price[i] )

sf = history_data.simulatFuture("test_basic", "1", test_config)

def makeOfferPrice(ctype, solution):
	res_vec = solution[ctype];
	total = sum(list([x[1] for x in res_vec]));
	n = round(random.random()*total);
	for r in res_vec:
		if n < r[1]:
			return r[0]
		n -= r[1]
	return((res_vec[-1])[0])


sfi = 0;
sfdata = sf['data']

fixed_revenues = dict.fromkeys( list(range(400,660,10)), 0 )
fixed_remaining = dict.fromkeys( list(range(400,660,10)), total_qty )

dp_rev = 0;
dp_remaining = total_qty
random.seed(400)
baseDay = datetime.date.fromisoformat('2022-01-01').toordinal();
acc_sale_target = 0;
for day in range(total_days):
	date_now = baseDay + day
	today_vol = [x for x in sfdata if x['date'] == date_now]
	actual_myo =  len([x for x in today_vol if x['ctype'] == 'm'])*1.0/len(today_vol)
	acc_sale_target += daily_target_qtys[day];
	acc_sale_target = max(0, acc_sale_target)
	target_sale_qty = acc_sale_target
	print( "Starting with actual=",daily_target_qtys[day], ",modified=",acc_sale_target )
	expected_req_vol = daily_expected_req[day];
	expected_myo = calculated_profile['myopia']
	#expected_myo = actual_myo

	solution = lp_solve.solve(target_sale_qty, expected_req_vol, expected_myo, sp_m, sp_s)
	req_served = 0;
	r_myo = 0;
	r_str = 0;
	while sfi < len(sfdata) and sfdata[sfi]['date'] == date_now:
		req_served += 1
		if(sfdata[sfi]['ctype'] == 's'):
			r_str += 1
		else:
			r_myo += 1
		for p,rev in fixed_revenues.items():
			if fixed_remaining[p] and sfdata[sfi]['cust_price'] >= p and sfdata[sfi]['scout'] == False:
				fixed_remaining[p] -= 1
				fixed_revenues[p] += p/1000.0
	
		if(acc_sale_target>0):
			dp = makeOfferPrice(sfdata[sfi]['ctype'], solution)
			if dp_remaining and sfdata[sfi]['cust_price'] >= dp and sfdata[sfi]['scout'] == False:
				dp_remaining -= 1
				acc_sale_target -= 1
				dp_rev += dp/1000.0
				#print(dp)
		sfi += 1
	print( "day=", date_now, "expected_req_vol=", expected_req_vol, ", actual_vol=", req_served, 
			", expected_myo=", expected_myo, ", actual myo=", r_myo*1.0/(r_myo+r_str), ",sol=", solution );

print(fixed_revenues)
#46600.67999993477

print(dp_rev)