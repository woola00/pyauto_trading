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
    excepted_ticker = ['CHL','BLACK','HORUS','ADD','USDT','MEETONE','BAY','RCN','SLS','IQ','ONIT']
    ticker = []
    buy_price = []
    unit = []
    current_price = []
    balances = upbit.get_balances()
    for balance in balances[1:] :
        currency = balance['currency']
        if currency not in excepted_ticker :
            ticker.append('KRW-'+currency)
            buy_price.append(balance['avg_buy_price'])
            unit.append(balance['balance'])
            current_price.append(pyupbit.get_current_price('KRW-'+currency))
        time.sleep(0.1)
    my_ticker = pd.DataFrame({'ticker':ticker,
                              'buy_price':buy_price,
                              'balance':unit,
                              'current_price':current_price })
    my_ticker['krw_balance'] = my_ticker.current_price.astype(float) * my_ticker.balance.astype(float)
    my_ticker = my_ticker.loc[my_ticker.krw_balance > 5000]
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
    target_price = df.iloc[-2]['close'] + abs(df.iloc[-2]['close'] - df.iloc[-2]['open'])*0.5
    return target_price

def get_sell_tg_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="day")
    if len(df) < 6 :
        return 1000000000
    target_price = df.iloc[-2]['close']# - abs(df.iloc[-2]['close'] - df.iloc[-2]['open'])*0.3
    return target_price

def buy_crypto_currency(ticker, krw) :
    if krw > 4000000 : unit = krw*0.06
    elif krw > 3000000 : unit = krw * 0.08
    elif krw > 2000000 : unit = krw * 0.09
    elif krw > 1000000 : unit = krw * 0.2
    else : unit = krw * 0.9
    order = upbit.buy_market_order(ticker, unit)
    print('##result:\n',order)
    
def sensing_crypto(up,down) :
    my_ticker = get_my_ticker()
    buy_price = my_ticker.buy_price.astype(float)
    for ticker, buy_price in zip(my_ticker.ticker,buy_price):
        price = pyupbit.get_current_price(ticker)
        if (price > buy_price*up)|(price < buy_price*down) :    
            unit = upbit.get_balance(ticker)
            print('Trying sell ticker :', ticker)
            order = upbit.sell_market_order(ticker, unit)
            print('##result:\n',order)
        time.sleep(0.1)

def all_crypto_sell(ticker) :
    my_ticker = get_my_ticker()
    for ticker in my_ticker.ticker :
        unit = upbit.get_balance(ticker)
        order = upbit.sell_market_order(ticker, unit)
        time.sleep(0.1)
    
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

def time_ratio() :
    now = datetime.datetime.now()
    start = str(get_start_time('KRW-BTC'))
    start = datetime.datetime.strptime(start,'%Y-%m-%d %H:%M:%S')
    delta = (now - start).total_seconds()
    ratio = (24*60*60) / delta
    return ratio

def get_tg_volume(ticker) :
    volume = pyupbit.get_ohlcv(ticker).iloc[:,-2] 
    now_volume = volume[-1]*time_ratio()
    tg_volume = volume[-2] * 2
    return now_volume, tg_volume

def select_ticker() :
    interesting_ticker =[]
    value =[] 
    my_ticker = get_my_ticker()
    for ticker in pyupbit.get_tickers(fiat='KRW') :
        cur_p = pyupbit.get_current_price(ticker)
        tg_p = get_target_price(ticker)
        now_vol, tg_vol = get_tg_volume(ticker)
        if ticker not in list(my_ticker.ticker) :
            if (cur_p > get_ma5(ticker)) and (cur_p > tg_p) and (now_vol > tg_vol) :
                interesting_ticker.append(ticker)
                value.append(pyupbit.get_ohlcv(ticker).iloc[-1,-1])
                time.sleep(0.1)
    buy_list = pd.DataFrame({'ticker':interesting_ticker,
                             'volume':value})
    
    pick_ticker = buy_list.sort_values('volume', ascending = False)
    ratio = list(reversed(range(len(pick_ticker))))
    
    return (pick_ticker.ticker, ratio, my_ticker)

today_buy_list = ['KRW-THETA','KRW-ENJ','KRW-CRE','KRW-LSK','KRW-MTL','KRW-STX','KRW-FLOW','KRW-GAS','KRW-TON',
                  'KRW-SBD','KRW-MANA','KRW-CBK','KRW-MFT','KRW-SAND','KRW-XRP','KRW-STRAX','KRW-AXS']
while True :
    try :
        now = datetime.datetime.now()
        print('STRAT :',now)        
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        krw = upbit.get_balance('KRW')
        if start_time < now < end_time - datetime.timedelta(seconds=450) :
            if krw > 1000000 :
                pick_ticker, ratio, my_ticker = select_ticker()
                print('pick_ticker : \n',pick_ticker) 
                for ticker,ratio in zip(pick_ticker, ratio) :
                    ratio = ratio + 1
                    krw = upbit.get_balance('KRW')
                    if ticker not in today_buy_list :
                        buy_crypto_currency(ticker,krw)
                        today_buy_list.append(ticker)
                        time.sleep(0.1)
                    print('Buy Complete :',datetime.datetime.now())
                    print('today buy :', today_buy_list)
                sensing_crypto(up=1.2, down=0.9)
                print('sensing complete :', datetime.datetime.now())
            else :
                sensing_crypto(up=1.2, down=0.9)
                print('sensing complete :', datetime.datetime.now())
        else :
            all_cryto_sell()
            today_buy_list = []
            
    except Exception as e:
        print('error: ',e)
        time.sleep(1)            
