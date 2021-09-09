# Code which will backtest Algo 3 
# For 5 stocks ['CVPUF', 'HRSHF', 'YAHOF', 'VACNY', 'CKHGY']
#----------------------------------- VARIABLES + IMPORTS -----------------------------------
import functions 
from portfolioClass import Portfolio
import time 
import dataframes 
#----------------------------------- MAIN -----------------------------------
if __name__ == "__main__":
    # #----------------------------------- SETUP -----------------------------------
    # new_portfolio = Portfolio(10000.00)
    # new_portfolio.updatePortfolio('portfolio.pickle')
    # functions.createNewFile('portfolioResults.csv', ["Date", "Total Value of Portfolio", "Cash on Hand", "Shares Owned", "Amount in Shares", "Unrealised Profit", "Realised Profit", "Total Growth Rate"])
    # functions.createNewFile('results.csv', ['Ticker', 'Date Sold', 'Amount Invested', 'Profit', '% Return', 'Quarterly Book to Market', 'Quarterly Net Current Assets / MV', 'Quarterly Current Ratio'])
    # #----------------------------------- ACTION -----------------------------------
    # # Loop as if a day by day i.e. for each row in data frame
    # api_calls = 0
    # for current_day in range(1095,0,-1):
    #     # Get current date and portfolio 
    #     current_date = dataframes.data_dict[dataframes.shares_to_test[0]].iloc[-current_day]['date']
    #     ticker_list = [tickers for tickers in dataframes.shares_to_test] 
    #     daily_portfolio = functions.getPortfolio('portfolio.pickle')

    #     #----------------------------------- UPDATING VALUES -----------------------------------
    #     # Start from -1095 element and then loop to most recent element i.e. -1 
    #     for shares_owned in daily_portfolio.positions:
    #         shares_owned.updateShare(dataframes.data_dict[shares_owned.ticker].iloc[-current_day])
    #     # Now can update portfolio values 
    #     daily_portfolio.updateValues()

    #     #----------------------------------- ACTION OWNED -----------------------------------
    #     # Then action owned 
    #     shares_to_sell = daily_portfolio.actionOwned()        
    #     for current_share in shares_to_sell:
    #         daily_portfolio.sellPosition(current_share)
    #         # Add result
    #         functions.addResult('results.csv', current_share, current_date)
    #         api_calls += 1 
    #         # Only if calling Alpha Vantage to get Balance Sheet 

    #     if api_calls == 5:
    #         api_calls = 0
    #         print("NAPTIME")
    #         time.sleep(60)

    #     #fill up current portfolio with share list 
    #     if len(daily_portfolio.positions) < 5:
    #         daily_portfolio.fillPortfolio(ticker_list, -current_day)

    #         # # #----------------------------------- ENDING REMARKS -----------------------------------
    #     day = 1096 - current_day
    #     print(f"Action completed for day: {day}\n")
    #     daily_portfolio.printPortfolio()
    #     # Store results
    #     daily_portfolio.portfolioResults(current_date)

    # # Add benchmark growth in 
    # time.sleep(60)
    # functions.addBenchmarkGrowthRate('portfolioResults.csv', 'VOO', 'portfolioResults.csv')

    # Now store results 
    plot_data = functions.createDataframe('portfolioResults.csv', ['Date', 'Total Value of Portfolio', 'Benchmark Growth Rate', 'Total Growth Rate'],'2017-07-21', '2021-09-03')  
    functions.plotDataframe(plot_data, 'Growth vs Benchmark', 'Date','% Growth', ['Total Growth Rate', 'Benchmark Growth Rate'], 'result.png')  
    functions.displayPortfolioMetrics(plot_data, 'Total Value of Portfolio')