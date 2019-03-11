"""
This code is an example of a simple market maker strategy for ETH-EUR market

Disclaimer: Not saying it will make you money, in fact it most likely wont. Use at your own risk.
"""

import krakenex
import numpy as np
from numpy import cumsum, log, polyfit, sqrt, std, subtract
from numpy.random import randn
import matplotlib.pyplot as plt
import pandas as pd
k = krakenex.API()
k.load_key('kraken.key')
import random
import time

def order_book():
    res=k.query_public('Depth',{'pair':'XETHZEUR'})
        
    asks = res['result']['XETHZEUR']['asks']

    bids = res['result']['XETHZEUR']['bids']
    return asks,bids


open_orders = k.query_private('OpenOrders')['result']['open']
for x in open_orders:
	if open_orders[x]['descr']['type']=='buy' and open_orders[x]['descr']['pair']=='ETHEUR':
		k.query_private('CancelOrder', {'txid': x})	
l=0
asks,bids=order_book()
while True:
	balance = k.query_private('Balance')
	eth_bal = float(balance['result']['XETH'])-9.96696
	eur_bal = float(balance['result']['ZEUR'])
	total_val =(eur_bal+eth_bal*float(bids[0][0]))

	if eth_bal>0:
		open_orders = k.query_private('OpenOrders')#['result']['open']
		if open_orders['error']==[]:
			ticker = 0
			open_orders = open_orders['result']['open']			
			for x in open_orders:
				if open_orders[x]['descr']['type']=='sell' and open_orders[x]['descr']['pair']=='ETHEUR':
					k.query_private('CancelOrder', {'txid': x})		
			asks,bids=order_book() # 1 sec

			sell_price = float(asks[0][0])-0.0001
			sell_order=k.query_private('AddOrder', {'pair': 'XETHZEUR',
								 'type': 'sell',
								 'ordertype': 'limit',
								 'price': sell_price,
								 'volume': eth_bal,
								 })
			old_sell=sell_price


	if eth_bal<0.1:
		open_orders = k.query_private('OpenOrders')#['result']['open']
		if open_orders['error']==[]:
			ticker = 0
			open_orders = open_orders['result']['open']			
			for x in open_orders:
				if open_orders[x]['descr']['type']=='buy' and open_orders[x]['descr']['pair']=='ZECEUR':
					k.query_private('CancelOrder', {'txid': x})
			asks,bids=order_book()# 1 sec
			
			if float(asks[0][0])>float(bids[0][0])*1.004:
				bid_price = float(bids[0][0])+0.00001
			
				buy_vol = ((eur_bal-1))/bid_price
				buy_order=k.query_private('AddOrder', {'pair': 'XETHZEUR',
										 'type': 'buy',
										 'ordertype': 'limit',
										 'price': bid_price,
										 'volume': buy_vol,
										 })
				old_price = bid_price

			else:
				print "No order. Perc ",abs(float(asks[0][0])-float(bids[0][0]))/float(bids[0][0])
				open_orders = k.query_private('OpenOrders')
				open_orders = open_orders['result']['open']			
				for x in open_orders:
					if open_orders[x]['descr']['type']=='buy' and open_orders[x]['descr']['pair']=='ZECEUR':
						k.query_private('CancelOrder', {'txid': x})
				

	l+=1
	time.sleep(2)


