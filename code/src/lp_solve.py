from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit
def solve(target_sale_qty, expected_req_vol, mratio, sp_m, sp_s):
	'''
	Formulate and solve lp using google or tools for dynamic pricing
	Parameters:
		target_sale_qty: qty to sale in the period
		expected_req_vol: expected volume of price requests
		mratio: ratio of request of myopic customers
		sp_m: sale probabilities of myopic customers
		sp_s: sale probabilities of strategic customers
	'''
	sp_t = sp_m + sp_s;
	expected_m_vol = round(expected_req_vol*mratio)
	expected_s_vol = expected_req_vol-expected_m_vol;

	#print( "target_sale_qty=", target_sale_qty, ",expected_req_vol=",expected_req_vol, ",mratio=", mratio, ",\nsp_m=", sp_m, ",\nsp_m=", sp_s )
	print( "@LP.. target_sale_qty=", target_sale_qty, ",expected_req_vol=",expected_req_vol, ",mratio=", mratio)

	solver = pywraplp.Solver.CreateSolver('GLOP')

	lpv_names =   [ "v_m_qty_" + str(i) for i in range(len(sp_m)) ] + [ "v_s_qty_" + str(i) for i in range(len(sp_s)) ]
	lpv_reqcnt_per_price = [solver.NumVar(0.0, solver.infinity(), v) for v in lpv_names]
	prices = [p[0] for p in sp_m] + [p[0] for p in sp_s] 
	probs = [p[1] for p in sp_m] + [p[1] for p in sp_s] 

	#following constraints need to be added
	lpv_constraints = [];

	#v_qtys[0] + v_qtys[1] < expected_m_vol
	lpv_constraints.append( solver.Constraint(0, expected_m_vol) )
	for i in range(len(sp_m)):
		lpv_constraints[0].SetCoefficient( lpv_reqcnt_per_price[i], 1 );

	#v_qtys[2] + v_qtys[3] + v_qtys[4] < expected_s_vol
	lpv_constraints.append( solver.Constraint(0, expected_s_vol) )
	for i in range(len(sp_m),len(sp_m)+len(sp_s)):
		lpv_constraints[1].SetCoefficient( lpv_reqcnt_per_price[i], 1 );

	#v_qtys[0]*probs[0] + v_qtys[1]*probs[1] ... < target_sale_qty
	lpv_constraints.append( solver.Constraint(0, target_sale_qty) );
	for i in range(len(probs)):
		lpv_constraints[2].SetCoefficient( lpv_reqcnt_per_price[i], probs[i] );

	#maximize
	#prices[0]|*m_qtys[0]*probs[0] + v_qtys[1]*probs[1] ... 
	objective = solver.Objective()
	for [prob, price, var] in zip(probs,prices,lpv_reqcnt_per_price):
		objective.SetCoefficient(var, prob*price)

	objective.SetMaximization()
	status = solver.Solve()

	result = {'m' : [], 's' : []}
	if status != solver.OPTIMAL:
		print( "Solution is not optimal" )
		result['optimal'] = False
	else:
		result['optimal'] = True

	for i,v in enumerate(lpv_reqcnt_per_price):
		sol = round(v.solution_value())
		if sol == 0:
			continue;
		pr = prices[i];
		if "_m_" in str(v):
			result['m'].append( [pr, sol] )
		else:
			result['s'].append( [pr, sol] )

	if(len(result['s'])==0):
		result['s'] = result['m']

	return result;
