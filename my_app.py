import streamlit as st
import pandas as pd
import matplotlib as plt
from functions_pbp import get_play_by_play
from functions_pbp import create_home_delta_plot
from functions_pbp import get_all_nba_games
from nba_api.stats.endpoints import playbyplayv2
import numpy as np
from datetime import datetime

st.title("NBA IN GAME LEAD TRACKER\n (1996-2023)")
tab1, tab2 = st.tabs(['README', 'LEAD TRACKER'])

with tab1:
    st.header("README")

with tab2:
    st.header("LEAD TRACKER")
    
    with st.sidebar:
        st.header("Filters:")
        year_list = list(reversed(range(1996, 2024)))
        selected_year = st.selectbox("Select a Year", year_list)
        df_season_games = get_all_nba_games(selected_year)

        if selected_year:
            min_season_dates = datetime.strptime(df_season_games['GAME_DATE'].min(),'%Y-%m-%d').date()
            max_season_dates = datetime.strptime(df_season_games['GAME_DATE'].max(),'%Y-%m-%d').date()
            selected_date = st.date_input("Select a date", 
                                            value=min_season_dates, 
                                            min_value=min_season_dates, 
                                            max_value=max_season_dates, 
                                            format="YYYY/MM/DD"
                                            )
            if selected_date:
                # daily_matches = df_season_games.loc[df_season_games['GAME_DATE']==selected_date]['MATCHUP'].unique()
                # daily_matches = df_season_games['MATCHUP'].unique()
                matchup = st.selectbox('Select Matchup', list(df_season_games.loc[df_season_games['GAME_DATE']==str(selected_date)]['MATCHUP']))
                game_id = str(df_season_games.loc[  (df_season_games['MATCHUP']==matchup) & 
                                                    (df_season_games['GAME_DATE']==str(selected_date))
                                                ]['GAME_ID'].tolist()[0])
                

    df = get_play_by_play(game_id)
    # Use Streamlit to create and display the plot
    st.pyplot(create_home_delta_plot(df))