import sys
sys.path.append('src/calculations')
sys.path.append('src/config')

import csv
from alice_blue.alice_blue import LiveFeedType
from aliceBlue_connect import get_token
from time import sleep
import datetime
import time
import numpy as np

alice_token = get_token()
start = time.time()

with open('Data\data1.csv','w') as data_file:
	data_writer = csv.writer(data_file,delimiter=',',lineterminator = '\n')

	socket_opened = False
	def event_handler_quote_update(message):
		print((type(message['instrument'][4])))
		date = datetime.datetime.utcfromtimestamp(message['exchange_time_stamp'])
		sec = date.second
		print(message)
		#sec = date.second
		#print(sec)
		if(sec):
			data_writer.writerow([message['exchange_time_stamp'],message['ltp']
			,message['volume'],message['instrument'][2],message['instrument'][4]])
			print(f"quote update {message}")
			# global socket_opened
			# socket_opened = False
			

		#with open('test.txt','w') as f:
		#print(message["exchange_time_stamp"])
			#f.write(f"quote update {message}")
		#sleep(10)


	def open_callback():
		global socket_opened
		socket_opened = True

	alice_token.start_websocket(subscribe_callback=event_handler_quote_update,
						socket_open_callback=open_callback,
						run_in_background=True)
 
	# token for nifty bank index
	#option_token = alice_token.get_instrument_by_symbol('NSE', 'Nifty Bank')
	""" option_token = alice_token.get_instrument_for_fno(symbol = 'NIFTY', 
		expiry_date=datetime.date(2021, 8, 26), is_fut=False, strike=16000, is_CE = True)
 """
 
strikes = np.arange(35000,35300,100)

print(len(strikes))
print(strikes)

alice_token = get_token()
option_tokens = []

niftybank_token = alice_token.get_instrument_by_symbol('NSE', 'Nifty Bank')
option_tokens.append(niftybank_token)


for strike in strikes:
    option_tokens.append(alice_token.get_instrument_for_fno(symbol = 'BANKNIFTY', 
        expiry_date=datetime.date(2021, 8, 26), is_fut=False, strike=strike, is_CE = True))

while True:
		alice_token.subscribe(option_tokens, LiveFeedType.COMPACT)	
		if time.time() - start > 60:
			#alice_token.unsubscribe(option_token, LiveFeedType.COMPACT)	
			exit()
		#sleep(10)


