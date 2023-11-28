# import streamlit as st
# import pandas as pd
# import matplotlib as plt
# from functions_pbp import get_play_by_play
# from nba_api.stats.endpoints import playbyplayv2
# import numpy as np

# # Load your data (adjust the path to your actual data file)
# nba_games_id = pd.read_csv('nba_games_id.csv')

# # Streamlit app

# st.title("NBA Play-by-Play Data Viewer 22222")

# # Create a select box for matchups
# matchups = nba_games_id['MATCHUP'].unique()

# with st.form(key='my_form'):
#     matchup=st.selectbox('Select Matchup.', list(nba_games_id['MATCHUP']))
#     submit_button = st.form_submit_button(label='Submit')

# if submit_button:
#     game_id = nba_games_id['GAME_ID'].loc[nba_games_id['MATCHUP']==matchup]
#     df = get_play_by_play(game_id)

# st.line_chart(df['HomeScore'])

import pandas as pd
import pandas_datareader as web
import datetime as dt
import numpy as np
import streamlit as st
st.title('Crypto price over time.')
with st.form(key='my_form'):
    crypto=st.selectbox('Select Cryptocurrency', ['BTC','ETH','XRP','BCH'])
    start=st.date_input('Start')
    end=st.date_input('End')
    submit_button = st.form_submit_button(label='Submit')
if submit_button:
    df = web.DataReader(f'{crypto}-USD', 'yahoo', start, end)
st.line_chart(df['Adj Close'])