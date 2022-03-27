from config_model import *
tests = {
	"test_basic" : TestModel( 
		customer_base = CustomerBaseConfigModel(myopic_percentage=0.2) ,
		target = TargetModel(target_qty=100000)
	)
}

def getTest(testName):
	return tests[testName]
