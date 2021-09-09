# Code which will outline attributes and methods of portfolio
#------------------------ IMPORTS + VARIABLES-----------------------#
import math
import pickle
from datetime import date
import time
import csv
import functions
from shareClass import Share

import dataframes
#--------------------------- CLASS --------------------------#
class Portfolio:
    # Input -> cash(float)
    def __init__(self, cash):
        self.starting_cash = cash
        self.current_cash = cash
        self.current_total_value = cash
        self.unrealised_profit_loss = 0
        self.realised_profit_loss = 0
        self.positions = []
        self.available_cash = 0

        # Other important ratios for portfoliso:
        # self.returnRate = 0
        # self.sharpe_ratio = 0
        # self.treynor_ratio = 0
        # self.roi = 0
        # self.hpr = 0
        # self.cagr = 0


    #--------------------------- UPDATING VALUES--------------------------#
    # Method which will update all values of portfolio
    def updateValues(self):
        self.resetValues()
        self.current_total_value = self.current_cash
        for share in self.positions:
            self.current_total_value += share.current_value
            self.unrealised_profit_loss += share.current_value - share.amount_invested
    
    # Method which will reset daily values
    def resetValues(self):
        self.unrealised_profit_loss = 0
        self.current_total_value = 0

    #----------------------------------- Action Owned -----------------------------------
    # Method to action on any stocks in owned
    def actionOwned(self):
        shares_to_sell = []
        for current_share in self.positions:
            if int(current_share.current_position) == -1:
                print(f"We are going to sell {current_share.ticker}")
                # self.sellPosition(current_share)
                shares_to_sell.append(current_share)
            else:
                print(f"Going to keep {current_share.ticker}")
        return shares_to_sell

    #----------------------------------- Buying + Selling -----------------------------------
    # Function which will initialise an attribute of how much money we have to invest
    def getInvestAmount(self):
        if self.current_cash > 2000.00:
            self.available_cash = 2000.00
        else:
            self.available_cash = self.current_cash

    # Method to add position into portfolio
    # Input -> share(object)
    def buyPosition(self, share):
        # 2 things
        # Add position to list
        self.positions.append(share)
        # Reduce cash amount
        self.current_cash -= share.amount_invested
        #Update portfolio
        self.updatePortfolio('portfolio.pickle')

    # Method to remove position from portfolio
    # Input-> share(object)
    def sellPosition(self, share):
        for current_object in self.positions:
            if current_object.ticker == share.ticker:
                self.positions.remove(current_object)
                break
        # Add cash value back and transfer unrealised profit/loss to realised profit/loss
        self.unrealised_profit_loss -= (share.current_value - share.amount_invested)
        self.realised_profit_loss += share.current_value - share.amount_invested
        self.current_cash += share.current_value
        # And update portfolio 
        self.updatePortfolio('portfolio.pickle')

    #----------------------------------- Fill Portfolio -----------------------------------    
    # Method which will fill up a portfolio based on a list of tickers to look at 
    # Input -> list(list) - list of stock tickers, row(int) for the row that it wants to look at -> JUST FOR TESTING
    def fillPortfolio(self,assetList, row):

        tickers_looked_at_today = []
        for current_share in self.positions:
            tickers_looked_at_today.append(current_share.ticker)
        # api_calls = 0 
        # Fill up portfolio
        while len(self.positions) < 5 and len(assetList) > 0:
            # Look at asset once at a time
            #Reset API Calls
            # if api_calls == 5:
            #     api_calls = 0
            #     time.sleep(60)
            current_share = assetList[0]
            if current_share not in tickers_looked_at_today:
                # print(f"Looking at {current_share}")
                #LOOK TO ACTION
                tickers_looked_at_today.append(current_share)
                data = dataframes.data_dict[current_share]
                # api_calls += 1
                if int(data.iloc[row]['position']) == 1:
                    self.getInvestAmount()
                    num_shares = math.floor(self.available_cash / data.iloc[row]['adjusted close'])
                    if num_shares <= 0:
                        print("Not enough cash to buy shares")
                        break
                    print(f"We are going to buy {num_shares} of {current_share}")
                    new_share = Share(current_share, data.iloc[row], num_shares)
                    self.buyPosition(new_share)
            # Remove ticker from list
            assetList.pop(0)

    #----------------------------------- Documentation -----------------------------------
    # Method to save portfolio to pickle file
    def updatePortfolio(self,file):
        with open(file,"wb") as output_file:
            pickle.dump(self, output_file)
            output_file.close()

    # Method to print out positions in portfolios
    def printPortfolio(self):
        print(f"Portfolio value: ${round(self.current_total_value,2)}")
        print(f"Cash: ${round(self.current_cash,2)}")
        print("Positions:")
        for current_object in self.positions:
            print(f"{current_object.num_shares} shares of {current_object.ticker} bought at",end='')
            print(f" ${current_object.buy_price} for ${round(current_object.amount_invested,2)}",end='')
            print(f" is now worth ${round(current_object.current_value,2)}\n")

    # Method which will export results of our trading into a csv which we can see
    # Headers include:
    # Date, Cash, Amount in Shares, Unrealised Profit, Realised Profit, % Return,
    # Sharpe Ratio... CAN ADD MORE LATER

    #current_date date format JUST FOR TESTING 
    def portfolioResults(self, current_date):
        shares_owned = []
        for share in self.positions:
            shares_owned.append(share.ticker)

        results = {
            "Date": current_date,
            'Total Value of Portfolio': round(self.current_total_value,2),
            "Cash on Hand": round(self.current_cash,2),
            "Shares Owned": shares_owned,
            "Amount in Shares": round(self.current_total_value - self.current_cash,2),
            "Unrealised Profit": round(self.current_total_value - self.realised_profit_loss -self.starting_cash,2),
            "Realised Profit": round(self.realised_profit_loss,2),
            "Total Growth Rate": round((((self.current_total_value / self.starting_cash))- 1) * 100, 2),
            # "Benchmark Daily Growth Rate": benchmark
            # "Sharpe Ratio": 0
        }
        # Daily % Change: (EOD VALUE / START VALUE) - 1
        # Compound Growth Rate: ((CURRENT VALUE / START VALUE) ^ (1/ NUM PERIODS)) - 1

        with open('portfolioResults.csv', 'a') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(results.values())
        