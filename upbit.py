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
    ticker =[]
    buy_price =[]
    balances = upbit.get_balances()
    for balance in balances[1:] :
        ticker.append(balance['currency'])
        buy_price.append(balance['avg_buy_price'])

    my_ticker = pd.DataFrame({'ticker':ticker,'buy_price':buy_price})
    my_ticker = my_ticker.loc[(my_ticker.buy_price != '0')]
    return my_ticker

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else: return 0
    return 0

def get_target_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day")
    if len(df) < 6 :
        return 1000000000
    target_price = df.iloc[-2]['close'] + (df.iloc[-2]['high'] - df.iloc[-2]['low'])*0.5
    return target_price

def buy_crypto_currency(ticker, ratio) :
    krw = upbit.get_balance() * 0.1
    unit = krw/ratio
    order = upbit.buy_market_order(ticker, unit)
    print(order)
    
def sell_crypto_currency(ticker,buy_price,up,down) :
    price = pyupbit.get_current_price('KRW'+ticker)
    if (price > buy_price*up) & (price < buy_price*down) :    
        unit = upbit.get_balance(ticker)
        order = upbit.sell_market_order('KRW'+ticker, unit)
        print(order)

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

def select_ticker() :  
    interesting_ticker =[]
    volume =[] 
    for ticker in pyupbit.get_tickers(fiat='KRW') :
        pre_p = pyupbit.get_current_price(ticker)
        tg_p = get_target_price(ticker)
        
        if (pre_p > get_ma5(ticker)) and (pre_p > tg_p) :
            interesting_ticker.append(ticker)
            volume.append(pyupbit.get_ohlcv(ticker).iloc[-1,-2])
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


while True :
    try :
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        
        #if start_time < now < end_time - datetime.timedelta(seconds=10) :
        pick_ticker, ratio = select_ticker()
        my_ticker = get_my_ticker()
        print('pick_ticker : ',pick_ticker)
        print('my_picker : ',my_ticker)        
        for ticker,ratio in zip(pick_ticker, ratio) :
            ratio = ratio + 1
            if ticker not in my_ticker :
                buy_crypto_currency(ticker,ratio)
                time.sleep(0.1)

        
        
        for ticker in my_ticker :
            sell_crypto_currency(ticker.ticker, ticker.buy_price, up=1.1, down=0.97)
            time.sleep(0.1)
                        
    except Exception as e:
        print('error: ',e)
        time.sleep(1)        
       
  
    

