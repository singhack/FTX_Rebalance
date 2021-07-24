import pandas as pd
import matplotlib.pyplot as plt
from exchange import Exchange
from record import Record
import warnings
ex  = Exchange()
rec =Record()


def pie_chart(values,label):
    # plt.show()
    fig1, ax1 = plt.subplots()
    ax1.pie(values,labels = label,shadow=False, startangle=90, pctdistance=0.75,autopct= '%1.1f%%')
    # ax1.axis('equal')
    plt.tight_layout()

    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    # plt.pie(wallet_data['usdValue'], labels  = wallet_data['coin'])
    plt.show()


def calc_MDD(networth):
  df = pd.Series(networth, name="nw").to_frame()

  max_peaks_idx = df.nw.expanding(min_periods=1).apply(lambda x: x.argmax()).fillna(0).astype(int)
  df['max_peaks_idx'] = pd.Series(max_peaks_idx).to_frame()

  nw_peaks = pd.Series(df.nw.iloc[max_peaks_idx.values].values, index=df.nw.index)

  df['dd'] = ((df.nw-nw_peaks)/nw_peaks)
  df['mdd'] = df.groupby('max_peaks_idx').dd.apply(lambda x: x.expanding(min_periods=1).apply(lambda y: y.min())).fillna(0)

  return df



wallet = ex.get_wallet()
df = pd.DataFrame(wallet)
df1 = df[['coin', 'usdValue']]
# df1.dropna(inplace=True)

df1['usdValue'] = df1['usdValue'].astype(float)
wallet_data = df1[df1['usdValue'] > 1]
usdd = (wallet_data[wallet_data['coin'] == 'USD'])['usdValue'].values
# wallet_data['exposure'] = wallet_data['usdValue'] /usdd
# print(wallet_data[wallet_data['coin']=='XRP']['usdValue'])
wallet_data['Exposure']=wallet_data['usdValue'] / usdd
total_equity = wallet_data['usdValue'].sum()
cash  = ex.get_cash()
asset_total = 0.0
for i in wallet_data['usdValue']:
    if i != 'USD':
        asset_total += i
asset_total = asset_total - usdd
# print('**'*50)
# print(wallet_data)
# print(f'Total Equity {total_equity} Cash {cash} Total Asset {asset_total} ')
#
# print('**'*50)
# pie_chart(wallet_data['usdValue'],label= wallet_data['coin'])

print(rec.get_trade_history('XRP/USD'))