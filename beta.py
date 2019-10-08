import pandas as pd
import yfinance as yf # documentation: https://pypi.org/project/yfinance/

security = "FB"
benchmark = "^GSPC"
start_date = "2016-09-08"
end_date = "2019-10-07"
interval = "1mo" # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
period = None # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max

data = yf.download('{} {}'.format(security, benchmark),  
                   start=start_date, 
                   end=end_date, 
                   interval = interval,
                   period = period)

def daily_return(data, ticker):
    daily_return = [None]
    last = None
    for i, row in data.iterrows():
        curr = row['Adj Close'][ticker]
        if last != None:
            change = (curr - last) / last
            daily_return += [change]
        last = curr 
    data.insert(len(data.columns), 'Daily Change {}'.format(ticker), daily_return, True)
        
daily_return(data, security)
daily_return(data, benchmark)

def slope_beta(data):
    xbar = data['Daily Change {}'.format(security)].mean() 
    ybar = data['Daily Change {}'.format(benchmark)].mean()
    xs = []
    ys = []
    for i, row in data.iterrows():
        xi = row['Daily Change {}'.format(security)]
        yi = row['Daily Change {}'.format(benchmark)]
        xsi = float(xi - xbar)
        ysi = float(yi - ybar)
        xs += [xsi]       
        ys += [ysi]  
    over = 0
    under = 0
    for i in range(1, len(xs)):
        over += xs[i] * ys[i]
        under += ys[i]**2
    slope_beta = over / under
    return slope_beta
    
    
beta = reg2(data) 



################################################################################
'''
def reg(data):
    xbar = data['Daily Change {}'.format(security)].mean() 
    ybar = data['Daily Change {}'.format(benchmark)].mean()
    xs = []
    ys = []
    xs_by_ys = []
    ys_sqr = []
    for i, row in data.iterrows():
        
        xi = row['Daily Change {}'.format(security)]
        yi = row['Daily Change {}'.format(benchmark)]
        
        curr_xs = float(xi - xbar)
        xs += [curr_xs]
        
        curr_ys = float(yi - ybar)
        ys += [curr_ys]
        
        xs_by_ys += [curr_xs * curr_ys]
        ys_sqr += [curr_ys**2]
        
    data.insert(len(data.columns), 'xs - {}'.format(security), xs, True)
    data.insert(len(data.columns), 'ys - {}'.format(benchmark), ys, True)
    data.insert(len(data.columns), 'xs_by_ys', xs_by_ys, True)
    data.insert(len(data.columns), 'ys_sqr', ys_sqr, True)
    
    over = data['xs_by_ys'].sum()
    under = data['ys_sqr'].sum()
    
    slope_beta = over / under
    print(slope_beta)
    return slope_beta
    
    
reg(data) 
'''

