import streamlit as st
import pandas as pd
import matplotlib as plt
from functions import get_play_by_play
from nba_api.stats.endpoints import playbyplayv2

# Load your data (adjust the path to your actual data file)
nba_games_id = pd.read_csv('nba_games_id.csv')

# Streamlit app

st.title("NBA Play-by-Play Data Viewer")

# Create a select box for matchups
matchups = nba_games_id['MATCHUP'].unique()

with st.form(key='my_form'):
    matchup=st.selectbox('Select Matchup.', list(nba_games_id['MATCHUP']))
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    game_id = nba_games_id['GAME_ID'].loc[nba_games_id['MATCHUP']==matchup]
    get_play_by_play(game_id)