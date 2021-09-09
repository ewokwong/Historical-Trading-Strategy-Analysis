# Code which will outline share class for Algo 3
#------------------------ IMPORTS + VARIABLES ------------------------#
# import math
# import pandas
from datetime import date
import csv 
from alpha_vantage.fundamentaldata import FundamentalData
API_KEY = '8X17EEI7VHEPZZZ5'
#------------------------- CLASS ------------------------- #

class Share:
    # When initialising need the portfolio(object), a ticker(string), and data(dataframe)
    def __init__(self, ticker, data, num_shares):
        # Else can initialise everything else
        self.ticker = ticker
        self.current_price = data['adjusted close']
        self.buy_price = data['adjusted close']
        self.amount_invested = num_shares * data['adjusted close']
        self.current_value = num_shares * data['adjusted close']
        self.num_shares = num_shares
        # Calculate Sharpe Ratio of each share
        # Assuming a long-only position rather than
        # market neutral(try to balance long and short holdings)
        # Assuming we get whole dataframe instead of one line and R.F rate is 5%
        # self.sharpe = 0
        self.current_position = data['position']
        self.buy_date = date.today()
        self.sell_date = date.today()

  #----------------------------------- Updating Values -----------------------------------
    # Method which will update price, value and position of our share 
    # Input -> data(1 line from dataframe)
    def updateShare(self, data): 
        self.current_price = data['adjusted close']
        self.current_value = self.num_shares * data['adjusted close']
        self.current_position = data['position']
        self.sell_date = date.today()

