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

####### Script Startup: Argv processing and run #########
if(len(sys.argv) < 2):
	print(sys.argv[0] + " <test> ?variation")
	exit()


def calculateSalesProbabilities(test_hist_data, ctype):
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

def calculateProfile(hist_data):
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

def maxSellableQty(hist_data):
	min_price = min([x['offer'] for x in hist_data])
	MSQ = len([x for x in hist_data if x['scout'] == False and x['cust_price'] >= min_price])
	MSQ = round(MSQ/365);
	return MSQ;

def makeDailyTargetProfile(total_qty, total_days, calculated_profile):
	global sale_start_date
	past_total_vol = len(test_hist_data['data']);
	calc_adv = round(past_total_vol/365.0);
	total_expected_req = calc_adv*total_days;

	relative_target = [];
	for i in range(total_days):
		d = datetime.date.fromordinal(sale_start_date+i)
		m = d.month-1
		w = d.weekday()
		relative_target.append(100.0 * calculated_profile['month_profile'][m] * calculated_profile['weeks_profile'][w])
	relative_target = [x/sum(relative_target) for x in relative_target ]
	daily_target_qtys = [ round(total_qty * x) for x in relative_target ]
	daily_expected_req = [ round(total_expected_req * x) for x in relative_target ]

	'''
	delta = total_qty-sum(daily_target_qtys)
	abs_delta = abs(delta);
	for i in range(abs_delta):
		daily_target_qtys[i] += delta/abs_delta
		daily_target_qtys[i] = int(daily_target_qtys[i])
	'''
	return ([daily_target_qtys, daily_expected_req])

def makeOfferPriceFromLPSolution(ctype, solution):
	res_vec = solution[ctype];
	total = sum(list([x[1] for x in res_vec]));
	n = round(random.random()*total);
	for r in res_vec:
		if n < r[1]:
			return r[0]
		n -= r[1]
	return((res_vec[-1])[0])


test = sys.argv[1]
variation = str(sys.argv[2] if(len(sys.argv)>=3) else 0);

test_config = config_test.getTest("test_basic")
test_hist_data = history_data.load("test_basic", "1", test_config)	
thdata = test_hist_data['data'];
sf = history_data.simulatFuture("test_basic", "1", test_config)
sfdata = sf['data']
sale_start_date = sfdata[0]['date']

MSQ = maxSellableQty(thdata)


sale_prob_mayo = calculateSalesProbabilities(test_hist_data, 'm')
sale_prob_strt = calculateSalesProbabilities(test_hist_data, 's')
calculated_profile = calculateProfile(test_hist_data['data'])
expected_myo = calculated_profile['myopia']
[total_qty, total_days] = [test_config.target.target_qty, test_config.target.period_days]

total_qtys = [ round(total_days*MSQ/10.0),  round(total_days*MSQ/5.0), round(total_days*MSQ/3.0), round(total_days*MSQ/1.5) ]

#cp_prices = [1.15, 1.25, 1.4, 1.5]
cp_prices = [ round(x*400) for x in [1.15, 1.25, 1.4, 1.5, 1.6] ]
for total_qty in total_qtys:
	[daily_target_qtys, daily_expected_req] = makeDailyTargetProfile(total_qty, total_days, calculated_profile);
	print("total_qty=",total_qty)
	sfi = 0;
	fixed_revenues = dict.fromkeys( cp_prices, 0 )
	fixed_remaining = dict.fromkeys( cp_prices, total_qty )
	dp_rev = 0;
	dp_remaining = total_qty

	random.seed(400)
	acc_sale_target = 0;
	for day in range(total_days):
		date_now = sale_start_date + day
		today_vol = [x for x in sfdata if x['date'] == date_now]
		actual_myo =  len([x for x in today_vol if x['ctype'] == 'm'])*1.0/len(today_vol)
		acc_sale_target += daily_target_qtys[day];
		acc_sale_target = max(0, acc_sale_target)
		target_sale_qty = acc_sale_target
		#print( "Starting with actual=",daily_target_qtys[day], ",modified=",acc_sale_target )
		expected_req_vol = daily_expected_req[day];

		solution = lp_solve.solve(target_sale_qty, expected_req_vol, expected_myo, sale_prob_mayo, sale_prob_strt)
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
				dp = makeOfferPriceFromLPSolution(sfdata[sfi]['ctype'], solution)
				if dp_remaining and sfdata[sfi]['cust_price'] >= dp and sfdata[sfi]['scout'] == False:
					dp_remaining -= 1
					acc_sale_target -= 1
					dp_rev += dp/1000.0
					#print(dp)
			sfi += 1
		#print( "day=", date_now, "expected_req_vol=", expected_req_vol, ", actual_vol=", req_served, 
		#		", expected_myo=", expected_myo, ", actual myo=", r_myo*1.0/(r_myo+r_str), ",sol=", solution );

	print(fixed_revenues)
	print(dp_rev)