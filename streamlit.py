import streamlit as st
import pandas as pd
# import matplotlib as plt
from functions import get_play_by_play

# Load your data (adjust the path to your actual data file)
nba_games_id = pd.read_csv('nba_games_id.csv')

# Streamlit app

st.title("NBA Play-by-Play Data Viewer")

# Create a select box for matchups
matchups = nba_games_id['MATCHUP'].unique()
selected_matchup = st.selectbox("Select a Matchup", matchups)

with st.form(key='my_form'):
    matchup=st.selectbox('Select Matchup.', list(nba_games_id['MATCHUP']))
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    game_id = nba_games_id['GAME_ID'].loc[nba_games_id['MATCHUP']==matchup]
    fig = get_play_by_play(game_id)

st.pyplot(fig)