import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import playbyplayv2
from nba_api.stats.endpoints import leaguegamelog

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
        all_games_df = all_games_df[['GAME_ID',	'GAME_DATE', 'MATCHUP',	'TEAM_ID']]
        all_games_df = all_games_df.sort_values(by=['GAME_DATE','GAME_ID'])

        # Identifying the home and away teams.
        home_team_row = all_games_df[~all_games_df['MATCHUP'].str.contains('@')]
        away_team_row = all_games_df[all_games_df['MATCHUP'].str.contains('@')]

        # Constructing the target DataFrame.
        target_state_data = {
            'GAME_ID': home_team_row['GAME_ID'].values,
            'GAME_DATE': home_team_row['GAME_DATE'].values,
            'MATCHUP': home_team_row['MATCHUP'].str.replace('@', 'vs.').str.strip(),
            'HOMETEAM_ID': home_team_row['TEAM_ID'].values,
            'AWAYTEAM_ID': away_team_row['TEAM_ID'].values
        }

        # Creating the DataFrame for the target state.
        target_df = pd.DataFrame(target_state_data)

    return target_df

def get_starting_lineup(GAME_ID, TEAM_ID):
    game_id =  GAME_ID
    boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    boxscore_df = boxscore.get_data_frames()[0]
    starting_lineup = list(boxscore_df.loc[boxscore_df['TEAM_ID']==TEAM_ID][0:5]["PLAYER_ID"])
    return starting_lineup

def get_lead_timeline(GAME_ID):
    play_by_play = playbyplayv2.PlayByPlayV2(game_id=GAME_ID)

    play_by_play = play_by_play.get_data_frames()[0]
    play_by_play = play_by_play[['PERIOD','PCTIMESTRING','SCORE']]
    play_by_play = play_by_play.fillna(value=np.nan)
    
    play_by_play['HomeScore'] = play_by_play['SCORE'].str.split('-',expand=True)[0]#.fillna(value=np.nan)[0]
    play_by_play['AwayScore'] = play_by_play['SCORE'].str.split('-',expand=True)[1]#.fillna(value=np.nan)[1]
    play_by_play['HomeScore'] = pd.to_numeric(play_by_play['HomeScore'])
    play_by_play['AwayScore'] = pd.to_numeric(play_by_play['AwayScore'])

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
    # Fill null values with previous value
    merged_df['HomeScore'] = merged_df['HomeScore'].fillna(method='bfill')
    merged_df['AwayScore'] = merged_df['AwayScore'].fillna(method='bfill')
    
    merged_df['HomeDelta'] = merged_df['HomeScore']-merged_df['AwayScore']
    merged_df['AwayDelta'] = -merged_df['HomeDelta']

    merged_df['HomeDif'] = merged_df['HomeDelta'].diff() 
    merged_df['HomeDif'].iloc[0] = merged_df['HomeDelta'].iloc[0]

    merged_df['AwayDif'] = merged_df['AwayDelta'].diff() 
    merged_df['AwayDif'].iloc[0] = merged_df['AwayDelta'].iloc[0]

    merged_df['TotalPoints'] = merged_df['HomeScore']+merged_df['AwayScore']
    merged_df = merged_df[['PERIOD', 'PCTIMESTRING','HomeDelta','HomeDif','AwayDelta','AwayDif','TotalPoints']]
    
    # Find the rows with the highest TotalPoints for each unique combination
    unique_combinations = merged_df.groupby(['PERIOD', 'PCTIMESTRING'])['TotalPoints'].idxmax()

    # Use the above indices to select the corresponding rows
    result_df = merged_df.loc[unique_combinations]

    # Sort the result by index in ascending order
    result_df.sort_index(ascending=True, inplace=True)

    # Reset the index
    result_df.reset_index(drop=True, inplace=True)

    return result_df

def get_lineup_log(GAME_ID, HOMETEAM_ID, AWAYTEAM_ID):
    HOME_STARTING_LINEUP = get_starting_lineup(GAME_ID, HOMETEAM_ID)
    HOME_STARTING_LINEUP.insert(0,HOMETEAM_ID)
    HOME_STARTING_LINEUP.insert(1,1)
    HOME_STARTING_LINEUP.insert(2,"12:00")

    AWAY_STARTING_LINEUP = get_starting_lineup(GAME_ID, AWAYTEAM_ID)
    AWAY_STARTING_LINEUP.insert(0,AWAYTEAM_ID)
    AWAY_STARTING_LINEUP.insert(1,1)
    AWAY_STARTING_LINEUP.insert(2,"12:00")

    boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=GAME_ID)
    boxscore_df = boxscore.get_data_frames()[0]

    playbyplay = playbyplayv2.PlayByPlayV2(game_id=GAME_ID)
    playbyplay_df = playbyplay.get_data_frames()[0]

    DESCRIPTION_STRING = ["HOMEDESCRIPTION", "VISITORDESCRIPTION"]
    TEAMS_ID = [HOMETEAM_ID, AWAYTEAM_ID]
    STARTING_LINEUP = [HOME_STARTING_LINEUP, AWAY_STARTING_LINEUP]

    lineup_df = pd.DataFrame(columns=['TEAM_ID','PERIOD','PCTIMESTRING','PLAYER1','PLAYER2','PLAYER3','PLAYER4','PLAYER5'])

    for j, team_description in enumerate(DESCRIPTION_STRING):
        lineup_df.loc[len(lineup_df)] = STARTING_LINEUP[j]
        substitutions_log = playbyplay_df[playbyplay_df[team_description].str.contains('sub', case=False)&
                                        playbyplay_df[team_description].notna()
                                        ]
        substitutions_log['TEAM_ID'] = TEAMS_ID[j]

        substitutions_log = substitutions_log[['TEAM_ID','PERIOD','PCTIMESTRING',team_description,
                                            'PLAYER1_ID','PLAYER1_NAME','PLAYER2_ID','PLAYER2_NAME']]
        substitutions_log = substitutions_log.reset_index(drop=True)


    # substitutions_log
        for i in range(0,len(substitutions_log)):
            PERIOD_SUB = substitutions_log['PERIOD'].values[i]
            PCTIMESTRING_SUB = substitutions_log['PCTIMESTRING'].values[i]
            player_out = substitutions_log['PLAYER1_ID'].values[i]
            player_in  = substitutions_log['PLAYER2_ID'].values[i]
            
            previous_lineup = list(lineup_df.loc[len(lineup_df)-1].values)
            new_lineup = previous_lineup
            new_lineup[0] = TEAMS_ID[j]
            new_lineup[1] = PERIOD_SUB
            new_lineup[2] = PCTIMESTRING_SUB
            new_lineup = [player_in if x == player_out else x for x in new_lineup]
            lineup_df.loc[len(lineup_df)] = new_lineup

            idx = lineup_df.groupby(['TEAM_ID','PERIOD', 'PCTIMESTRING'])['PLAYER1'].idxmax()
            clean_lineup_df = lineup_df.loc[idx].sort_index().reset_index(drop=True)
            clean_lineup_df['PCTIMESTRING']= clean_lineup_df['PCTIMESTRING'].apply(lambda x: ':'.join(part.zfill(2) for part in x.split(':')))

    # clean_lineup_df = clean_lineup_df.sort_values(by=['PERIOD','PCTIMESTRING'], ascending=[True, False]).reset_index(drop=True)
    return clean_lineup_df

# def lead_timeline_lineup(GAME_ID, HOMETEAM_ID, AWAYTEAM_ID):

def lead_timeline_lineup(GAME_ID, HOMETEAM_ID, AWAYTEAM_ID):
    lineup_df = get_lineup_log(GAME_ID, HOMETEAM_ID, AWAYTEAM_ID)
    lead_timeline = get_lead_timeline(GAME_ID)
    
    merged_df = pd.merge(lead_timeline, lineup_df, 
                        left_on=['PERIOD', 'PCTIMESTRING'], 
                        right_on=['PERIOD', 'PCTIMESTRING'], 
                        how='left')
    
    return merged_df