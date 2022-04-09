'''
Product data: Product code, category, entry date, total inventory, quality (rating) 
Basic Prices: Base price, cost of storage/time, min and max sale price 
Sales objective: Average Sale price, Time to sell, 
Current Status: Remaining inventory, Current cost price
Competition data: others price, other’s quality (if available)
Market: Current demand, predicted demand in future based on history
Explore factor: new product discount, new customer discount

how to make vwap for ecommerce dp
transaction table --> vwap profile (time window -> #of txn)
transaction table --> demand curve (dx/dp)
inflation adjustment
predict number of items those can be sold at each prices.
if met daily target start showing high prices

Inputs:
(1) txnTable --> 
| product | date |  clientFactor | salePrice | competitorPrice | costPrice | profit

(2) Historical RequestRate

(3) SalesObjective:
Objective .. 100 items , over 5 days

(4) Ongoing

(5) CustomerData


Intermediate:

#ItemCanBeSold | CustomerCategory | Price 


#Item to sell,, 


'''
class ProductData: 
    @classmethod
    def __init__(self, productCode, productCategory, launchDate, totalInventory, quality):
        self.productCode = productCode;
        self.productCategory = productCategory;
        self.launchDate = launchDate;
        self.totalInventory = totalInventory
        self.quality = quality; #(1-5)

    @staticmethod
    def loadFromStore(productCode):
        if(productCode == "iphone 13" || True):
            return ProductData( productCode, "electronics-mobile", "2020-06-01", 1000, 5 );

class PriceSettings: 
    def __init__(self):
        self.basePrice = 0;
        self.minPrice = 0;
        self.maxPrice = 0;
        pass;

class SalesObjective:
    def __init__(self):
        pass;

class SalesStatus:
    def __init__(self):
        pass; 

class MarketTrend:
    def __init__(self):
        self.currentSellingRate = 0; ## 0 --> 1, more than 1 is high in demand
        self.futureDemandAnticipation = 0;  ## 0 --> 1, more than 1 is high demand in future 

class CompetitionData:
    def __init__(self):
        self.otherPrices = [
            '''
            {'quality': 'superior/same/worse', 'price': number}
            '''
        ]

        pass; 

class DiscountFactor:
    def __init__(self):
        self.prudctFactor = 0;
        self.customerFactor = 0;

class Product:
    def __init__(self, productCode):
        self.productData = ProductData.loadFromStore(productCode);
        self.priceSettings = PriceSettings(productCode); 
        self.discountFactor = DiscountFactor();
        self.competitionData = CompetitionData();
        self.marketTrend = MarketTrend();

        self.calculatedPrice = 0;
        pass;

    def calcPrice(self):
        if(self.MarketTrend.isOngoingHighDemand()):
            self.calculatedPrice = self.priceSettings.maxPrice;

        if(self.MarketTrend.isAnticipatedHighFutureDemand() > pendingInventoryRatio):
            self.calculatedPrice = self.priceSettings.maxPrice;

        # calculatr factors for discounting from the max price 
        # rice points --> currentPrice --> maxPrice 
        #
        
        demandFactor = 0;
        customerFactor = 0; #find a number 
        exploreFactor = 0;

        priceFactor = calculatedPriceFactor( demandFactor, customerFactor, exploreFactor ); 

        #please note price factor can be negative value, that is to clearup the inventories, to avoid storage cost and wastage due to perishabilty        

        price = currentPrice + priceFactor*Range;
        return price; 

    def calculatedPriceFactor( demandFactor, customerFactor, exploreFactor, competitorData ):
        #demand factor: this is should be most important factor
        #explore factor should only be inverse of inventory remaining. 
        #customer factor: customers can get discount, this is explicit 

        priceFactor = 1

        '''
        We need to generate a table like this... this can be gernerated using numerical analysis, statistical analysis or ML techniques
        ╔════════╤═════════╤══════════╤═══════╗
        ║ Demand │ Explore │ Customer │ Price ║
        ╠════════╪═════════╪══════════╪═══════╣
        ║ 0.9    │ 1       │ 0.9      │ 0.9   ║
        ╟────────┼─────────┼──────────┼───────╢
        ║ 0.8    │ 0.9     │ 1        │ 0.75  ║
        ╚════════╧═════════╧══════════╧═══════╝

        We are trying to optimize the price offered which maximizes the possibility of purchase 
        
        priceFactor = tableLookpup( grid(demandFactor), grid(customerFactor), grid(exploreFactor))

        Profit = ( Sum(Price-i*IS-i)) ) - (ItemProduce*Cost + FixedCost + StorageCost* + (ItemProduced-ItemSold)*PerItemCostOfDisposal )
        
        Conversion probability == Ideal 10%
            - Average search rate. 
            - Demand curve.
                Price,CustomerType  --> #item sold
                item to sell        --> Price 
            - You need to have a daily target 
                - TWAP
                - Volume profile
            - Reacting to ongoing demand
        
        Sell at max. when there is demand, or continue selling 
        Price - Denand - 


        '''

        return priceFactor; 