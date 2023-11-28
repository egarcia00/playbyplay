import streamlit as st
import pandas as pd
import matplotlib as plt
from functions_pbp import get_play_by_play, create_home_delta_plot
from nba_api.stats.endpoints import playbyplayv2
import numpy as np

# Load your data (adjust the path to your actual data file)
nba_games_id = pd.read_csv('nba_games_id.csv',  
                            dtype= {'	Unnamed: 0':str, 
                            'GAME_ID':str,
                            'MATCHUP':str})[["GAME_ID","MATCHUP"]]

# Streamlit app

st.title("NBA Play-by-Play Data Viewer")

# Create a select box for matchups
matchups = nba_games_id['MATCHUP'].unique()

with st.form(key='my_form'):
    matchup=st.selectbox('Select Matchup.', list(nba_games_id['MATCHUP']))
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    game_id = nba_games_id['GAME_ID'].loc[nba_games_id['MATCHUP']==matchup]
    df = get_play_by_play(game_id)
    # Use Streamlit to create and display the plot
    st.pyplot(create_home_delta_plot(df))