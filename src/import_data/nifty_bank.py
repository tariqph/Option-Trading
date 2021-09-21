import sys
import datetime
from time import time
import numpy as np
from greeks import greek_calculation
from alice_blue.alice_blue import LiveFeedType
from aliceBlue_connect import get_token
import psycopg2
from config import config

sys.path.append('src/strategy')
sys.path.append('src/config')

# Postgres database connection
# read connection parameters
params = config()

# connect to the PostgreSQL server
print('Connecting to the PostgreSQL database...')
connection = psycopg2.connect(**params)
print('Connected to Database')
connection.autocommit = True

# cursor object for database
cursor = connection.cursor()
postgres_insert_query = """ INSERT INTO option_data (date_time, instrument, 
                            ltp, option, strike,expiry, delta, theta, vega, gamma) 
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

# Strike price of the option chain
strikes = np.arange(32000,37100,100)

alice_token = get_token()
option_tokens = []

# Underlying token appended to option token
niftybank_token = alice_token.get_instrument_by_symbol('NSE', 'Nifty Bank')
option_tokens.append(niftybank_token)

# Call option tokens appended to option_tokens
for strike in strikes:
    option_tokens.append(alice_token.get_instrument_for_fno(symbol = 'BANKNIFTY', 
        expiry_date=datetime.date(2021, 8, 26), is_fut=False, strike=strike, is_CE = True))

# Put option tokens appended to option_tokens
for strike in strikes:
    option_tokens.append(alice_token.get_instrument_for_fno(symbol = 'BANKNIFTY', 
        expiry_date=datetime.date(2021, 8, 26), is_fut=False, strike=strike, is_CE = False))


socket_opened = False
def event_handler_quote_update(message):
    # Convert timestamp recieved from websocket to readable format
    date_time = datetime.datetime.utcfromtimestamp(message['exchange_time_stamp'])
    date_time = date_time + datetime.timedelta(hours=5, minutes=30)
    date = date_time.date()
    time = date_time.time()
    
    seconds = date_time.second
    expiry = message['instrument'][4]
    
    # Write to the database every minute
    if(seconds == 0):
        if(expiry != None):
            strike = float(message['instrument'][2].split()[2])
            is_ce = bool(message['instrument'][2].split()[3] == 'CE')
            days_to_expiry = int((message['instrument'][4] - datetime.date.today()).days)
            price = float(message['ltp'])
            
            # Calculate the option greeks using the livefeed data
            delta, theta, vega, gamma = greek_calculation(35000,strike,price,0.1,days_to_expiry,is_ce)
            
            # Insert a record in the database
            record_to_insert = (date_time,message['instrument'][2].split()[0],
                                price,
                                message['instrument'][2].split()[3],
                                strike,expiry,delta, theta, vega, gamma)
            cursor.execute(postgres_insert_query, record_to_insert)
            
            

        else:
            # Get the underlying price from livefeed and insert into database
            price = float(message['ltp'])
            record_to_insert = (date_time,message['instrument'][2].split()[0],
                                price,
                                'Underlying',
                                0,expiry,0, 0, 0, 0)
            cursor.execute(postgres_insert_query, record_to_insert)
            
        

def open_callback():
    global socket_opened
    socket_opened = True

# Start the websocket connection
alice_token.start_websocket(subscribe_callback=event_handler_quote_update,
                      socket_open_callback=open_callback,
                      run_in_background=True)

#Check this and change back if required
while True:
    # Subscribe to the options specified in the option_tokens
    alice_token.subscribe(option_tokens, LiveFeedType.COMPACT)
        

