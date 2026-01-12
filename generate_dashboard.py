import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings 
warnings.filterwarnings('ignore')

pd.set_option('display.max_rows',None)
pd.set_option('display.max_columns',None)
pd.set_option('display.expand_frame_repr',False)
pd.set_option('max_colwidth',25)

import pandas as pd
import requests
import zipfile
import io

# Cricsheet IPL CSV ZIP
url = "https://cricsheet.org/downloads/wpl_female_csv2.zip"

# Download ZIP into memory
response = requests.get(url)
zip_bytes = io.BytesIO(response.content)

dfs = []

# Open ZIP in memory
with zipfile.ZipFile(zip_bytes) as z:
    for file in z.namelist():
        
        # Only match CSVs (skip _info.csv)
        if file.endswith(".csv") and "_info" not in file:
            
            with z.open(file) as f:
                df = pd.read_csv(f)
                df["match_file"] = file   # optional: track source
                dfs.append(df)

# Merge all matches
all_matches_df = pd.concat(dfs, ignore_index=True)

df = all_matches_df.copy()

if ('2025/26' in df['season'].unique()) or ('2026' in df['season'].unique()) or (2026 in df['season'].unique()):
    df = df[df['season'].isin(['2025/26','2026',2026])]
else:
    df = df[df['season'].isin(['2024/25'])]

attackers = ['KE Bryce','H Deol','SD Bahadur', 'S Ishaque', 'SB Pokharkar', 'S Sajana', 'S Mandhana', 'MM Lanning', 'A King', 'CE Dean', 'Shafali Verma']
bcc = ['AB Kaur', 'PP Bala', 'AC Jayangani', 'M Kapp', 'MS Kashyap', 'TN Pathan', 'PG Chopra', 'Simran Shaikh', 'Meghna Singh', 'KJ Garth', 'A Capsey']
blazing_titans = ['A Sutherland', 'BL Mooney', 'LMM Tahuhu', 'TR Sadhu', 'IECM Wong', 'GM Harris', 'SJ Bryce', 'BS Fulmali', 'Komal Zanzad', 'CA Henry', 'K Goud']
eleven_stars = ['A Reddy', 'G Voll', 'TM McGrath', 'Ashwani Kumari', 'N de Klerk', 'JN Kalita', 'SIR Dunkley', 'S Meghana', 'S Rana', 'DB Sharma', 'VJ Joshitha']
kingslayers =['DJS Dottin', 'RP Yadav', 'NS Prasad', 'H Kaur', 'HK Matthews', 'JI Rodrigues', 'AC Kerr', 'EA Perry', 'Raghvi Bist', 'S Sehrawat', 'KS Gautam']
super_kings =['TP Kanwar', 'DP Vaidya', 'S Ecclestone', 'NR Sciver-Brunt', 'SB Keerthana', 'DV Gujjar', 'HY Kazi', 'M Joshi', 'E Bisht', 'S Molineux', 'SV Yashasri']
knights = ['DR Gibson', 'N Shree Charani', 'KS Ahuja', 'L Wolvaardt', 'PS Sisodia', 'RS Gayakwad', 'D Vrinda', 'S Gupta', 'SS Pawar', 'V Krishnamurthy', 'JL Jonassen']
thalasons = ['SFM Devine', 'P Litchfield', 'S Pandey', 'M Mani', 'YH Bhatia', 'SG Satghare', 'K Anjali Sarvani', 'S Ismail', 'KP Navgire', 'SZ Thakor', 'TG Norris']
troublemaker_kings =['ML Schutt', 'S Verma', 'S Asha', 'T Bhatia', 'RM Ghosh', 'P Rawat', 'G Wareham', 'Poonam Yadav', 'DD Kasat', 'G Kamalini', 'H Graham']
vsk = ['EA Burns', 'DN Wyatt', 'G Sultana', 'D Hemalatha', 'Priya Mishra', 'U Chetry', 'HC Knight', 'AJ Healy', 'A Gardner', 'PN Khemnar', 'P Vastrakar']


all_teams = {'attackers':attackers,
             'bcc':bcc,
             'blazing_titans':blazing_titans,
             'eleven_stars':eleven_stars,
             'kingslayers':kingslayers,
             'super_kings':super_kings,
             'knights':knights,
             'thalasons':thalasons,
             'troublemaker_kings':troublemaker_kings,
             'vsk':vsk
}

def fantasy_points(df,total_points_df_download=0,rank_df_download=0):

    #Match Info
    match_info = df.groupby(['match_id']).agg({'batting_team':'first','bowling_team':'first'}).reset_index()

    match_info.rename(columns={'batting_team':'team_1','bowling_team':'team_2'}, inplace=True)

    #captain and Vice-Captain Boost
    boost_df = pd.DataFrame({'player':[],
                             'BOOST':[]})
    boost_df['player'] = boost_df['player'].astype('str')

    #Featue Engineering

    # Dot,1s ,2s, 3s, 4s, 6s
    df['isdot'] = ( (df['runs_off_bat']==0) & (df['wides'].isna()) & (df['noballs'].isna()) ).astype(int)
    df['is_batter_dot'] = ((df['runs_off_bat']==0) & (df['wides'].isna()) ).astype(int)
    df['isone'] = df['runs_off_bat'].apply(lambda x: 1 if x == 1 else 0)
    df['istwo'] = df['runs_off_bat'].apply(lambda x: 1 if x == 2 else 0)
    df['isthree'] = df['runs_off_bat'].apply(lambda x: 1 if x == 3 else 0)
    df['isfour'] = df['runs_off_bat'].apply(lambda x: 1 if x == 4 else 0)
    df['issix'] = df['runs_off_bat'].apply(lambda x: 1 if x == 6 else 0)

    # Bowler Runs, Over No
    df['is_bowler_runs'] = df['runs_off_bat'].fillna(0) + df['wides'].fillna(0) +df['noballs'].fillna(0) 
    df['over_no'] = df['ball'].apply(np.ceil)

    # Is Ball?
    df['is_ball'] = (df['wides'].isna() & df['noballs'].isna()).astype(int)
    df['is_batter_ball'] = (1 & df['wides'].isna()).astype(int)

    # Is bowler Wicket
    df['is_bowl_out'] = np.where(df['wicket_type'].isin(['caught', 'bowled',  'lbw', 'caught and bowled',
       'stumped', 'hit wicket']),1,0)

    #Batting Points

    #Groupby Batting df
    batting_df = df.groupby(['match_id','striker']).agg({'runs_off_bat':'sum','is_batter_ball':'sum','is_batter_dot':'sum','isfour':'sum','issix':'sum'}).reset_index()

    # Bat SR, bat points, boundary points, run Bonus
    batting_df['sr'] = round(batting_df['runs_off_bat']/batting_df['is_batter_ball'] * 100,2)
    batting_df['batting_points'] = batting_df['runs_off_bat']
    batting_df['batting_boundary_points'] = batting_df['isfour']*4 + batting_df['issix']*6
    batting_df['batting_run_bonus'] = batting_df['runs_off_bat'].apply(lambda x: 16 if x>=100 else(
                                                                                    12 if x>=75 else(
                                                                                        8 if x>=50 else(
                                                                                            4 if x>=25 else
                                                                                                -2 if x==0 else 0))   
                                                                    ))
    batting_df['batting_sr_points'] = batting_df.apply(lambda x : 0 if x['is_batter_ball']<10 else
                                                    6 if x['sr'] > 170 else 
                                                    4 if x['sr'] > 150 else
                                                    2 if x['sr'] > 130 else
                                                    -6 if x['sr'] < 50 else
                                                    -4 if x['sr'] < 60 else
                                                    -2 if x['sr'] < 70 else 0, axis=1)
    batting_df.rename(columns={'striker':'player'}, inplace=True)
    batting_df['total_batting_points'] = batting_df['batting_points'] + batting_df['batting_boundary_points'] + batting_df['batting_run_bonus'] + batting_df['batting_sr_points']

    #Bowler Points
    
    # Groupby Bowler df for Maiden
    bowling_df = df.groupby(['match_id','bowler','over_no']).agg({'is_bowler_runs':'sum','is_ball':'sum','is_bowl_out':'sum','isdot':'sum'}).reset_index()

    # Is maiden
    bowling_df['is_maiden'] = bowling_df.apply(lambda x: 1 if ((x['is_bowler_runs']==0) & (x['isdot']==6)) else 0, axis=1)

    # # Groupby Bowler df
    bowling_df = bowling_df.groupby(['match_id','bowler']).agg({'is_bowler_runs':'sum','is_ball':'sum','is_bowl_out':'sum','isdot':'sum','is_maiden':'sum'}).reset_index()

    # Economy, Wkt points, dot points, economy points
    bowling_df['economy'] = round(bowling_df['is_bowler_runs']/bowling_df['is_ball'] *6, 2)
    bowling_df['bowling_wkt_points'] = bowling_df['is_bowl_out'] * 35
    bowling_df['bowling_dot_points'] = bowling_df['isdot']
    bowling_df['bowling_economy_points'] = bowling_df.apply(lambda x: 0 if x['is_ball']<12 else
                                                            6 if x['economy'] < 5 else
                                                            4 if x['economy'] < 6 else
                                                            2 if x['economy'] < 7 else
                                                            -2 if x['economy'] > 12 else
                                                            -4 if x['economy'] > 11 else
                                                            -6 if x['economy'] > 10 else 0, axis=1)
    bowling_df['bowling_wkt_bonus'] = bowling_df['is_bowl_out'].apply(lambda x: 12 if x >= 5 else
                                                                    8 if x >= 4 else
                                                                    4 if x >= 3 else 0)
    bowling_df['bowling_maiden_points'] = bowling_df['is_maiden'] * 12

    bowling_df.rename(columns={'bowler':'player'}, inplace=True)

    bowling_df['total_bowling_points'] = bowling_df['bowling_wkt_points'] + bowling_df['bowling_economy_points'] + bowling_df['bowling_dot_points'] + bowling_df['bowling_wkt_bonus'] +bowling_df['bowling_maiden_points'] 

    #Merging Bat_df , bowl_df , boost_df
    total_points_df = pd.merge(batting_df,bowling_df, on=['match_id','player'], how='outer')
    total_points_df = total_points_df.merge(match_info, on=['match_id'],how='outer')

    # Add Total_points clmn
    total_points_df['total_batting_points'].fillna(0, inplace=True)
    total_points_df['total_bowling_points'].fillna(0, inplace=True)

    total_points_df['total_points'] = total_points_df['total_batting_points'] + total_points_df['total_bowling_points']

    total_points_df['auction_team'] = total_points_df['player'].apply(lambda x: 'attackers' if x in attackers else
                                                                      'bcc' if x in bcc else
                                                                      'blazing titans' if x in blazing_titans else
                                                                      'eleven_stars' if x in eleven_stars else
                                                                      'kingslayers' if x in kingslayers else
                                                                      'super kings' if x in super_kings else
                                                                      'super knights' if x in knights else
                                                                      'troublemaker_kings' if x in troublemaker_kings else
                                                                      'thalasons' if x in thalasons else
                                                                      'vsk' if x in vsk else 
                                                                      np.nan)

    ###########################
    # Download total_points_df to get match by match player points
    ############################
    
    #Final df Total points for Players
    final_df = total_points_df.groupby(['player']).agg({'total_points':'sum', 'auction_team':'first'}).reset_index().sort_values(by='total_points',ascending=False)
    final_df.rename(columns={'total_points':'points'},inplace=True)

    # Adding Captaincy boost for player
    final_df = final_df.merge(boost_df, on='player',how='outer')
    final_df['BOOST'] = final_df['BOOST'].fillna(1)
    final_df['total_points'] = final_df['points'] * final_df['BOOST']

    #Adding Team and Team Points in Dictionary
    final_team_points_dict = {}

    for team_name, players in all_teams.items():
        final_team_points_dict[f'{team_name}'] = final_df[final_df['player'].isin(players)]['total_points'].sum()

    final_team_names = list(final_team_points_dict.keys()) # Storing Team names in a list
    final_team_points = list(final_team_points_dict.values()) # Storing Team Points In a List

    #ranking the points 
    rank_df = pd.DataFrame({'teams': final_team_names[:10],
                        'points': final_team_points[:10]})

    rank_df['rank'] = rank_df['points'].rank(ascending=False)


    ########################
    # Final Points Table for Auction
    rank_df = rank_df.sort_values(by='rank')
    ########################

    if total_points_df_download == 1:
        total_points_df.to_csv('Player Points 2025 Match by Match.csv', index=False)
    if rank_df_download == 1:
        rank_df.to_csv('Rank_df.csv', index=False)
    # print(total_points_df)
    print(rank_df)
    print('No. of Matches completed ', df['match_id'].nunique())
    # print(total_points_df[total_points_df['auction_team']=='super knights'].head(100))

    return rank_df, total_points_df


rank_df, total_points_df = fantasy_points(df,total_points_df_download=0,rank_df_download=0)
matches_completed = df['match_id'].nunique()

# =========================
# BUILD HTML FROM TEMPLATE
# =========================

# ---------- BUILD HTML (CORRECT WAY) ----------

rank_json = rank_df.to_json(orient="records")
points_json = total_points_df.fillna("").to_json(orient="records")

# 🔑 ALWAYS READ TEMPLATE
with open("template.html", "r", encoding="utf-8") as f:
    html = f.read()

html = html.replace("{{RANK_DATA}}", rank_json)
html = html.replace("{{POINTS_DATA}}", points_json)
html = html.replace("{{MATCHES_COMPLETED}}", str(matches_completed))

# 🔑 ALWAYS WRITE INDEX
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("index.html updated successfully")

