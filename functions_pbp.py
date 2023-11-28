from nba_api.stats.endpoints import playbyplayv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_play_by_play(GAME_ID,perspective='HomeScore'):
    # Fetch the play-by-play data for the specified game
    play_by_play = playbyplayv2.PlayByPlayV2(game_id=GAME_ID)

    # Extract the data to a DataFrame
    play_by_play = play_by_play.get_data_frames()[0]
    play_by_play = play_by_play[['PERIOD','PCTIMESTRING','SCORE']]
    play_by_play = play_by_play.fillna(value=np.nan)
    play_by_play['HomeScore'] = play_by_play['SCORE'].str.split('-',expand=True).fillna(value=np.nan)[0]
    play_by_play['AwayScore'] = play_by_play['SCORE'].str.split('-',expand=True).fillna(value=np.nan)[1]
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

    # Merge with original data
    merged_df = pd.merge(template_df, original_df, 
                        left_on=['PERIOD', 'PCTIMESTRING'], 
                        right_on=['PERIOD', 'PCTIMESTRING'], 
                        how='left')


    # Find max SCORE for each PERIOD & PCTIMESTRING combination
    merged_df['HomeScore'] = merged_df.groupby(['PERIOD', 'PCTIMESTRING'])['HomeScore'].transform('max')
    merged_df['AwayScore'] = merged_df.groupby(['PERIOD', 'PCTIMESTRING'])['AwayScore'].transform('max')
    # Fill null values with previous value
    merged_df['HomeScore'] = merged_df['HomeScore'].fillna(method='bfill')
    merged_df['AwayScore'] = merged_df['AwayScore'].fillna(method='bfill')
    # fig, ax = plt.subplots()
    # ax.plot(merged_df[perspective])
    
    
    return merged_df