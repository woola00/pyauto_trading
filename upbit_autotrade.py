import time
import pyupbit
import datetime

access = "FbldTXxXqiHmuQkXKazGSGEJCXzM7JxMlSbc6bIs"
secret = "aDuiawxGiN1ckwCGuuOchXu7HOCT4QaarQEXk72U"


def get_my_ticker() :
    my_ticker =[]
    balances = upbit.get_balances()
    for balance in balances[1:] :
        ticker = balance['currency']
        my_ticker.append("KRW-"+ticker)
    return my_ticker

def get_target_price(ticker):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day")
    if len(df) < 6 :
        return 1000000000
    target_price = df.iloc[-2]['close'] + (df.iloc[-2]['high'] - df.iloc[-2]['low'])*0.5
    return target_price

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
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma5(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day")
    if len(df) < 6 :
        return 1000000000
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma15 = get_ma15("KRW-BTC")
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
        else:
            btc = get_balance("BTC")
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
        
       
interesting_ticker =[]
volume =[]

for ticker in pyupbit.get_tickers(fiat='KRW') :
    current_price = pyupbit.get_current_price(ticker)
    target_price = get_target_price(ticker)
    
    if (get_ma5(ticker)) < currnet_price) and (current_price > target_price) :
        interesting_ticker.append(ticker)
        volume.append(pyupbit.get_ohlcv(ticker).iloc[-1,-1])
    buy_list = pd.DataFrame({'ticker':interesting_ticker,
                             'volume':volume})
    print(buy_list)
    
    if len()
