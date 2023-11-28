from nba_api.stats.endpoints import playbyplayv2
from nba_api.stats.endpoints import leaguegamelog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

def get_play_by_play(GAME_ID,perspective='HomeScore'):
    # Fetch the play-by-play data for the specified game
    play_by_play = playbyplayv2.PlayByPlayV2(game_id=GAME_ID)

    # Extract the data to a DataFrame
    play_by_play = play_by_play.get_data_frames()[0]
    play_by_play = play_by_play[['PERIOD','PCTIMESTRING','SCORE']]
    play_by_play = play_by_play.fillna(value=np.nan)
    
    play_by_play['HomeScore'] = play_by_play['SCORE'].str.split('-',expand=True)[0]#.fillna(value=np.nan)[0]
    play_by_play['AwayScore'] = play_by_play['SCORE'].str.split('-',expand=True)[1]#.fillna(value=np.nan)[1]
    play_by_play['HomeScore'] = pd.to_numeric(play_by_play['HomeScore'])
    play_by_play['AwayScore'] = pd.to_numeric(play_by_play['AwayScore'])
    play_by_play['HomeDelta'] = play_by_play['HomeScore'] - play_by_play['AwayScore']
    play_by_play['AwayDelta'] = -play_by_play['HomeDelta']
    play_by_play['PCTIMESTRING']= play_by_play['PCTIMESTRING'].apply(lambda x: ':'.join(part.zfill(2) for part in x.split(':')))
    
    original_df = play_by_play[['PERIOD','PCTIMESTRING','HomeScore','AwayScore']]

    # Create template DataFrame
    periods = range(1, 5)
    times = pd.date_range("00:12:00", "00:00:00", freq="-1S").strftime('%M:%S').tolist()
    template_df = pd.DataFrame([(p, t) for p in periods for t in times], columns=['PERIOD', 'PCTIMESTRING'])
    print(template_df.shape)
    # Merge with original data
    merged_df = pd.merge(template_df, original_df, 
                        left_on=['PERIOD', 'PCTIMESTRING'], 
                        right_on=['PERIOD', 'PCTIMESTRING'], 
                        how='left')
    print(merged_df.shape)

    # Find max SCORE for each PERIOD & PCTIMESTRING combination
    # merged_df['HomeScore'] = merged_df.groupby(['PERIOD', 'PCTIMESTRING'])['HomeScore'].transform('max')
    # merged_df['AwayScore'] = merged_df.groupby(['PERIOD', 'PCTIMESTRING'])['AwayScore'].transform('max')
    # Fill null values with previous value
    merged_df['HomeScore'] = merged_df['HomeScore'].fillna(method='bfill')
    merged_df['AwayScore'] = merged_df['AwayScore'].fillna(method='bfill')
    merged_df['HomeDelta'] = merged_df['HomeScore']-merged_df['AwayScore']
    merged_df['TotalPoints'] = merged_df['HomeScore']+merged_df['AwayScore']
    merged_df = merged_df[['PERIOD', 'PCTIMESTRING','HomeDelta','TotalPoints']]
    
    # Find the rows with the highest TotalPoints for each unique combination
    unique_combinations = merged_df.groupby(['PERIOD', 'PCTIMESTRING'])['TotalPoints'].idxmax()

    # Use the above indices to select the corresponding rows
    result_df = merged_df.loc[unique_combinations]

    # Sort the result by index in ascending order
    result_df.sort_index(ascending=True, inplace=True)

    # Reset the index
    result_df.reset_index(drop=True, inplace=True)

    return result_df

def create_home_delta_plot(df):
    
    fig, ax = plt.subplots()
    ax.plot(df['HomeDelta'])
    ax.hlines(y=0, xmin=0, xmax=df.shape[0], colors='black')

    for period in range(1, 5):
        ax.vlines(x=(60 * 12 * period),
                  ymin=df['HomeDelta'].min(),
                  ymax=df['HomeDelta'].max(),
                  colors='gray',
                  ls='--'
                  )
    
    for period in range(5, (df['PERIOD'].max() + 1)):
        ax.vlines(x=(60 * 5 * period),
                  ymin=df['HomeDelta'].min() // 5,
                  ymax=df['HomeDelta'].max(),
                  colors='gray',
                  ls='--'
                  )
    
    y_ticks = np.arange(((df['HomeDelta'].min() // 5)) * 5, ((df['HomeDelta'].max() // 5) + 2) * 5, 5)
    plt.yticks(y_ticks)
    
    x_labels = [(12 * 60 * 1), (12 * 60 * 2), (12 * 60 * 3), (12 * 60 * 4)]
    plt.xticks(x_labels, labels=['Q1', 'Q2', 'Q3', 'Q4'])
    
    plt.xlabel('Period / time (s)')
    plt.ylabel('Home Delta')

    return fig

def get_all_nba_games(season):
    # Initialize an empty list to store game data
    all_games = []

    # Specify the range of seasons you want to cover
    # For example, from the 1946-47 season to the 2020-21 season
    season_str = f"{season}-{str(season+1)[-2:]}"
    # print(f"Fetching games for season: {season_str}")

    for game_type in ["Playoffs","Regular Season"]:
        # Fetch the game logs for the season
        game_log = leaguegamelog.LeagueGameLog(season=season_str,season_type_all_star=game_type)
        games = game_log.get_data_frames()[0]

        # Append the data to the all_games list
        all_games.append(games)

        # Combine all seasons into a single DataFrame
        all_games_df = pd.concat(all_games, ignore_index=True)
    filtered_df = all_games_df[~all_games_df["MATCHUP"].str.contains("@")]
    filtered_df = filtered_df.reset_index(drop=True)
    return filtered_df
