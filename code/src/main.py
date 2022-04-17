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

import bisect
def calculateSalesProbabilitiesComb(sale_prob_mayo, sale_prob_strt):
	p1 = [[x[0],x[1]*0.2] for x in sale_prob_mayo]
	p2 = [[x[0],x[1]*0.8] for x in sale_prob_strt]
	k1 = sorted([x[0] for x in p1])
	k2 = sorted([x[0] for x in p2])
	kk = sorted(list(set(k1+k2)), reverse = True)
	d1 = dict(p1)
	d2 = dict(p2)
	res = []
	for k in kk:
		f1 = f2 = 0
		i1 = bisect.bisect_left(k1,k)
		if( len(k1) > i1):
			f1 = d1[k1[i1]]
		i2 = bisect.bisect_left(k2,k)
		if( len(k2) > i2):
			f2 = d2[k2[i2]]
		res.append( [k, round(1000*(f1+f2))/1000] );
	return res


def calculateSalesProbabilities(test_hist_data, ctype):
	if(ctype == 'c'):
		ctype_hist_data = deepcopy(test_hist_data['data'])
	else:
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

def makeDailyTargetProfile(start_date, total_qty, total_days, calculated_profile, vwap=True):
	global sale_start_date
	global MSQ


	past_total_vol = len(test_hist_data['data']);
	calc_adv = round(past_total_vol/365.0);
	total_expected_req = calc_adv*total_days;

	relative_target = [];
	for i in range(total_days):
		d = datetime.date.fromordinal(start_date+i)
		m = d.month-1
		w = d.weekday()
		if vwap:
			relative_target.append(100.0 * calculated_profile['month_profile'][m] * calculated_profile['weeks_profile'][w])
		else: #TWAP
			relative_target.append(1);

	relative_target = [x/sum(relative_target) for x in relative_target ]
	daily_target_qtys = [ round(total_qty * x) for x in relative_target ]
	daily_expected_req = [ round(total_expected_req * x) for x in relative_target ]

	if MSQ*total_days <= total_qty:
		daily_target_qtys = [MSQ]*total_days
		daily_target_qtys[0] = total_qty-MSQ*(total_days-1)

	return ([daily_target_qtys, daily_expected_req])

def makeOfferPriceFromLPSolution(ctype, solution):
	try:
		res_vec = solution[ctype];
		total = sum(list([x[1] for x in res_vec]));
		n = round(random.random()*total);
		for r in res_vec:
			if n < r[1]:
				return r[0]
			n -= r[1]
		#print(res_vec)
		return((res_vec[-1])[0])
	except:
		print("res_vec", res_vec)
		return((res_vec[-1])[0])


def simulateForLPPricing(msg, total_qty, sale_prob_mayo, sale_prob_strt, expected_myo, use_vwap, ctype_ovr=''):
	global calculated_profile
	global total_days
	global sfdata
	global sale_start_date

	random.seed(300)
	[daily_target_qtys, daily_expected_req] = makeDailyTargetProfile(sale_start_date, total_qty, total_days, calculated_profile, use_vwap);
	sfi = 0;
	dp_rev = 0;
	dp_remaining = total_qty
	acc_sale_target = 0;

	trace = [];
	for day in range(total_days):
		date_now = sale_start_date + day
		today_vol = [x for x in sfdata if x['date'] == date_now]
		#acc_sale_target += daily_target_qtys[day];
		#acc_sale_target = max(1, acc_sale_target)
		#target_sale_qty = acc_sale_target
		[daily_target_qtys, ignored_] = makeDailyTargetProfile(date_now, dp_remaining, total_days-day, calculated_profile, use_vwap);
		target_sale_qty = max(1, daily_target_qtys[0])
		acc_sale_target = target_sale_qty
		expected_req_vol = daily_expected_req[day];
		solution = lp_solve.solve(target_sale_qty, expected_req_vol, expected_myo, sale_prob_mayo, sale_prob_strt)
		sold = 0
		real_vol = 0
		real_target_qty = acc_sale_target
		today_rev=0
		while sfi < len(sfdata) and sfdata[sfi]['date'] == date_now:
		#{
			real_vol += 1
			ctype_loc = ctype_ovr if len(ctype_ovr) else sfdata[sfi]['ctype'];
			if acc_sale_target < 0:
				dp = 650
			else:
				dp = makeOfferPriceFromLPSolution(ctype_loc, solution)
			if dp_remaining and sfdata[sfi]['cust_price'] >= dp and sfdata[sfi]['scout'] == False:
				dp_remaining -= 1
				acc_sale_target -= 1
				dp_rev += dp/1000.0
				sold += 1
				today_rev += dp/1000.0
			sfi += 1
		#} while ends	
		trace.append([
				day, 
				expected_req_vol,
				real_vol,
				daily_target_qtys[0],
				real_target_qty,
				sold,
				today_rev,
				str(solution).replace(",", "_") 
			])
	with open(msg + '.csv', 'w', newline='') as csvfile:
		csvfile.write("day,exp_req,real_req,target_qty,real_target_qty,sold,today_rev,solution")
		for d in trace:
			ds = [str(x) for x in d]
			csvfile.write('\n'+','.join(ds))
	return([msg, dp_rev, dp_remaining]);


def simulateForLPPricingVWAP(total_qty):
	global sale_prob_mayo
	global sale_prob_strt
	expected_myo = calculated_profile['myopia']
	return simulateForLPPricing("VWAP", total_qty, sale_prob_mayo, sale_prob_strt, expected_myo, True)

def simulateForLPPricingTWAP(total_qty):
	global sale_prob_mayo
	global sale_prob_strt
	expected_myo = calculated_profile['myopia']
	return simulateForLPPricing("TWAP", total_qty, sale_prob_mayo, sale_prob_strt, expected_myo, False)

def simulateForLPPricingComb(total_qty):
	global sale_prob_comb
	expected_myo = 0
	return simulateForLPPricing("COMB", total_qty, [], sale_prob_comb, 0, False, 's')

def simulateForCostPlusPricing(total_qty):
	global sfdata
	global total_days
	global sale_start_date

	max_date = sale_start_date + total_days

	sfi = 0;
	cp_prices = [ round(x*400) for x in [1.15, 1.25, 1.4, 1.5, 1.6] ]
	fixed_revenues = dict.fromkeys( cp_prices, 0 )
	fixed_remaining = dict.fromkeys( cp_prices, total_qty )
	while sfi < len(sfdata):
		if(sfdata[sfi]['date'] > max_date):
			break;
		for p,rev in fixed_revenues.items():
			if fixed_remaining[p] and sfdata[sfi]['cust_price'] >= p and sfdata[sfi]['scout'] == False:
				fixed_remaining[p] -= 1
				fixed_revenues[p] += p/1000.0
		sfi += 1
	return [ fixed_revenues, fixed_remaining]

test = sys.argv[1]
variation = str(sys.argv[2] if(len(sys.argv)>=3) else 0);

test_config = config_test.getTest("test_basic")
test_hist_data = history_data.load("test_basic", "1", test_config)	
thdata = test_hist_data['data'];
sf = history_data.simulatFuture("test_basic", "3", test_config)
sfdata = sf['data']
sale_start_date = sfdata[0]['date']

MSQ = maxSellableQty(thdata)
sale_prob_mayo = calculateSalesProbabilities(test_hist_data, 'm')
sale_prob_strt = calculateSalesProbabilities(test_hist_data, 's')
sale_prob_comb = calculateSalesProbabilitiesComb(sale_prob_mayo, sale_prob_strt)

calculated_profile = calculateProfile(test_hist_data['data'])

[total_qty, total_days] = [test_config.target.target_qty, test_config.target.period_days]
total_days = 100
total_qtys = [ round(total_days*MSQ/10.0),  round(total_days*MSQ/5.0), round(total_days*MSQ/3.0), round(total_days*MSQ/1.5), round(total_days*MSQ) ]
#total_qtys = [8000]
#total_qtys = [1500, 4000, 5000, 6000, 6100, 7000, 7100, 8000, 8100, 9000, 9100, 10000, 10100, 11000, 11100, 12000, 13000, 13800, 14000]
total_qtys = list(range(1000,15200,200))
total_qtys = [8000]


#rrrrr;
model_revenue = {};
model_unsold = {};
for total_qty in total_qtys:
	print( "====", total_qty, "====" )
	model_revenue[ total_qty ] = {}
	model_unsold[ total_qty ] = {}

	[cp_revs, cp_rems] = simulateForCostPlusPricing(total_qty)
	for p,r in cp_revs.items():
		model_revenue[ total_qty ][ "CP_" + str(p) ] = r;
	for p,r in cp_rems.items():
		model_unsold[ total_qty ][ "CP_" + str(p) ] = r;

	[name, rev, uns] = simulateForLPPricingComb(total_qty);
	model_revenue[ total_qty ][ name ] = rev;
	model_unsold[ total_qty ][ name ] = uns;

	[name, rev, uns] = simulateForLPPricingTWAP(total_qty);
	model_revenue[ total_qty ][ name ] = rev;
	model_unsold[ total_qty ][ name ] = uns;

	[name, rev, uns] = simulateForLPPricingVWAP(total_qty);
	model_revenue[ total_qty ][ name ] = rev;
	model_unsold[ total_qty ][ name ] = uns;

keys = list(model_revenue[total_qtys[0]].keys())
keys = ['total_qty'] + keys;
with open('rev.csv', 'w', newline='') as csvfile:
	csvfile.write(','.join(keys))
	for tq in total_qtys:
		d = [tq] + list(model_revenue[tq].values())
		ds = [str(x) for x in d]
		csvfile.write('\n'+','.join(ds))

with open('rem.csv', 'w', newline='') as csvfile:
	csvfile.write(','.join(keys))
	for tq in total_qtys:
		d = [tq] + list(model_unsold[tq].values())
		ds = [str(x) for x in d]
		csvfile.write('\n'+','.join(ds))

