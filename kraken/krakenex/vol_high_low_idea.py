

import krakenex
import numpy as np
from numpy import cumsum, log, polyfit, sqrt, std, subtract
from numpy.random import randn
import matplotlib.pyplot as plt

k = krakenex.API()
k.load_key('kraken.key')
"""
k.query_private('AddOrder', {'pair': 'XXBTZEUR',
                             'type': 'buy',
                             'ordertype': 'limit',
                             'price': '1',
                             'volume': '1',
                             'close[pair]': 'XXBTZEUR',
                             'close[type]': 'sell',
                             'close[ordertype]': 'limit',
                             'close[price]': '9001',
                             'close[volume]': '1'})
"""
#def order_book():
res = k.query_public('Depth',{'pair':'ETHEUR'})
    


