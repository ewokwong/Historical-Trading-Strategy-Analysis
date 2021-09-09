# Functions for Algo 3
#------------------------ IMPORTS + VARIABLES ------------------------#
import csv
from csv import DictReader
from datetime import date, datetime 
import ffn 
import pickle
import math
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import matplotlib
matplotlib.use('TkAgg')
import numpy as np
import pandas as pd 
import time 
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData



API_KEY = '8X17EEI7VHEPZZZ5'
#-------------------------- GETTING PORTFOLIO --------------------------#
# Function which will initiate a portfolio object from a CSV file
def getPortfolio(file):
    with open(file,'rb') as portfolio_input:
        portfolio = pickle.load(portfolio_input)
    return portfolio

#-------------------------- GETTING DATAFRAME --------------------------#
# Function which will get a ticker and output a dataframe modified to Alpha model
# Model we will be using is a 50-day 20-day crossover moving average
# Input -> ticker(string)
# Output -> result(dataframe)
def tickerDataframe(ticker):
    time_series = TimeSeries(key = API_KEY, output_format='pandas')
    data, meta = time_series.get_daily_adjusted(symbol = ticker, outputsize = 'full')
    #Adjust columns and sort out rows
    data = data.drop(columns=['7. dividend amount', '8. split coefficient'])
    columns = ['open','high','low','close','adjusted close', 'volume']
    data.columns = columns
    data['date'] = data.index.date
    data.sort_index(inplace=True)
    #Get 50 and 200 day SMA's and add it to our data
    data['20 day SMA'] = SMA(data, 20, 'adjusted close')
    data['50 day SMA'] = SMA(data, 50, 'adjusted close')
    #Numpy where 5 day SMA is larger than 13 day yield 1 else yield 0
    data['signal'] = np.where(data['20 day SMA'] > data['50 day SMA'], 1 , 0)
    # Get the difference between signals of furthest price and current price
    data['position'] = data['signal'].diff()
    return data

def SMA(data, period, column):
    return data[column].rolling(window=period).mean()

#-------------------------- RESULTS --------------------------#

# Function to update results folder with info of share just sold and quarterly balance sheet data 
# Input -> file(string), share(object), current_date(string) - date that it is sold 
def addResult(file, share, current_date):
    # Results dictionary will be in form:
    # ['Ticker', 'Date Sold', 'Amount Invested', 'Profit', '% Return',
    # 'Book to Market', 'Net Current Assets / MV', 'Quick Ratio']
    results = {
    'Ticker': share.ticker,
    'Date Sold': str(current_date),
    'Amount Invested': round(share.amount_invested,2),
    'Profit': round(share.current_value - share.amount_invested,2),
    '% Return': round(((share.current_value - share.amount_invested)/share.amount_invested) * 100,2)
    }

    # Get Fundamental Data 
    fundamental_data = FundamentalData(key = API_KEY, output_format = 'pandas')
    try:
        data = fundamental_data.get_balance_sheet_quarterly(symbol = share.ticker)

        # Find row which comprises to same quarter as date sold 
        for row_index in range(len(data[0]['fiscalDateEnding'])):
            # IF QUARTERS MATCH:
            # If date sold is before current fiscal date ending but more than the next one in line then it is in that quarter 
            if find_difference_days(str(current_date), str(data[0]['fiscalDateEnding'][row_index])) >= 0 and find_difference_days(str(current_date), str(data[0]['fiscalDateEnding'][row_index + 1])) < 0:
                print(f"{current_date} is in quarter when fiscal Date ending is {data[0]['fiscalDateEnding'][row_index]}")
                break 
        results['Book to Market'] = round((float(data[0]['totalShareholderEquity'][row_index]) / (share.current_price * float(data[0]["commonStockSharesOutstanding"][row_index]))) ,2)
        results['Net Current Assets / MV'] = round((float(data[0]['totalCurrentAssets'][row_index]) - float(data[0]['totalLiabilities'][row_index])) / float(data[0]["commonStockSharesOutstanding"][row_index]),2)
        results['Current Ratio'] = round((float(data[0]['totalCurrentAssets'][row_index]) / float(data[0]['totalCurrentLiabilities'][row_index])),2)
    except Exception as e:
        print(f"Error message: {e}")

    # ADD TO FILE
    with open(file, 'a') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(results.values())


#--------------------------------------------------------- ADDING BENCHMARK GROWTH RATE  + TESTING ------------------------------------------------------------#
# Function which will write a csv file of benchmark growth rates as last column of portfolio results
# Input -> file(string) - name of file, ticker(string), output(string) - Name of outputfile
def addBenchmarkGrowthRate(file, ticker, output):
    # Open file find starting cash, starting date and ending date of portfolio
    with open(file, 'r') as input_file:
        dict_reader = DictReader(input_file)
        list_of_dict = list(dict_reader)
        # Extract info 
        start_date = list_of_dict[0]['Date']
        start_cash = list_of_dict[0]['Total Value of Portfolio']
        end_date = list_of_dict[-1]['Date']

    # Get dataframe 
    data = tickerDataframe(ticker)
    # Cut dataframe to only dates needed 
    row_number = 0 
    for current_index, current_row in data.iterrows():
        if str(current_row['date']) == start_date:
            num_shares = math.floor(float(start_cash) / current_row['adjusted close'])
            start_value = num_shares * current_row['adjusted close']
            start_row_number = row_number
        if str(current_row['date']) == end_date:
            end_row_number = row_number
            break 
        row_number += 1
    #Cut dataframe
    result = data.iloc[start_row_number:end_row_number + 1]

    for current_dict in list_of_dict:  
        current_date = current_dict['Date']
        # Loop through dataframe 
        for index, row in result.iterrows():
            # If date matches up with date result can compute it 
            if str(row['date']) == current_date:
                current_value = num_shares * row['adjusted close']
                number_days = find_difference_days(start_date, current_date)
                # Can add it to current_dict 
                if number_days == 0:
                    current_dict['Benchmark Growth Rate'] = 0
                else:
                    current_dict['Benchmark Growth Rate'] = round(((current_value/start_value) - 1) * 100, 2)
        
        # Add it to N/A if couldnt be found
        if 'Benchmark Growth Rate' not in current_dict.keys():
            current_dict['Benchmark Growth Rate'] = 'N/A'

    # Add dictionary back to csv
    headers = list_of_dict[0].keys()
    with open(output, 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, headers)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_dict)
     

# Function which will find difference in days between 2 strings
# Input will be i.e. and 2017-03-23 2021-09-02
def find_difference_days(start_date, end_date):
    date_format = "%Y-%m-%d"
    start = datetime.strptime(start_date, date_format)
    end = datetime.strptime(end_date, date_format)
    difference = end - start 
    return difference.days 

# Function which will initialise a dictionary of dataframe given a list of tickers
# Input -> test_list(list)
# Output -> data_dict(dictionary)
def getTestDataframes(test_list):
    data_dict = {}
    for ticker in test_list:
        data_dict[ticker] = tickerDataframe(ticker)
    time.sleep(60)
    return data_dict 

#--------------------------------------------------------- GENERIC FUNCTIONS  ------------------------------------------------------------#
# Function which creates new file
# Input -> file(string), headers(list)
def createNewFile(file, headers):
    with open(file, 'w') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(headers)



#--------------------------------------------------------- Functions for FFN  ------------------------------------------------------------#
# Function to create dataframe off of a csv file with headers from a certain date 
# Input -> file(string), headers(list), start_date(string), end_date(string)
def createDataframe(file, headers, start_date, end_date):
    with open(file, 'r') as input_file:
        # Get a list of dictionaries with [{date:... total growth rate:...} {...}]
        dict_reader = DictReader(input_file)
        list_of_dict = list(dict_reader)
    
    # Then get only the headers you want into a new list of dictionaries 
    resulting_dict = []
    for current_result in list_of_dict:
        # If gone past end_date break from loop
        if find_difference_days(end_date, current_result['Date']) > 0:
            print(f"Gone past {end_date} at {current_result['Date']}")
            break

        # Otherwise make sure past start date
        elif find_difference_days(start_date, current_result['Date']) >= 0: 
            new_entry = {}
            for current_header in headers:
                new_entry[current_header] = current_result[current_header]
    
            resulting_dict.append(new_entry)
    #pd.dataframe(data, index - date, columns - column headers)
    # Change dates into index such that can use with FFN 
    result = pd.DataFrame(resulting_dict)
    # # Set index 
    result = result.set_index(pd.DatetimeIndex(result['Date']))
    float_columns = [current_header for current_header in headers if current_header != 'Date']
    
    for column in float_columns:
        result[column] = pd.to_numeric(result[column],downcast= 'float')

    return result 

# Function which will plot a graph given a dataframe and outputs a photo 
# Input -> dataframe(pandas object), x_label(string), y_label(string), headers(list) output_file(string)
def plotDataframe(dataframe, title, x_label, y_label, headers, output_file):

    #Change to datetime so can be evenly spaced out 
    dataframe['Date']= pd.to_datetime(dataframe['Date'])
    x_index = dataframe['Date']
    fig,ax = plt.subplots(1, figsize=(12,6))

    # Since there is so many points want to plot a maximum of 18 points 
    for current_header in headers:
        # Plot x,y with labels and a mark
        ax.plot(x_index, dataframe[current_header], label = current_header, markevery=1)
    #
    fig.autofmt_xdate()
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    
    #Add legend, title and x + y labels
    plt.legend(loc="best")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)

    fig.savefig(output_file)


# FFN Stats 
def displayPortfolioMetrics(data, header):
    perm = ffn.core.GroupStats(data[header])
    applyRiskFreeRate(perm,0.05)
    #Display 
    perm.display()


# Function which will take in an ffn object and set risk free rate
def applyRiskFreeRate(ffn_object, rf_rate):
    ffn_object.set_riskfree_rate(rf_rate)