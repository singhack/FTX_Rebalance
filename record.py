import pandas as pd
from exchange import Exchange
import datetime as dt
import time


# ### Config ############
sub_account =Exchange().sub_account
LOGFILE =Exchange().LOGFILE
last_transaction =Exchange().last_transaction
date_str = dt.datetime.today().strftime('@%d_%m_%y')
filen=   f'Equity_{sub_account+date_str}.csv'
path_log = f'log/{filen}' ###Access Foldes
filen = path_log
last_transaction  = 10


class Record():
    def __int__(self):
        self.ex = Exchange()
        self.sub_account = Exchange().sub_account

    def get_trade_history(self, pair,last_transaction=10):
        pair = pair
        trade_history = pd.DataFrame(Exchange().exchange.fetchMyTrades(pair, limit=last_transaction),
                                     columns=['id', 'timestamp', 'datetime', 'symbol', 'side', 'price', 'amount',
                                              'cost',
                                              'fee'])
        cost = []
        for i in range(len(trade_history)):
            cost.append((trade_history['fee'][i]['cost']))  # ใน fee เอาแค่ cost
        trade_history['fee'] = cost
        return trade_history


    def get_last_id(self, pair):
        pair = pair
        trade_history = self.get_trade_history(pair)
        last_trade_id = (trade_history.iloc[:last_transaction]['id'])

        return last_trade_id


    def checkDB(self,pair):
        pairx = pair.split('/')[0]
        log_trade = f"{Exchange().sub_account}_{pairx}.csv"

        try:
            tradinglog = pd.read_csv(log_trade)
            print('DataBase Exist Loading DataBase....')
        except:
            tradinglog = pd.DataFrame(
                columns=['id', 'timestamp', 'datetime', 'symbol', 'side', 'price', 'amount', 'cost', 'fee'])
            tradinglog.to_csv(log_trade, index=False)
            print("Database Created")
        return tradinglog

    def update_trade_log(self,pair):
        # pair = pair
        pairx = pair.split('/')[0]
        log_trade = f"{Exchange().sub_account}_{pairx}.csv"

        ### Read DB
        tradinglog = pd.read_csv(log_trade) ####
        ### Fetch order
        trade_history = self.last_transcation(pair)  # symbols
        tradinglogg = pd.concat([tradinglog, trade_history], ignore_index=True)
        tradinglogg['id'] = tradinglogg['id'].astype('int64')  ### Convert id to int

        tradinglogg = tradinglogg.drop_duplicates('id')
        tradinglogg.to_csv(log_trade, index=False)

    def last_transcation(self,pair, limitt=100):
        since_trade = dt.datetime.now() - dt.timedelta(days=30)  ### Last 5 days
        since_str = since_trade.strftime('%Y-%m-%d')
        timestamp = since_trade.timestamp() * 1000
        transcation = pd.DataFrame(Exchange().exchange.fetchMyTrades(pair, since=timestamp, limit=limitt),
                                   columns=['id', 'timestamp', 'datetime', 'symbol', 'side', 'price', 'amount', 'cost',
                                            'fee'])
        transcations = []
        for i in range(len(transcation)):
            transcations.append((transcation['fee'][i]['cost']))  # ใน fee เอาแค่ cost
        transcation['fee'] = transcations
        return transcation

    # def update_trade_log(self, pair):
    #     pair = pair
    #     pairx = pair.split('/')[0]
    #     tradinglog = pd.read_csv(f"{Exchange().sub_account}_{pairx}.csv")
    #     last_trade_id = self.get_last_id(pair)
    #     trade_history = self.get_trade_history(pair)
    #
    #     for i in last_trade_id: ### Check last trade in csv file
    #         tradinglog = pd.read_csv(f"{Exchange().sub_account}_{pairx}.csv")
    #         trade_history = self.get_trade_history(pair)
    #
    #         if int(i) not in tradinglog.values:  ### append last trade to csv
    #             print(i not in tradinglog.values)
    #             last_trade = trade_history.loc[trade_history['id'] == i]
    #             tradinglog = pd.concat([last_trade, tradinglog], ignore_index=True)
    #             tradinglog.to_csv(f"{Exchange().sub_account}_{pairx}.csv", index=False)
    #             # print('Recording Trade ID : {}'.format(i))
    #         else:
    #             # print(f'{pairx} Trade Already record')
    #             pass

    def get_report_equity(self,token_name): ##### asset in config data

        equity = pd.DataFrame(columns=token_name)
        equity['date'] = pd.Series(Exchange().get_time())
        wallet = Exchange().get_wallet()
        port = pd.DataFrame(wallet)

        try:
            hold_token_value = 0.0
            for asset_name in token_name:  ### extract coin[list] to str
                equity[asset_name] = round(float(Exchange().get_token_value(asset_name)), 3)
                equity[asset_name + '_price'] = float(Exchange().get_price(asset_name + '/USD'))
                hold_unit = float(Exchange().get_token_unit(asset_name))
                equity[asset_name + '_unit'] = hold_unit
                hold_token_value += equity[asset_name].values
        except Exception as e:
            equity[asset_name] = 0.0
            print(str(e))

        try:
            equity['Cash'] = round(float(Exchange().get_cash()), 3)
            equity['Equity'] = hold_token_value + equity['Cash'].values
            for coins in token_name:  ### extract coin[list] to str
                equity['Exposure' + coins] = ((equity[coins].sum()) / (equity['Equity'].values))
        except Exception as e:
            equity['Exposure' + coins] = 0.0
            print(str(e))

        # equity.set_index('date',inplace=True)
        equity['Exposure_ALL'] = round(((equity[token_name].sum(1) + 2) / (equity['Equity'].values)), 3)

        return equity

    def get_report_equity1(self): ### all_asset in wallet
        wallet = Exchange().get_wallet()
        token_name = []
        for i in range(len(wallet)):
            if ('USD' not in wallet[i]['coin']):
                coin_name = (wallet[i]['coin'])
                token_name.append(coin_name)
                equity = pd.DataFrame(columns=token_name)
                equity['date'] = pd.Series(Exchange().get_time())
        try:
            hold_token_value = 0.0
            for i in range(len(token_name)):
                if ('USD' not in token_name[i]) and ('USDT' not in token_name[i]):
                    equity[token_name[i]] = round(float(Exchange().get_token_value(token_name[i])), 3)
                    equity[token_name[i] + '_price'] = float(Exchange().get_price(token_name[i] + '/USD'))
                    hold_unit = float(Exchange().get_token_unit(token_name[i]))
                    equity[token_name[i] + '_unit'] = hold_unit
                    hold_token_value += equity[token_name[i]].values
        except Exception as e:
            equity[token_name[i]] = 0.0
            print(str(e))

        try:
            equity['Cash'] = round(float(Exchange().get_cash()), 3)
            equity['Equity'] = hold_token_value + equity['Cash'].values

            for coins in token_name:  ### extract coin[list] to str
                equity['Exposure' + coins] = ((equity[coins].sum()) / (equity['Equity'].values))

        except Exception as e:
            equity['Exposure' + coins] = 0.0
            print(str(e))

            # equity.set_index('date',inplace=True)
        equity['Exposure_ALL'] = round(((equity[token_name].sum(1) + 2) / (equity['Equity'].values)), 3)
        return equity

    def save_database(self,token_name):
        try:
            equity_db = pd.read_csv(filen)
            equity_db = equity_db.append(self.get_report_equity(token_name))

            equity_db.set_index('date', inplace=True)
            equity_db.to_csv(filen)
            return equity_db
        except:
            equity_db = self.get_report_equity(token_name)
            equity_db.set_index('date', inplace=True)
            equity_db.to_csv(filen)
            return equity_db

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

    #
    def check_pnl(self,token_name):
        first_entry = {}
        # price = {}
        try:
            equity_db = pd.read_csv('entry_price_log.csv')
            first_entry[token_name] = equity_db[equity_db['symbol'] == token_name]['entry'].values
            # first_entry[token_name] = equity_db[equity_db['symbol'] == token_name]['entry'][0]
            # price[token_name] = equity_db[equity_db['symbol'] == token_name]['price'][0]
            # diff = (price[token_name] - first_entry[token_name])
            return first_entry
        except:
            symbols = token_name + '/USD'
            first_entry[token_name] = Exchange().get_price(symbols)
            print('**** None Database *** ')
            return first_entry



rec= Record()
ex = Exchange()

# rec.update_trade_log('DOGEBEAR2021/USD')

#### TEST ###
# print(rec.check_pnl('XRP'))
# print(ex.sub_account)
# rec.checkDB(pair)
# rec.checkDB(pairx)
# rec.update_trade_log(pairx)
# rec.save_database(token_name)
# equity = rec.get_report_equity(token_name)
# print(equity)
# # rec.get_report_equity(['XRP'])
# rec =Record()
# print(rec.get_report_equity(pair))
# rec.log('ok')
# equity_db = pd.read_csv(filen)
# first_entry = {}
# first_entry['TEST'] = equity_db['XRP' + '_price'][0]
# # first_entry = first_entry
# # symbols = token_name + '/USD'
# print(first_entry)
# print(type(equity_db['XRP' + '_price'][0]))
# print(rec.check_pnl('XRP'))