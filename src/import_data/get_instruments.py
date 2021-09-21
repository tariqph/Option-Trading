from alice_blue	import *
from aliceBlue_connect import get_token


alice_token = get_token()

print(alice_token.get_all_subscriptions())