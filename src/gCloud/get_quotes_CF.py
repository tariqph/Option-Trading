
from alice_blue.alice_blue import LiveFeedType
from aliceBlue_connect import get_token
from time import sleep
import datetime
import time
import sqlalchemy
import os

# Connection details for Google Cloud SQL
connection_name = os.environ('connection')
table_name = os.environ('table_name')
table_field1 = "timestamp"
table_field2 = "ltp"
table_field3 = "volume"
table_field4 = "Instrument"
table_field5 = "Expiry"

db_name = os.environ('db_name')
db_user = os.environ('db_user')
db_password = os.environ('db_password')
alice_token = get_token()
start = time.time()

driver_name = 'mysql+pymysql'
query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})

socket_opened = False



def call_insert(request,context):
	def event_handler_quote_update(message):
		table_field_value1 = message['exchange_time_stamp']
		table_field_value2 = message['ltp']
		table_field_value3 = message['volume']
		table_field_value4 = message['instrument']
		table_field_value5 = message['instrument'][4]
		
		db = sqlalchemy.create_engine(  sqlalchemy.engine.url.URL(
		drivername=driver_name,
		username=db_user,
		password=db_password,
		database=db_name,
		query=query_string, ),
		pool_size=5,
		max_overflow=2,
		pool_timeout=30,
		pool_recycle=1800)


		stmt = sqlalchemy.text('insert into {} ({},{},{},{}) values ({},{},{},"{}")'.format(table_name,
								table_field1,table_field2,table_field3,table_field4,
						table_field_value1, table_field_value2, table_field_value3,table_field_value4)
	)


		date = datetime.datetime.utcfromtimestamp(message['exchange_time_stamp'])
		sec = date.second
		#print(stmt)
		#print(db)
		#print(message)
		#sec = date.second
		#print(sec)
		if(True):
			try:
				with db.connect() as conn:
					print('here')
					conn.execute(stmt)
					context.end()
			except Exception as e:
				print("here1")
				return 'Error: {}'.format(str(e))
				context.end()
			
			

		#with open('test.txt','w') as f:
		#print(message["exchange_time_[stamp"])
			#f.write(f"quote update {message}")
		#sleep(10)


	def open_callback():
		global socket_opened
		socket_opened = True

	alice_token.start_websocket(subscribe_callback=event_handler_quote_update,
						socket_open_callback=open_callback,
						run_in_background=True)

	option_token = alice_token.get_instrument_for_fno(symbol = 'BANKNIFTY', 
		expiry_date=datetime.date(2021, 8, 26), is_fut=False, strike=30000, is_CE = True)

	while True:
		alice_token.subscribe(option_token, LiveFeedType.COMPACT)	
		if time.time() - start > 5:
			alice_token.unsubscribe(option_token, LiveFeedType.COMPACT)	
			context.end()
		#sleep(1