import yfinance as yf
import pandas as pd
import numpy as np

class FinancialAnalysis:
    '''
    Fields:
    self.stock_data stores the last 5 years of market data for stock with 1 day 
         intervals
    self.benchmark_data same as stock_data but for benchmark
    self.info stores info for stock
    self.riskfree stores the risk free rate = price of 13 week t-bill / 100
    '''
    
    # FinancialAnalysis(stock, benchmark) initiates a new FinancialAnalysis
    #    object for stock and associated benchmark.
    # Str Str --> FinancialAnalysis
    # Requires: stock and benchmark are Yahoo Finance tickers
    def __init__(self, stock, benchmark):
        stock = yf.Ticker(stock)
        benchmark = yf.Ticker(benchmark)
        self.info = stock.info
        t_bill = yf.Ticker('^IRX') # 13 week US T-bill ticker
        self.riskfree = t_bill.info['regularMarketPrice'] / 100
        self.stock_data = stock.history(period='5y', interval='1d')
        self.benchmark_data = benchmark.history(period='5y', interval='1d')
        # return_col(df) adds column 'Return %' to df, a yf dataframe.
        def return_col(df):
            last_close = None
            for i, row in df.iterrows():
                if last_close != None:
                    change = (row['Close'] - last_close) / last_close
                    df.at[i, 'Return %'] = 100 * change
                last_close = row['Close']
            #df = df.iloc[1:] # since first row will have empty return cell
        return_col(self.stock_data)
        return_col(self.benchmark_data)
              
     
    # self.beta() produces the five year beta for self against benchmark
    # beta: FinancialAnalsysis --> Float 
    def beta(self):
        # 1. inner merge 'Returns %' for stock and benchmark
        left = self.stock_data[['Return %']]
        right = self.benchmark_data[['Return %']]
        left.rename(columns = {'Return %': 'Stock Return %'}, inplace=True)
        right.rename(columns = {'Return %': 'Benchmark Return %'}, inplace=True)
        data = pd.merge(left, right, on='Date', how='inner')
        # 2. calculate beta
        cov = data.cov().at['Stock Return %', 'Benchmark Return %']
        var = data['Benchmark Return %'].var()
        beta = cov / var
        return beta
    
    # 
    def sharpe(self):
        # expected return on stock = avg annual return over last 5 yrs
        rs = (self.stock_data['Return %'].sum() / 5) / 100
        # risk free rate
        rf = self.riskfree
        # standard deviation of returns on stock
        sd = self.stock_data['Return %'].std()
        sharpe = (rs - rf) / sd
        return sharpe
    
    #
    def capm(self):
        rf = self.riskfree
        beta = self.beta()
        # expected return on the market = avg annual return over last 5 yrs
        erm = (self.benchmark_data['Return %'].sum() / 5) / 100
        rm = erm - rf        
        capm = rf + (beta * rm)
        return capm
    
    #
    # requires: unit is one of 'percent', 'dollar'
    # note: uses price as of time the FA object was created
    def roi(self, buy_price, commission, quantity, unit):
        cost = (buy_price * quantity) + commission
        curr_price = self.info['regularMarketPrice'] 
        mv = curr_price * quantity
        if unit is 'percent':
            roi = 100 * (mv - cost) / cost
        elif unit is 'dollar':
            roi = mv - cost           
        return roi
    
    # computes the number of days required to liquidate a position of size
    #    quantity assuming you can capture 20% of the 3 month ADV.
    def d2l(self, quantity):
        adv_3m = self.info['averageDailyVolume3Month']
        d2l = quantity / (adv_3m * .2)
        return d2l
       
    def sector_beta(sector):
        pass
    
    def unlevered_beta(self):
        pass
    
    # move this to its own file / project
    # produces a graph with bollnger bands
    def bollinger_bands(self):
        pass
    

tsla = FinancialAnalysis('TSLA','^GSPC')


class PortfolioAnalysis:
    '''
    Fields:
    self.portfolio stores the df containing information for all securities in 
         portfolio
    self.securities stores tickers for securities in portfolio
    '''
    def __init__():
        pass
    
    def __iter__():
        pass
    
    def __str__():
        pass
    
    def export_portfolio():
        pass
    
    def add_security(security, quantity, price, commission, position:[l/s], sector, exchange, currency, date):
        pass
    
    def remove_security(security):
        pass
    
    def edit_position([[order type: bought, sold], security, quantity, price, commision, date]):
        pass
    
    def gross():
        pass
    
    def net():
        pass
    
    def L_S_breakdown():
        pass
    
    def VaR():
        pass
    
    def D2L():
        pass
    
    def NAV():
        pass
    
    def total_return(self, [percent, dollar]):
        pass
    
    def alpha():
        pass