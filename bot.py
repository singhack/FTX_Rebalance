import datetime

from exchange import Exchange
from record import Record
import pandas as pd
import numpy as np
import time
import sys
import simplejson as json
import warnings
import schedule

warnings.filterwarnings("ignore")

def read_config():
    with open('config.json') as json_file:
        return json.load(json_file)

config = read_config()
token_name= config["symbols"]
fix_value_lst = config["fix_value"]
threshold_buy = config["threshold_buy"]
threshold_sell = config["threshold_sell"]
trigger_stop_sell = config["trigger_stop_sell"]
trigger_stop_buy = config["trigger_stop_buy"]

gap = config["gap"]
cdBot = config["cd"]
entry_list = config["entry_list"]





#### Join Dict #####
string = '/USD'
symbols_trades = [s + string for s in token_name]
token_fix_value = {token_name[i]: fix_value_lst[i] for i in range(len(token_name))}
trade_dict = {token_name[i]: symbols_trades[i] for i in range(len(token_name))}

threshold_dict_buy = {token_name[i]: threshold_buy[i] for i in range(len(token_name))}
threshold_dict_sell = {token_name[i]: threshold_sell[i] for i in range(len(token_name))}

threshold_stop_sell= {token_name[i]: trigger_stop_sell[i] for i in range(len(token_name))}
threshold_stop_buy = {token_name[i]: trigger_stop_buy[i] for i in range(len(token_name))}

entry_dict= {token_name[i]: entry_list[i] for i in range(len(token_name))}

rec= Record()
ex = Exchange()


def Check_asset(sendding_buy=False):
    total_asset= 0.0
    wallet = ex.get_wallet()
    cash = ex.get_cash()
    asset_in_wallet = [item['coin'] for item in wallet]
    Time = ex.get_time()

    print("#### Setting ####")
    print('Time : {}'.format(Time))
    print(f'Your Remaining Balance : {cash:.3f}')
    for item in wallet:
        asset_value = round(float(item['usdValue']), 2)
        total_asset += asset_value
    print(f'Your Total Asset Value is : {total_asset:.3f}')
    print("-------------------------")

    for asset_name, fixed_value in token_fix_value.items():  ##asset_name = XRP
        if asset_name in asset_in_wallet:
            # wallet = ex.getBalance()
            port = pd.DataFrame(wallet)
            buy_reb_threshold = threshold_dict_buy[asset_name]  ## buy %
            sell_reb_threshold = threshold_dict_sell[asset_name]  ## buy %
            buy_threshold = fixed_value - (fixed_value * buy_reb_threshold)
            sell_threshold = fixed_value + (fixed_value * sell_reb_threshold)  ###
            hold_value = port.loc[port['coin'] == asset_name]['usdValue'].values
            hold_value = round(float(hold_value.astype(float)), 2)
            print(f'Bot - {asset_name}    Fix  {fixed_value} $  :  Hold {hold_value} $ ')
            print(f' Buy Target {buy_threshold}---{buy_reb_threshold * 100}% : Sell Target {sell_threshold}---{sell_reb_threshold * 100}% ')

            print('.-' * 50)

        elif asset_name not in asset_in_wallet:
            #### parameter ####
            cash = float(ex.get_cash())
            pair = trade_dict[asset_name]
            initial_diff = token_fix_value[asset_name]
            price = ex.get_price(pair)
            bid_price = float(ex.get_bid_price(pair))
            ask_price = float(ex.get_ask_price(pair))
            mid_price = round((bid_price + ask_price) / 2, 5)
            pending_buy = ex.get_pending_buy(pair)
            min_trade_value = float(ex.get_min_trade_value(pair))
            step_price = float(ex.get_step_price(pair))
            min_size = float(ex.get_minimum_size(pair))
            time.sleep(0.5)

            buy_price = round(bid_price - step_price, 4)
            buy_size = initial_diff / buy_price  ###
            buy_value = buy_size * buy_price

            # print('Min Value:Amount '+pair,min_trade_value,min_size) ## usd , amount
            print('.-' * 50)
            print('Bot ' + {asset_name} + ' Holding :' + '  0.00 $' + ' Fix Values ' + str(fixed_value))
            # print(f'{pair} Buy Price :{buy_price} Size :{buy_size} Usd: {buy_value}')  # Digit {digit_size}
            ################## Buy Tokens if not in wallet ########################
            if (cash > min_trade_value) and (buy_size > min_size) and (
                    sendding_buy == True):  ### cash > min(limit.buy) & amount_buy > (min(limit.buy.amount))
                if pending_buy == []:
                    print(f'Buying {asset_name} Size = {buy_size} Usd = {buy_value}')
                    order_id = ex.crete_order(pair, 'buy', buy_size, buy_price)
                    print('Waiting For Order To be filled')
                    print('.-' * 50)
                    time.sleep(cdBot)
                    ex.cancel_order(order_id)

            else:
                ###  Cash <= min_trade_value $
                print(f'Buy Command {sendding_buy}')
                print(f"Not Enough Balance to buy {asset_name}")
                print(f'Your Cash is {cash} // Minimum Trade Value is {min_trade_value}')
                print('.-' * 50)
        else:
            print(f'{asset_name} is Already in Wallet')
            print('.-' * 50)



# Check_asset()

def Rebalance():
    try:
        wallet = ex.get_wallet()
        cash = ex.get_cash()
        # try:
        #     asset_in_wallet = [item['coin'] for item in wallet]
        # except:
        #     time.sleep(1)
        #     asset_in_wallet = [item['coin'] for item in wallet]
            # pass

        for asset_name, fixed_value in token_fix_value.items():  ##asset_name = XRP
            # if asset_name in asset_in_wallet:  ### [ XRP , BTC ,ETH ]
                pair = trade_dict[asset_name] # pair = XRP/USD
                price = ex.get_price(pair)
                # print('Check DataBase')
                # rec.checkDB(pair)
                # rec.update_trade_log(pair)
                time.sleep(1)
                hold_value = round(float(ex.get_token_value(asset_name)),3)
                hold_unit = float(ex.get_token_unit(asset_name))

                # fixed_value = token_fix_value[asset_name]
                buy_reb_threshold = threshold_dict_buy[asset_name]  ## buy %
                sell_reb_threshold = threshold_dict_sell[asset_name]  ## buy %
                buy_threshold = fixed_value - (fixed_value * buy_reb_threshold)
                sell_threshold = fixed_value + (fixed_value * sell_reb_threshold)  ###
                # print(buy_reb_threshold,sell_reb_threshold) ## %%%%
                first_entry = rec.check_pnl(asset_name)
                first_entry = first_entry[asset_name][0]
                # print(first_entry)
                pnl = (price - first_entry)
                pnl_p = pnl / first_entry

                tp = float(threshold_stop_sell[asset_name]) # 30%
                sl = float(threshold_stop_buy[asset_name]) # 50%

        # stop_price = round(first_entry- (stop_run * first_entry),5)
                max_zone = round(first_entry + (first_entry * tp), 5)
                min_zone = round(first_entry - (first_entry * sl), 5)
                timestamp = ex.get_time()
                round_pnl  = round(pnl,3 )
                round_pnlp  = round(pnl_p*100,3)

                print('.-' * 50)
                print(timestamp,asset_name)
                print(f' Entry {first_entry} PnL {round_pnl}:PnL% {round_pnlp}%\n Value {hold_value:.2f}$ : FixValues {fixed_value} \n ZoneMax {max_zone} : ZoneMin {min_zone} Stoploss  @ {sl*100 }% ')
                # print(f' Buy Target {buy_threshold}---{buy_reb_threshold*100}% : Sell Target {sell_threshold}---{sell_reb_threshold*100}% ')

                if ((price) > min_zone ) and (hold_value < buy_threshold ):  ### check pnl ### stop loss
                    #chg pnl_p > stoploss :

                    diff = float(fixed_value - hold_value)
                    bid_price = float(ex.get_bid_price(pair))
                    ask_price = float(ex.get_ask_price(pair))
                    mid_price = round((bid_price + ask_price) / 2, 5)
                    pending_buy = ex.get_pending_buy(pair)
                    min_trade_value = float(ex.get_min_trade_value(pair))
                    step_price = float(ex.get_step_price(pair))
                    min_size = float(ex.get_minimum_size(pair))
                    buy_price = round(bid_price - step_price, 5)
                    buy_price_m = float(mid_price - (round(mid_price, 5) * gap))
                    buy_size = abs(diff) / buy_price_m  ###
                    buy_value = buy_size * buy_price_m
                    print('.-' * 50)
                    print('Asset Now Below Fix Values ')
                    # print(f'Buy @ Mid Price {buy_price_m} {buy_value}$ , {buy_size} {asset_name} ----- Bids {buy_price} ')
                    print('.-' * 50)

                    if (cash > min_trade_value) and (
                            buy_size > min_size):  ### cash > min(limit.buy) & amount_buy > (min(limit.buy.amount))
                        if pending_buy == []:
                            print(f'Buying {asset_name}@{buy_price_m} Size = {buy_size} USD$  = {buy_value:.2f}')
                            order_id = ex.crete_order(pair, 'buy', buy_size, buy_price)
                            print('Waiting For Order To be filled')
                            print('.-' * 50)
                            ## cooldown and cancle
                            # time.sleep(5) ### Wait to Fill
                            # ex.cancel_order(str(order_id))
                            time.sleep(1)

                        else:
                            pending_buy_id = ex.get_pending_buy(pair)[0]['id']
                            print("Pending Order Found")
                            print("Canceling pending Order")
                            ex.cancel_order(pending_buy_id)
                            time.sleep(1)
                            # order_id = ex.crete_order(pair, 'buy', buy_size, buy_price)
                            print('>>' * 50)
                    else:
                        ###  Cash <= min_trade_value $
                        print(f"Not Enough Balance  {asset_name}")
                        print(f'Your Cash is {cash:.2f} // Size below Minimum Trade Value  {min_trade_value:.2f}')
                        print('.-' * 50)
                        time.sleep(5)  ### size < min_size >> rerun

                ##
                elif  ((price) < max_zone ) and  (hold_value > sell_threshold):  ### check Values > Fix , Check Price Zone ,etc
                    #chg pnl_p < tp :

                    diff = fixed_value - hold_value
                    bid_price = ex.get_bid_price(pair)
                    ask_price = ex.get_ask_price(pair)
                    mid_price = round((bid_price + ask_price) / 2, 5)
                    pending_sell = ex.get_pending_sell(pair)
                    min_trade_value = ex.get_min_trade_value(pair)
                    step_price = ex.get_step_price(pair)
                    min_size = ex.get_minimum_size(pair)
                    sell_price = round(bid_price + (3 * step_price), 5)
                    sell_price_m = mid_price + (round(mid_price, 5) * gap)
                    sell_size = abs(diff) / sell_price_m  ###
                    sell_value = sell_price_m * sell_size
                    timestamp = ex.get_time()
                    print('.-' * 50)
                    print(timestamp)
                    print('Asset now  more than  Fix Values ')
                    # print(f'Mid Price {sell_price_m}  Asks {ask_price} ')
                    print('.-' * 50)

                    if sell_size > min_size:
                        if pending_sell == []:
                            print(f'Selling {asset_name}@{sell_price_m} Size = {sell_size} USD$  = {sell_value:.2f}')
                            order_id = ex.crete_order(pair, 'sell', sell_size, sell_price_m)
                            print('Waiting For Order To be filled')
                            print('.-' * 50)
                            # time.sleep(10) ### Wait to Fill
                            # ex.cancel_order(str(order_id))
                            time.sleep(1)
                        else:
                            pending_sell_id = ex.get_pending_sell(pair)[0]['id']
                            print("Pending Order Found")
                            print("Canceling pending Order")
                            ex.cancel_order(pending_sell_id)
                            time.sleep(1)
                            # order_id = ex.crete_order(pair, 'sell', sell_size, sell_price_m)

                            print('.-' * 50)

                    else:
                        ###  Cash <= min_trade_value $
                        # print(f'Buy Command {sendding_buy}')
                        print(f"Not Enough Balance to sell {asset_name}")
                        print(f'Your Cash is {cash:.2f} // Minimum Trade Value is {min_trade_value:.2f}  ')
                        print('.-' * 50)
                        time.sleep(5)

                elif price < min_zone:
                    round_pnl = round(pnl_p *100 ,2)
                    print(f'Stop Bot ! PnL now {round_pnl}% Stop Trigger :{sl*100}%')

                elif price >max_zone:
                    round_pnl = round(pnl_p * 100, 2)
                    print(f'Stop Bot ! PnL now {round_pnl}% Take Profit Trigger :{tp * 100}%')
                    # sell all , buy all

                else:
                    timestamp = ex.get_time()
                    # print(timestamp)
                    #### Hold Values  ###
                    print('.-' * 50)
                    print(f'No Action PnL : {pnl_p*100}% ')
                    print(f"{pair} @{price} Holding {hold_value:.2f}$ Free Cash {cash:.2f}\n  Waiting {cdBot} Seconds")
                    print('.-' * 50)
                    time.sleep(1)

    except Exception as e:
        print(str(e))
        ex.log(e)
        pass

def entry_port():
    try:
        aa = pd.DataFrame()
        aa['symbol'] = np.array(token_name)
        aa['entry']=(entry_dict.values())

        price_list = []
        for symbol in token_name:
            price =  ex.get_price(symbol+'/USD')
            price_list.append(price)
            aa['price'] = 0.0
            # aa['entry'] = entry_dict[symbol]

            # aa['entry'] = 0.0
        # aa.loc[aa['symbol']==symbol ]['entry'] =

        aa['price'] = price_list
        aa['stop'] = aa['price']- (trigger_stop_buy* aa['price'])
        aa['tp'] = aa['price']+ (trigger_stop_sell* aa['price'])
        # aa.set_index('symbol',inplace=True)
        aa.to_csv('entry_price_log.csv')
        return aa



    except Exception as e:
        print(str(e))



def record(): ### Rebalance jobs
    return_code = 1
    # while True:
    #     return_code = 1 ### Run bot status

    try:
            print('.*'*60)
            print('Check DataBase')
            for asset_name, symbols in trade_dict.items():
                    rec.checkDB(symbols)
                    rec.update_trade_log(symbols)
            time.sleep(1)
            print('.*'*60)
            rec.save_database(token_name)

    except KeyboardInterrupt as e:
            print(str(e),' UserStopBot')
            sys.exit(return_code)
            # logger.info('User Stop.')
            return_code = 0

    except SystemExit as e:
            return_code = e


    return return_code

schedule.every(20).seconds.do(Check_asset)

schedule.every(1).minutes.do(Rebalance)
schedule.every(5).minutes.do(record)
entry_port()

print(f'Bot Activate !')
print(datetime.datetime.now().strftime(('%d:%m:%Y %H:%M:%S')))
# Check_asset()
wallet = ex.get_wallet()
print(wallet)
# while 1:
#     # Check_asset()
#     # time.sleep(60)
#     schedule.run_pending()
#     time.sleep(1)
#


# if __name__ == '__main__':
#     print('Bot Turn On : Running ')
#     main_job()
# # #
#

## record() #Test

