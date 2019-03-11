"""
This code is an example of a simple moving average cross-over strategy for BTC-EUR market, 5 min interval

Disclaimer: Not saying it will make you money, in fact it most likely wont. Use at your own risk.
"""

import krakenex
import pandas as pd
import matplotlib.pyplot as plt
import time
import numpy as np

k = krakenex.API()
k.load_key('kraken.key') # Load your api keys 
lon = 40

std_mult = 2.0
vol_len = 20
interval = 5
#===================================================================================================
def get_ohlc():
	res=k.query_public('OHLC',{'pair':'XXBTZEUR'
		                     ,'interval':interval})
	head=["time", "open", "high", "low", "close", "vwap", "volume", "count"]
	out=pd.DataFrame(res['result']['XXBTZEUR'],columns=head,dtype=float)
	out['hl2']=(out['high']+out['low'])/2
	return out
def order_book():
    res=k.query_public('Depth',{'pair':'XXBTZEUR'})
        
    asks = res['result']['XETHZEUR']['asks']

    bids = res['result']['XETHZEUR']['bids']
    return asks,bids

sell_txid = 0
buy_txid=0
total_val = 0
short_buy=False; short_sell=True;short_sell_check=False;short_buy_check=False	
shrt_t=8 ; lon_t=30

balance = k.query_private('Balance')
btc_bal = float(balance['result']['XXBT'])
eur_bal = float(balance['result']['ZEUR'])
	

while True:
	ohlc = get_ohlc()
	l = len(ohlc)
	#-------- indicators -------------------
	h_val = ohlc['high'][l-5:l].mean()*(1+0.0016)
	l_val = ohlc['low'][l-5:l].mean()*(1-0.0016)
	buy_price = l_val; sell_price = h_val
		
	rm_shrt_hl2_new = ohlc['hl2'][l-shrt_t:l].mean()
	rm_shrt_hl2_old = ohlc['hl2'][l-shrt_t-1:l-1].mean()
	rm_lon_hl2_new = ohlc['hl2'][l-lon_t:l].mean()
	rm_lon_hl2_old = ohlc['hl2'][l-lon_t-1:l-1].mean()
	hl_ppo_old = (rm_shrt_hl2_old -rm_lon_hl2_old)/rm_shrt_hl2_old*100
	hl_ppo_new = (rm_shrt_hl2_new -rm_lon_hl2_new)/rm_shrt_hl2_new*100


	#-------------balance--------------------
	balance = k.query_private('Balance')
	btc_bal = float(balance['result']['XXBT'])
	eur_bal = float(balance['result']['ZEUR'])
	total_val = eur_bal + btc_bal*ohlc['close'][l-1]*(1 - 0.0016)

	spend_eur= total_val*0.33
	buy_vol=spend_eur/buy_price	

	
	# close all orders
	order_list=k.query_private('OpenOrders')['result']['open'].keys()
	for ids in order_list:
		k.query_private('CancelOrder', {'txid': ids})

	# number of positions
	number_shorts=0
	pos_list=k.query_private('OpenPositions')['result']
	for q in range(len(pos_list.keys())):
		pos_id	= pos_list.keys()[q]	
		if pos_list[pos_id]['type']=='sell':
			number_shorts+=1
	#print "=======Old orders cancelled=============="
	if hl_ppo_old<hl_ppo_new and hl_ppo_new<0:	
		if eur_bal -(buy_price*(1.0-0.0016))*buy_vol >0:
			#place order to buy
			buy_order=k.query_private('AddOrder', {'pair': 'XXBTZEUR',
		                     'type': 'buy',
		                     'ordertype': 'limit',
		                     'price': buy_price,
		                     'volume': buy_vol,
		                     })
			buy_txid=buy_order['result']['txid'][0]
		elif eur_bal>5:
			small_buy = (eur_bal-0.3)/buy_price
			buy_order=k.query_private('AddOrder', {'pair':'XXBTZEUR',
		                     'type': 'buy',
		                     'ordertype': 'limit',
		                     'price': buy_price,
		                     'volume': small_buy,
		                     })
			buy_txid=buy_order['result']['txid'][0]		

		if number_shorts>0:
			short_buy_order=k.query_private('AddOrder', {'pair': 'XXBTZEUR',
		                     'type': 'buy',
		                     'ordertype': 'limit',
		                     'price': buy_price,
		                     'volume':0.075	,
		                     'leverage':2
		                     })
			short_buy_txid=short_buy_order['result']['txid'][0]




	if hl_ppo_old>hl_ppo_new and hl_ppo_new>0:
		if btc_bal-buy_vol >0:
			#place order to sell eth
			sell_order=k.query_private('AddOrder', {'pair': 'XXBTZEUR',
		                     'type': 'sell',
		                     'ordertype': 'limit',
		                     'price': sell_price,

		                     'volume': buy_vol,
		                     })
			sell_txid=sell_order['result']['txid'][0]		

		elif btc_bal>0.01:
			#place order to sell eth
			small_sell = btc_bal- 0.01
			sell_order=k.query_private('AddOrder', {'pair': 'XXBTZEUR',
		                     'type': 'sell',
		                     'ordertype': 'limit',
		                     'price': sell_price,
		                     'volume': small_sell
		                     })
			sell_txid=sell_order['result']['txid'][0]		
	

		if number_shorts<3:
			print "Short sell"
			short_sell_order=k.query_private('AddOrder', {'pair': 'XXBTZEUR',
		                     'type': 'sell',
		                     'ordertype': 'limit',
		                     'price': sell_price,
		                     'volume': 0.075,
		                     'leverage':2
		                     })
			short_sell_txid=short_sell_order['result']['txid'][0]


	#print "======================== Orders Placed ======================="
	print "Buy price: %s, Sell price: %s, hl_ppo_old: %s, hl_ppo_new:%s, number shorts: %s" %(buy_price, sell_price,hl_ppo_old,hl_ppo_new,number_shorts)
	print "Sleeping. Total value = %s. Euro = %s. Btc = %s\n" %(total_val,eur_bal, btc_bal) 
	time.sleep(60*interval-1)




