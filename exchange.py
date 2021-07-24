import ccxt
import datetime as dt
import pandas as pd
import time
import requests
import decimal
import simplejson as json


pd.set_option('display.max_columns', 10)

def read_config():
    with open('config.json') as json_file:
        return json.load(json_file)

###############
# ### Exchange ############
config = read_config()
apiKey= config["apiKey"]
secret = config["secret"]
sub_account = config["sub_account"]
LOGFILE = config["LOGFILE"]
token_line = config["token_line"]

# last_transaction = config["last_transaction"]


last_transaction  = 10 ## record last x  items in history



class Exchange:
    def __init__(self):
            self.apiKey = apiKey
            self.secret = secret
            self.sub_account = sub_account
            self.LOGFILE = LOGFILE
            self.last_transaction = last_transaction
            # self.Record=Record()
            self.exchange = ccxt.ftx({
                'verbose': False,
                'apiKey': apiKey,
                'secret': secret,
                'enableRateLimit': True,
                'headers': {
                    'FTX-SUBACCOUNT': sub_account,
                },
            })
            # exchange =     self.exchange
    def get_wallet(self):
            try:
                wallet = self.exchange.privateGetWalletBalances()['result']
                return wallet
            except:
                pass
    def get_time(self):  # เวลาปัจจุบัน
        time_now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return time_now

    def get_cash(self):
        try :
            wallet = self.exchange.privateGetWalletBalances()['result']
            for t in wallet:
                if t['coin'] == 'USD':
                    cash = float(t['availableWithoutBorrow'])
            return cash
        except:
            pass

    def get_token_value(self,token_name):
        try:
            usd_value = []
            wallet = self.exchange.privateGetWalletBalances()['result']
            for token in wallet:
                if token['coin'] == token_name:
                    usd_value = token['usdValue']
            return float(usd_value)
        except :
            pass

    def get_price(self,token_name):
        price = self.exchange.fetch_ticker(token_name)['last']
        return float(price)

    def get_token_unit(self,token_name):
        usd_value = []
        wallet = self.exchange.privateGetWalletBalances()['result']
        for token in wallet:
            if token['coin'] == token_name:
                unit = token['availableWithoutBorrow']
        return float(unit)

    def get_minimum_size(self,token_name):
        minimum_size = self.exchange.fetch_ticker(token_name)['info']['minProvideSize']
        return float(minimum_size)

    def get_min_trade_value(self,token_name):
        min_trade_value = float(self.exchange.fetch_ticker(token_name)['info']['sizeIncrement']) * float(
            self.get_price(token_name))
        return float(min_trade_value)

    def get_ask_price(self,token_name):
        ask_price = self.exchange.fetch_ticker(token_name)['ask']
        return float(ask_price)

    def get_bid_price(self,token_name):
        bid_price = self.exchange.fetch_ticker(token_name)['bid']
        return float(bid_price)

    def get_mid_price(self,token_name):
        bids = self.get_bid_price(token_name)
        asks = self.get_ask_price(token_name)
        mid_price = (bids + asks) / 2
        return float(mid_price)

    def get_pending_buy(self,token_name):
        pending_buy = []
        for i in self.exchange.fetch_open_orders(token_name):
            if i['side'] == 'buy':
                pending_buy.append(i['info'])
        return pending_buy

    def get_pending_sell(self,token_name):
        pending_sell = []
        for i in self.exchange.fetch_open_orders(token_name):
            if i['side'] == 'sell':
                pending_sell.append(i['info'])
        return pending_sell

    def get_digit(self,token_name):
        a = (self.exchange.fetch_ticker(token_name)['info']['priceIncrement'])
        d = (decimal.Decimal(a))
        # decimal_digit  = d.as_tuple().exponent
        print(d)
        return d
        # return decimal_digit

    def get_step_price(self,token_name):
        step_price = self.exchange.fetch_ticker(token_name)['info']['priceIncrement']
        return float(step_price)

    ############# Crete order  , cancle , sendline ##################################
    def crete_order(self,symbols, side, unit, price):
        try:
            orderID = self.exchange.create_order(symbols, 'limit', side, unit, price)["info"]["id"]
            unit = round(unit)
            usdValue = round(price*unit,3)
            msg = f'Open {side} ,{symbols}\n Price: {price} Unit :{unit} Usd {usdValue}$'
            print(msg)
            self.sendtext(msg)
            # orderID = exchange.create_order(symbols,'limit',side,unit,price)["info"]["id"]
            # print(f'Open Sell {orderID},{symbols}:{price}@{unit}')
            ###log InvalidOrder
            return orderID
        except ccxt.InvalidOrder as e:
            dollar_round = float(round(1 / price, 2))
            self.log("InvalidOrder " + str(e) + "Adjust" + str(dollar_round) + '$')
            msg_buy = f'{symbols, side, dollar_round, price,}'
            orderID = self.exchange.create_order(symbols, 'limit', side, dollar_round, price)["info"]["id"]
            print(msg_buy)
            # time.sleep(5)
            return orderID

        except ccxt.NetworkError as e:
            print(str(e))

            self.log("NetworkError , " + str(e))
            self.log(str(e))
        except ccxt.ExchangeError as e:
            print(str(e))
            self.log(str(e))
        return orderID

    def cancle_order_all(self):
        count_order = len(self.exchange.fetchOpenOrders())
        if count_order >= 1:
            order_pending = pd.DataFrame(self.exchange.fetchOpenOrders(), columns=['id'])
            for i in order_pending['id']:
                try:
                    print(f'Cancle pending order :{i}')
                    cancle = self.exchange.cancel_order(i)
                    time.sleep(0.5)
                except Exception as e:
                    print(str(e))
        else:
            pass
            print('No Pendding Order')

    def cancel_order(self,order_id):
        try :
            self.exchange.cancel_order(order_id)
            print("Order ID : {} Successfully Canceled".format(order_id))
        except Exception as e:
            print(str(e))
    # hold_unit = round(float(hold_unit.astype(float)), 5)

    def sendtext(self,message):
        try:
            token = token_line  ### ใส่ Token ตรงนี้ครับผม
            url = 'https://notify-api.line.me/api/notify'
            header = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}
            command = {'message': message}
            return requests.post(url, headers=header, data=command)
        except Exception as e:
            print(e)

    def log(self,msg):
        timestamp = dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        s = "[%s] %s" % (timestamp, msg)
        print(s)
        try:
            f = open(LOGFILE, "a")
            f.write(s + "\n")
            f.close()
        except:
            pass


ex = Exchange()
# ex.sendtext('Sawadd D kub')
# ex.get_cash()
# wallet = ex.get_wallet()
# df = pd.DataFrame(wallet)
# cols =['coin','availableWithoutBorrow','usdValue']
# df = df[cols]
# df[['usdValue','availableWithoutBorrow']].astype(float)
# trade_history = ex.get_trade_history('XRP/USD')
# print(trade_history)
#
#
#
# ex.update_trade_log('SOL/USD')


