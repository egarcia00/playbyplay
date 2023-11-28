import streamlit as st
import pandas as pd
import matplotlib as plt

# Assuming the get_play_by_play function is defined elsewhere and it returns a plot
from functions import get_play_by_play

# Load your data (adjust the path to your actual data file)
nba_games_id = pd.read_csv('nba_games_id.csv')

# Streamlit app
def main():
    st.title("NBA Play-by-Play Data Viewer")

    # Create a select box for matchups
    matchups = nba_games_id['MATCHUP'].unique()
    selected_matchup = st.selectbox("Select a Matchup", matchups)

    if selected_matchup:
        # Filter the DataFrame for the selected matchup and get the first game ID
        filtered_df = nba_games_id[nba_games_id['MATCHUP'] == selected_matchup]
        if not filtered_df.empty:
            game_id = filtered_df['GAME_ID'].iloc[0]

            # Get the play-by-play plot for the selected game
            plot = get_play_by_play(game_id)

            # Display the plot
            st.pyplot(plot)

if __name__ == "__main__":
    main()
