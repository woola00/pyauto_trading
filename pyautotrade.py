import time
import pybithumb
import datetime
import pandas as pd

with open('bithumb_API_key.txt') as f :
    lines = f.readlines()
    key = lines[0].strip()
    secret = lines[1].strip()
    bithumb = pybithumb.Bithumb(key, secret)

#def get_my_ticker() :
#    my_ticker = []
#    for ticker in pybithumb.get_tickers() :
#        if bithumb.get_balance(ticker)[0] != 0 :
#            my_ticker.append(ticker)
#        time.sleep(0.1)
#    return my_ticker
    
def get_target_price(ticker) :
    df = pybithumb.get_ohlcv(ticker)
    if len(df) < 6 :
        return 100000000000
    yesterday = df.iloc[-2]
    today_open = yesterday['close']
    yesterday_high = yesterday['high']
    yesterday_low = yesterday['low']
    target = today_open + (yesterday_high - yesterday_low) * 0.5
    return target

def buy_crypto_currency(ticker, ratio) :
    krw = bithumb.get_balance(ticker)[2]*0.7
    orderbook = pybithumb.get_orderbook(ticker)
    sell_price = orderbook['asks'][0]['price']
    unit = (krw/ratio) / float(sell_price)
    bithumb.buy_market_order(ticker, unit)
    print("sucessed buy order")

def sell_crypto_currency(ticker) :
    unit = bithumb.get_balance(ticker)[0]
    bithumb.sell_market_order(ticker, unit)
    print("sucessed sell order")

def get_yesterday_ma5(ticker) :
    df = pybithumb.get_ohlcv(ticker)
    if len(df) < 6 :
        return 100000000000
    close = df['close']
    ma = close.rolling(window=5).mean()
    return ma[-2]

def select_ticker() :
    interesting_ticker = []
    volume = []
    my_ticker = []
    
    for ticker in pybithumb.get_tickers() :
        amount = bithumb.get_balance(ticker)[0]
        current_price = pybithumb.get_current_price(ticker)
        krw_ticker = amount * current_price
        target_price = get_target_price(ticker)
        
        if krw_ticker > 5000 :
            my_ticker.append(ticker)

        if ticker not in my_ticker :
            if (get_yesterday_ma5(ticker) < current_price) and (current_price > target_price) :
                interesting_ticker.append(ticker)
                volume.append(pybithumb.get_ohlcv(ticker).iloc[-1,-1])

    buy_list = pd.DataFrame({'ticker': interesting_ticker, 'volume' : volume})
    buy_list.sort_values('volume', ascending = False, inplace=True)
    print(buy_list)

    if len(buy_list) < 3 :
        pick_ticker = buy_list
        ratio = list(reversed(range(len(buy_list))))
    else :
        pick_ticker = buy_list[:3]
        ratio = [2,1,0]
    return (pick_ticker.ticker, ratio, my_ticker)

now = datetime.datetime.now()
mid_night = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)

while True :
    try :
        pick_ticker, ratio, my_ticker = select_ticker()
       
        for ticker,ratio in zip(pick_ticker, ratio) :
            ratio = ratio + 1
            buy_crypto_currency(ticker,ratio)
        
        now = datetime.datetime.now()
        
        if mid_night < now < mid_night + datetime.timedelta(seconds=150) :
            mid_night = datetime.datetime(now.year, now.month, now.day) + datetime.timedelta(days=1)
            for ticker in my_ticker :
                sell_crypto_currency(ticker)
                time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
