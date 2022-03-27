target_sale_qty = 200
expected_req_vol = 3796
sp_m = [[600, 0.1], [510, 0.3]]
sp_s = [[505, 0.05], [500, 0.1], [495, 0.2]] 
mratio = 0.05

#Variables --> #of request for Price points .. req[i]
#Constraints --> 
	# Sum of ( req[i] ) <= expected_req_vol
	# Sum of ( sp[i]*req[i] ) <= target_qty
#Optimize
	# sum of ( req[i]*sp[i]*price[i] )



sp_t = sp_m + sp_s;


expected_m_vol = round(expected_req_vol*mratio)
expected_s_vol = expected_req_vol-expected_m_vol;

print( expected_m_vol, expected_s_vol)



from ortools.linear_solver import pywraplp
from ortools.init import pywrapinit
solver = pywraplp.Solver.CreateSolver('GLOP')

lpv_names =   [ "v_m_qty_" + str(i) for i in range(len(sp_m)) ] + [ "v_s_qty_" + str(i) for i in range(len(sp_s)) ]
lpv_qtys = [solver.NumVar(0.0, solver.infinity(), v) for v in lpv_names]
prices = [p[0] for p in sp_m] + [p[0] for p in sp_s] 
probs = [p[1] for p in sp_m] + [p[1] for p in sp_s] 


#following constraints need to be added

lpv_constraints = [];

#v_qtys[0] + v_qtys[1] < expected_m_vol
lpv_constraints.append( solver.Constraint(0, expected_m_vol) )
for i in range(len(sp_m)):
	lpv_constraints[0].SetCoefficient( lpv_qtys[i], 1 );

#v_qtys[2] + v_qtys[3] + v_qtys[4] < expected_s_vol
lpv_constraints.append( solver.Constraint(0, expected_s_vol) )
for i in range(len(sp_m),len(sp_m)+len(sp_s)):
	lpv_constraints[1].SetCoefficient( lpv_qtys[i], 1 );

#v_qtys[0]*sp_t[0] + v_qtys[1]*sp_t[1] ... < target_qty
lpv_constraints.append( solver.Constraint(0, target_qty) );
for i in range(len(probs)):
	lpv_constraints[2].SetCoefficient( lpv_qtys[i], probs[i] );


#maximize
#prices[0]|*m_qtys[0]*sp_t[0] + v_qtys[1]*sp_t[1] ... 

objective = solver.Objective()
for [prob, price, var] in zip(probs,prices,lpv_qtys):
	objective.SetCoefficient(var, prob*price)


objective.SetMaximization()

status = solver.Solve()

for v in lpv_qtys:
	print(v, v.solution_value(), "\n")