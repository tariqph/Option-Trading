import mibian

def greek_calculation(underlying_price:float, 
                      strike:float, price:float, 
                      interest_rate:float,days_to_expiry: int,
                      is_call: bool):
    
    """
    Calculates the implied volatility of an option contract given its 
    underlying, strike, price & expiry date.
    After obtaining the iv, it calculates and returns the greeks
    """
    if(is_call):
        call_option = mibian.BS([underlying_price,
                              strike,
                              interest_rate,days_to_expiry],
              callPrice =  price)
        implied_volatility = call_option.impliedVolatility
        greeks = mibian.BS([underlying_price,strike,
                            interest_rate,days_to_expiry]
                           ,volatility=implied_volatility)
        
        return greeks.callDelta, greeks.callTheta, greeks.vega, greeks.gamma
        
    else:
        put_option = mibian.BS([underlying_price,strike,interest_rate,days_to_expiry],
                               putPrice = price)
        implied_volatility = put_option.impliedVolatility
        greeks = mibian.BS([underlying_price,strike,interest_rate,days_to_expiry],
                           volatility = implied_volatility)
        
        return greeks.putDelta, greeks.putTheta, greeks.vega, greeks.gamma
    
    
    
    