import time
import pyupbit
import datetime
import pandas as pd

with open('upbit_API_key.txt') as f :
    lines = f.readlines()
    key = lines[0].strip()
    secret = lines[1].strip()
    upbit = pyupbit.Upbit(key, secret)

def get_my_ticker() :
    my_ticker =[]
    balances = upbit.get_balances()
    for balance in balances[1:] :
        ticker = balance['currency']
        my_ticker.append("KRW-"+ticker)
    return my_ticker

def get_target_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day")
    if len(df) < 6 :
        return 1000000000
    target_price = df.iloc[-2]['close'] + (df.iloc[-2]['high'] - df.iloc[-2]['low'])*0.5
    return target_price

def select_ticekr() :    
    interesting_ticker =[]
    volume =[]vi 
    for ticker in pyupbit.get_tickers(fiat='KRW') :
        current_price = pyupbit.get_current_price(ticker)
        target_price = get_target_price(ticker)

        if (get_ma5(ticker)) < current_price) and (current_price > target_price) :
            interesting_ticker.append(ticker)
            volume.append(pyupbit.get_ohlcv(ticker).iloc[-1,-1])
    buy_list = pd.DataFrame({'ticker':interesting_ticker,
                             'volume':volume})
    print(buy_list)

    if len(buy_list) < 3 :
        pick_ticker = buy_list
        ratio = list(reversed(range(len(buy_list))))
    else :
        pick_ticker = buy_list.sort_values('volume', ascending = False)[:3]
        ratio = [2,1,0]
    return (pick_ticker.ticker, ratio) 

def buy_crypto_currency(ticker, ratio) :
    krw = upbit.get_balance()
    orderbook = pyupbit.get_orderbook(ticker)[0]
    sell_price = orderbook["orderbook_units"][0]['ask_price']
    unit = (krw/ratio) / float(sell_price)
    pyupbit.buy_market_order(ticker, unit)
    print("successed buy order")
    
def sell_crypto_currency(ticker) :
    unit = upbit.get_balance(ticker)
    pyupbit.sell_market_order(ticker, unit)
    print('successed sell order')


def get_start_time(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma5(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day")
    if len(df) < 6 :
        return 1000000000
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

while True :
    try :
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        
        if start_time < now < end_time - datetime.timedelta(seconds=10) :
            pick_ticker, ratio = select_ticker()
            print(pick_ticker)
            for ticker,ratio in zip(pick_ticker, ratio) :
                ratio = ratio + 1
                buy_crypto_currency(ticker,ratio)
            
        my_ticker = get_my_ticker()
        print(my_ticker)
        for ticker in my_ticker :
            sell_crypto_currency(ticker)
                        
    except Exception as e:
        print(e)
        time.sleep(1)        
       
  
    
