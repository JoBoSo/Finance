import pandas as pd
import yfinance as yf # documentation: https://pypi.org/project/yfinance/

security = "BABA"
benchmark = "^GSPC"
start_date = "2016-09-08"
end_date = "2019-10-07"
interval = "1mo" # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
period = None # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max


################################################################################


# pulls historical market data from Yahoo Finance for security and benchmark
data = yf.download('{} {}'.format(security, benchmark),  
                   start=start_date, 
                   end=end_date, 
                   interval = interval,
                   period = period)

# beta_reg(data) produces the beta regression (slope method) for historical data
#    data for chosen security and benchmark.
# beta_reg: DataFrame --> Float64
def beta_reg(data):
    
    # gets daily returns for security and benchmark
    def daily_return(data, ticker):
        daily_return = [None]
        last = None
        for i, row in data.iterrows():
            curr = row['Adj Close'][ticker]
            if last != None:
                change = (curr - last) / last
                daily_return += [change]
            last = curr     
        return daily_return
    
    sec_returns = daily_return(data, security)
    bench_returns = daily_return(data, benchmark)    
    
    # gets (xi-xbar) and (yi-ybar) inputs 
    mean = lambda l: sum(l[1:]) / len(l[1:])
    xbar = mean(sec_returns)
    ybar = mean(bench_returns)
    xs = []
    ys = []
    for i in range(1, len(sec_returns)):
        xs += [sec_returns[i] - xbar]
        ys += [bench_returns[i] - ybar]
    
    # calculates beta regression    
    over = 0
    under = 0
    for i in range(0, len(xs)):
        over += xs[i] * ys[i]
        under += ys[i]**2
    beta_reg = over / under
    return beta_reg
    
    
beta = beta_reg(data) 
print(beta)
