# streamlit_app.py
import sys
sys.path.append('src/strategy')
sys.path.append('src/config')


from re import M
from numpy import mod
import streamlit as st
import psycopg2
import plotly.graph_objects as go
import pandas as pd
import pandas.io.sql as sqlio
import time as t
import datetime
from strategy import row_color_strat

st.set_page_config(layout="wide")

# Initialize connection.
# Uses st.cache to only run once.
@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

@st.cache(ttl=1)
def current_time():
    now = datetime.datetime.now()
    dt_string = now.strftime("%H:%M:%S")
    return dt_string
    

# Perform query and return results.
# Uses st.cache to only rerun when the query changes or after 1 min.
@st.cache(ttl=60)
def run_query(query1,query2, query3):
    with conn.cursor() as cur1,conn.cursor() as cur2, conn.cursor() as cur3:
        #return sqlio.read_sql_query(query,conn)
        cur1.execute(query1)
        cur2.execute(query2)
        cur3.execute(query3)
        return cur1.fetchall(), cur2.fetchall(), cur3.fetchall()

# Layouts for the dashboard.
col1 ,_,col3 = st.columns(3)
col1.title("BANKNIFTY")
underlying_placeholder = col1.empty()
time_placeholder = col3.empty()
html_str1 = f"""
<style>
p.a {{
font: bold 24px Courier;
}}
</style>
<p class="a">Expiry : 26-Aug-2021</p>
"""
col3.markdown(html_str1, unsafe_allow_html=True)


def option_table(placeholder,underlying_placeholder,query1,query2,query3):
    ''' Draw the option chain plotly table highlighting the required contract for trading strategy'''
    
	# query the database
    call_data,put_data, underlying = run_query(query1,query2,query3)
    col_names_call = ["strike","CE_LTP", "CE_Delta", "CE_Theta", "CE_Gamma","CE_Vega"]
    col_names_put = ["strike", "PE_LTP","PE_Delta", "PE_Theta", "PE_Gamma","PE_Vega"]
    
	# Insert the queried results into the a pandas dataframe
    underlying_price = pd.DataFrame(underlying).round(2)
    fetched_call_data = pd.DataFrame(call_data, columns=col_names_call).round(2)
    fetched_put_data = pd.DataFrame(put_data, columns=col_names_put).round(2)
    
    # Merge the put and call data based on strike
    merged_data = fetched_call_data.merge(fetched_put_data,how = 'outer', on = 'strike')
   
    headers = ['CE_Gamma','CE_Vega','CE_Theta','CE_Delta','CE_LTP','Strike','PE_LTP',
            'PE_Delta','PE_Theta','PE_Vega','PE_Gamma']
    new_headers = ['<b>' + header + '</b>' for header in headers]
    
    
    # Color to highlight rows based on strategy
    row_colors = row_color_strat(merged_data)
    
    modified_table = pd.concat([merged_data.CE_Gamma,merged_data.CE_Vega,merged_data.CE_Theta,
                                merged_data.CE_Delta,merged_data.CE_LTP,merged_data.strike,
                            merged_data.PE_LTP,merged_data.PE_Delta,
                                merged_data.PE_Theta,merged_data.PE_Vega,merged_data.PE_Gamma
                                ],
                            keys=headers)

    fig = go.Figure(data=[go.Table(
        header=dict(values=new_headers,
                    fill_color='rgb(246,151,4)',
                    line_color='rgb(73,0,146)',
                    font=dict( size=16),
                    align='left'),
        cells=dict(values=[modified_table.CE_Gamma,modified_table.CE_Vega,modified_table.CE_Theta,
                        modified_table.CE_Delta,
                        modified_table.CE_LTP,modified_table.Strike,
                        modified_table.PE_LTP,modified_table.PE_Delta,
                        modified_table.PE_Theta,modified_table.PE_Vega,modified_table.PE_Gamma],
                fill_color=[row_colors],
                line_color='rgb(0,0,0)',
                font = dict(size = 14, ),
                align='left'))
    ])
    # Print results.
    fig.update_layout( height=1000, margin=dict(l=1,r=1,b=1,t=1))
    placeholder.plotly_chart(fig,use_container_width=True)

    html_str = f"""
    <style>
    p.a {{
    font: bold 24px Courier;
    color: green;
    }}
    </style>
    <p class="a">{underlying_price.iloc[0,0]}</p>
    """
    underlying_placeholder.markdown(html_str, unsafe_allow_html=True)
    
# Empty placeholder to put the table in the dashboard
placeholder = st.empty()

while True:
    
    time = datetime.datetime.now()
    time = time - datetime.timedelta(days = 27 , hours = 23)
    time_last = time - datetime.timedelta(minutes= 45)
    time_now = time - datetime.timedelta(seconds= time.second)
    
    time_now = time_now.strftime("%H:%M:%S")
    time_last = time_last.strftime("%H:%M:%S")
 
  
    # queries for call, put option chain and underlying price changing bsed on current time
    query1 = f"SELECT strike,avg(ltp) as CE_LTP, avg(delta) as CE_Delta, avg(theta) as CE_Theta, avg(gamma) as CE_Gamma, avg(vega) as CE_Vega from option_data where option =\'CE\' and date_time::time <= time \'{time_now}\' and date_time::time >= time \'{time_last}\' group by strike order by strike;"
    query2 = f"SELECT strike,avg(ltp) as PE_LTP, avg(delta) as CE_Delta, avg(theta) as CE_Theta, avg(gamma) as CE_Gamma, avg(vega) as CE_Vega from option_data where option =\'PE\' and date_time::time <= time \'{time_now}\' and date_time::time >= time \'{time_last}\' group by strike order by strike;"
    query3 = f"SELECT AVG(ltp) from option_data where instrument =\'Nifty\' and date_time::time <= time \'{time_now}\' and date_time::time >= time \'{time_last}\' ;"
    
    t.sleep(0.5)
    time_now = current_time()
    time_placeholder.title(time_now)
    option_table(placeholder, underlying_placeholder, query1, query2,query3)
 
    
