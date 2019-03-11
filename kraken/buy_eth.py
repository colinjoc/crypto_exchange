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

#time.sleep(60)
def order_book():
    res=k.query_public('Depth',{'pair':'XETHZEUR'})
        
    asks = res['result']['XETHZEUR']['asks']

    bids = res['result']['XETHZEUR']['bids']
    return asks,bids


open_orders = k.query_private('OpenOrders')['result']['open']
for x in open_orders:
	if open_orders[x]['descr']['type']=='buy' and open_orders[x]['descr']['pair']=='ETHEUR':
		k.query_private('CancelOrder', {'txid': x})	
buy = False; sell = True; old_zec_bal = 0; old_sell = 0; old_price = 0
l = 0
#buy = True; sell = False; old_eth_bal = 0
ticker = 0
while True:
	
	
	balance = k.query_private('Balance')
	eth_bal = float(balance['result']['XETH'])
	eur_bal = float(balance['result']['ZEUR'])
	
    
	print "ETH: %s, Eur: %s" %(eth_bal,eur_bal)
	if eur_bal>5:
		open_orders = k.query_private('OpenOrders')#['result']['open']
		ticker = 0
		open_orders = open_orders['result']['open']			
		for x in open_orders:
			if open_orders[x]['descr']['type']=='sell' and open_orders[x]['descr']['pair']=='ETHEUR':
				k.query_private('CancelOrder', {'txid': x})		
		asks,bids=order_book()
		#if abs(float(asks[0][0])-float(asks[2][0]))>0.01:
		#	sell_price = max([float(asks[2][0]),float(bids[0][0])*(1.005)])-0.0001
		#else:		
		buy_price = float(bids[0][0])
		buy_vol = eur_bal/float(bids[0][0])
		buy_order=k.query_private('AddOrder', {'pair': 'XETHZEUR',
							 'type': 'buy',
							 'ordertype': 'limit',
							 'price': buy_price,
							 'volume': buy_vol,
							 })

	time.sleep(3)



