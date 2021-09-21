from alice_blue import *
from configparser import ConfigParser
from config import config

def get_token():
    
    ''' Returns an alice_blue token to access livedata and to place and cancel orders'''
    
    # Read the config file for alice blue connection parameters
    connection_params = config(filename='database.ini', section='alice_blue')
    access_token = AliceBlue.login_and_get_access_token(username=connection_params['user_id'], 
                                                        password=connection_params['pwd'],
                                                        twoFA='a', 
                                                        api_secret=connection_params['api_secret'],
                                                        app_id = connection_params['app_id'])
    
    alice = AliceBlue(username=connection_params['user_id'], password=connection_params['pwd'],
	access_token=access_token)
    
    return alice
   

    

    