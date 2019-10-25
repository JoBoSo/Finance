#!/usr/bin/env python
# coding: utf-8

# In[1]:


# libraries
import pandas as pd
import datetime as dt
import yfinance as yf # documentation: https://pypi.org/project/yfinance/


# In[2]:


# variables
security = 'BABA'
benchmark = '^GSPC' # S&P 500
interval = '1mo' # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
period = '5y' # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
Tbill_13wks = yf.Ticker('^IRX') # 13 week US T-bill ticker
Rf = Tbill_13wks.info['regularMarketPrice'] / 100 # risk free rate


# In[3]:


# historical data from Yahoo Finance for security and benchmark
sec_data = yf.download(security, interval = interval, period = period)
bench_data = yf.download(benchmark,  interval = interval, period = period)


# In[4]:


# # # # # # # # # # # # # #
#  Building the Dataframe #
# # # # # # # # # # # # # #


# # # # # # # # # # #
# 1. Clean yf data  #
# # # # # # # # # # #

# keep cols: Date (index), Adj Close; drop the rest
drop_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
for df in [sec_data, bench_data]:
    df.drop(drop_cols, axis=1, inplace=True)

    
# convert 'Date' index col from pd.Timestamp to a string date for ease of comparison
for df in [sec_data, bench_data]:
    df.index.names = ['Old Date'] # rename so we don't have two 'Date' cols
    df['Date'] = df.index.strftime('%Y/%m/%d') # create new 'Dates' col
    df.set_index('Date', inplace = True) # set index as new 'Dates' col


# In[5]:


# # # # # # # # # # # # # # # # # # # # # # #
# 2. Create and add 'Interval Return' col  #
# # # # # # # # # # # # # # # # # # # # # # #
    
# note: first row is None

# make_dict_col inserts dictionary into df as a new col where key = index
def make_dict_col(df, dictionary, header):
    # adds the empty new col to df
    nrows = df.shape[1]
    header = header
    df.insert(nrows, header, None, True)
    for i, row in df.iterrows():
        if i in list(dictionary.keys()):
            df.at[i, header] = dictionary[i]
                  
def rate_of_change(curr, prev):
    roc = (curr - prev) / prev
    return roc
                  
def interval_returns(df):
    returns = {}
    prev = None
    for i, row in df.iterrows():
        curr = row['Adj Close']
        if prev != None:
            change = rate_of_change(curr, prev)
            returns[i] = change
        prev = curr
    return returns

for df in [sec_data, bench_data]:
    make_dict_col(df, interval_returns(df), 'Interval Return')


# In[6]:


# place below cell where last changed occured for bench data
bench_data


# In[7]:


# # # # # # # # # # # # # # # # # # # # #
# 3. Create and add 'Annual Return' col #
# # # # # # # # # # # # # # # # # # # # #

def periods(start, end, interval):
    # 
    if isinstance(start, dt.datetime):
        pass
    else:
        dt_format = lambda d: dt.date(int(d[:4]), int(d[5:7]), int(d[8:10]))
        start = dt_format(start)
        end = dt_format(end)
    #
    periods = {}
    curr_period = 1
    period_start = start
    period_end = None
    #
    a_day = dt.timedelta(days=1)
    a_week = dt.timedelta(weeks=1)
    #
    next_month = lambda date:         date.replace(month=date.month + 1) if date.month < 12         else date.replace(month=1, year=date.year+1)
    #
    while period_end == None or next_month(period_start) - a_day <= end:
        period_end = next_month(period_start) - a_day
        periods[curr_period] = [period_start, period_end]
        period_start = period_end + a_day
        curr_period += 1
    # this caputers the month to date data (ie the latest incomplete month)
    if period_end < end:
        periods[curr_period] = [period_end + a_day, end]
    return periods

monthly_periods = periods(sec_data.index[0], sec_data.index[-1], '1m')

# compute and insert year to date actual returns for comparison to CAPM expected returns
def annual_returns(sec_data):
    
    def one_yr_periods(monthly_periods):
        one_yr_periods = []
        curr_period = 1
        while curr_period + 11 <= len(monthly_periods):
            one_yr = curr_period + 11
            start = monthly_periods[curr_period][0].strftime('%Y/%m/%d')
            end = monthly_periods[one_yr][0].strftime('%Y/%m/%d')
            one_yr_periods += [[start, end]]
            curr_period += 1
        # this captures the (incomplete) MTD data
        last_here = one_yr_periods[-1][1]
        last_there = list(monthly_periods.values())[-1][1].strftime('%Y/%m/%d')
        if last_here != last_there:
            start = monthly_periods[curr_period][0].strftime('%Y/%m/%d')
            end = last_there
            one_yr_periods += [[start, end]]
        return one_yr_periods

    one_yr_periods = one_yr_periods(monthly_periods)
    print(one_yr_periods)
    
    annual_returns = {}
    for date_range in one_yr_periods:
        start = date_range[0]
        end = date_range[1]
        curr = None
        prev = None
        for i, row in sec_data.iterrows():
            if i == start:
                prev = row['Adj Close']
            elif i == end:
                curr = row['Adj Close']
        if curr != None and prev != None:
            annual_returns[end] = (curr-prev)/prev
    for i, row in sec_data.iterrows():
        if i in list(annual_returns.keys()):
            ret = annual_returns[i]
    make_dict_col(sec_data, annual_returns, '1yr Return')
        
annual_returns(sec_data)


# In[8]:


# # # # # # # # # # # # # # # # # # #
# 4. Create and add '3yr Beta' col  #
# # # # # # # # # # # # # # # # # # #

def beta(sec_data, bench_data):
    # create list of returns on security and benchmark
    sec_returns = list(sec_data['Interval Return'])
    bench_returns = list(bench_data['Interval Return'])
    # calulate beta for given returns, while accounting for first None entry
    mean = lambda l: sum(l[1:]) / len(l[1:])
    xbar = mean(sec_returns)
    ybar = mean(bench_returns)
    xs = []
    ys = []
    for i in range(1, len(sec_returns)):
        xs += [sec_returns[i] - xbar]
        ys += [bench_returns[i] - ybar]
    over = 0
    under = 0
    for i in range(0, len(xs)):
        over += xs[i] * ys[i]
        under += ys[i]**2
    beta = over / under
    return beta

def three_yr_periods(monthly_periods):
    three_yr_periods = []
    curr_period = 1
    while curr_period + 35 <= len(monthly_periods):
        three_yrs = curr_period + 35
        start = monthly_periods[curr_period][0].strftime('%Y/%m/%d')
        end = monthly_periods[three_yrs][0].strftime('%Y/%m/%d')
        three_yr_periods += [[start, end]]
        curr_period += 1
    # this captures the (incomplete) MTD data
    last_here = three_yr_periods[-1][1]
    last_there = list(monthly_periods.values())[-1][1].strftime('%Y/%m/%d')
    if last_here != last_there:
        start = monthly_periods[curr_period][0].strftime('%Y/%m/%d')
        end = last_there
        three_yr_periods += [[start, end]]
    return three_yr_periods

three_yr_periods = three_yr_periods(monthly_periods)

def three_yr_betas(sec_data, bench_data, three_yr_periods):
    betas = {}
    for date_range in three_yr_periods:
        # select data for the 3yr period
        sec_data_3yr = sec_data.loc[date_range[0]: date_range[1]]
        bench_data_3yr = bench_data.loc[date_range[0]: date_range[1]]
        # compute beta for the period
        betax = beta(sec_data_3yr, bench_data_3yr)
        # store beta in betas with the corresponding date as key
        betas[date_range[1]] = betax
    '''
    # create empty col for '3yr Beta'
    nrows = sec_data.shape[1]
    header = '3yr Beta'
    sec_data.insert(nrows, header, None, True)
    # update '3yr Beta' values by comparing dates in betas with sec_data
    for i, row in sec_data.iterrows():
        # format_i = i.strftime('%m/%d/%Y')
        # if format_i in list(betas.keys()):
        if i in list(betas.keys()):
            sec_data.at[i, '3yr Beta'] = betas[i]
    '''        
    make_dict_col(sec_data, betas, '3yr Beta')

d = three_yr_betas(sec_data, bench_data, three_yr_periods)


# In[9]:


# place below cell where last changed occured for sec data
sec_data


# In[10]:


# # # # # # # # # # # # # # # # #
# 5. Create and add 'CAPM' col  #
# # # # # # # # # # # # # # # # #

# extract expected market return (ERm) = avg return in bench_data before dropping first three years
# ERm is an input into CAPM
bench_returns = list(bench_data['Interval Return'])
intervals_per_year = 12
ERm = intervals_per_year * sum(bench_returns[1:]) / len(bench_returns[1:])

# gets rid of the first 3 years of (beta input) data where beta = None
#   since beta is an input into CAPM, which is what this is ALLL ABOUTTT
for i, row in sec_data.iterrows():
    if type(row['3yr Beta']) is not float:
        sec_data = sec_data.drop([i])

def capm(Bi, Rf=Rf, ERm=ERm):
    # market risk premium
    Rm = ERm - Rf
    capm = Rf + Bi * Rm
    return capm

print(sec_data)

def capm_col(sec_data):
    # compute and insert 'CAPM' values
    capmx = {}
    for i, row in sec_data.iterrows():
        beta = row['3yr Beta']
        capmx[i] = capm(beta)
    print(capmx)
    make_dict_col(sec_data, campx, 'CAPM')
    '''
    nrows = sec_data.shape[1]
    header = 'CAPM'
    sec_data.insert(nrows, header, capmx, True)
    '''
        
capm_col(sec_data)
sec_data


# In[ ]:




