class RequestHistoryConfiModel:
	def __init__(self, 
				months=[10, 8, 8, 7, 8, 9, 8, 7, 8, 8, 9, 10 ],
				weekdays=[9,11,12,13,15,20,20],
				sigma=0.1,
				adv=1000,
				):
		self.months = months 
		self.weekdays = weekdays
		self.sigma = sigma
		self.adv = adv
	def __str__(self):
		return ( "\nRequestHistory, \nmonths=" + str(self.months) + ",weekdays=" + str(self.weekdays) + ",adv=" + str(self.adv) + ",std_dev=" + str(self.sigma));
	pass;

class StrategicCustomerBase:
	def __init__(self, scoute_percentage=90, competition_price=500, sigma=0.1):
		self.scoute_percentage = scoute_percentage;
		self.competition_price = competition_price;
		self.sigma = sigma;
	def __str__(self):
		return ( "scoute_percentage=" + str(self.scoute_percentage) + ",competition_price=" + str(self.competition_price) + ",sigma=" + str(self.sigma));


class MayopicCustomerBase:
	def __init__(self, scoute_percentage=70, cental_price=520, sigma=0.5):
		self.scoute_percentage = scoute_percentage;
		self.cental_price = cental_price;
		self.sigma = sigma;

	def __str__(self):
		return ( "scoute_percentage=" + str(self.scoute_percentage) + ",cental_price=" + str(self.cental_price) + ",sigma=" + str(self.sigma));


class CustomerBaseConfigModel:
	def __init__(self, myopic_percentage=0.1, sigma=0.1, myopic_info=MayopicCustomerBase(), strategic_info=StrategicCustomerBase() ):
		self.myopic_percentage = myopic_percentage;
		self.myopic_info=myopic_info;
		self.strategic_info = strategic_info;
		self.sigma  = sigma

	def __str__(self):
		return ("\n**CustomerBase**\n" +
				"myopic_percentage=" + str(self.myopic_percentage) + 
				",\nmyopic_info=" + str(self.myopic_info) + ",\nstrategic_info=" + str(self.strategic_info));


class TargetModel:
	def __init__(self, target_qty=1000, period_days=100):
		self.target_qty = target_qty
		self.period_days = period_days
	def __str__(self):
		return("\nTargetModel- target_qty:" + str(self.target_qty) + ",period:" + str(self.period_days) );

class TestModel:
	def __init__(self, customer_base=CustomerBaseConfigModel(), requests_history=RequestHistoryConfiModel(), target=TargetModel() ):
		self.customer_base = customer_base;
		self.requests_history = requests_history;
		self.target = target

	def __str__(self):
		return ("Test Info\n" + str(self.customer_base) + "\n" + str(self.requests_history) + "\n" + str(self.target))