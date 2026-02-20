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
url = "https://cricsheet.org/downloads/t20s_male_csv2.zip"

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

start_date = '2026-02-07' #yyyy-mm-dd
end_date = '2026-03-08' #yyyy-mm-dd

df['start_date'] = pd.to_datetime(df['start_date'])

df = df[(df['start_date'] >= pd.to_datetime(start_date))& (df['start_date'] <= pd.to_datetime(end_date))]

#################################

# if ('2025/26' in df['season'].unique()) or ('2026' in df['season'].unique()) or (2026 in df['season'].unique()):
#     df = df[df['season'].isin(['2025/26','2026',2026])]
# else:
#     df = df[df['season'].isin(['2024/25'])


#################################


######### Team List Starts ############
xi_strikers = ['MT Renshaw','BM Duckett','SA Yadav','Saim Ayub','GF Linde','PHKD Mendis','JC Buttler','Mohammad Nawaz','JO Holder','Abrar Ahmed','MJ Henry','BFW de Leede','Harmeet Singh','Noor Ahmad'] #2 remaning

thalasons = ['TM Head','RK Singh','MG Bracewell','PR Stirling','MD Shanaka','Sahibzada Farhan','AU Rashid','IS Sodhi','Abhishek Sharma','JA Duffy','JN Frylinck','Karan KC','JT Smuts','I Zadran']

super_knights = ['Shaheen Shah Afridi','JC Archer','C Green','JP Inglis','RD Rickelton','T Banton','Q de Kock','P Nissanka','Fakhar Zaman','Naseem Shah','AR Patel','R Ravindra',
                 'JJ Smit','AGS Gous','Waseem Muhammad']

sonu_48 = ['DA Miller','JJ Bumrah','M Pathirana','HH Pandya','GJ Maxwell','BKG Mendis','JG Bethell','SM Curran','C Bosch','Rashid Khan','A Zampa','Jatinder Singh','Sompal Kami','M Theekshana','HG Munsey']  #George munsey missing 

rcb = ['Babar Azam', 'J Little', 'L Wood','RL Chase','S Dube','SD Hope','TH David','AK Markram','KA Maharaj','L Ngidi','NT Ellis','T Stubbs'] #3 associate ramining

the_og_xi = ['D Brevis','MS Chapman','WG Jacks','M Jansen','J Charles','AJ Hosein','J Overton','JDS Neesham','CV Varun','PVD Chameera','Milind Kumar','MD Patel','SN Netravalkar','M Nabi'] #nabi missing

eleven_stars = ['BA King','LH Ferguson','Tilak Varma','R Powell','MP Stoinis','SE Rutherford','PD Salt','G Motie','R Shepherd','XC Bartlett','E Malinga','MW Forde','BJ McMullen','MRJ Watt','Shubham Ranjane'] #added 'ss ranjane'

blazing_titans = ['HC Brook','K Rabada','Usman Tariq','GH Dockrell','MDK Perera', 'MDKJ Perera','TL Seifert','FA Allen','SO Hetmyer','Kuldeep Yadav','Arshdeep Singh','MR Marsh',
                  'MJ Santner','DS Airee','SP Krishnamurthi','S Lamichhane','FH Allen'] # perera doubt

attackers = ['BJ Dwarshuis','Agha Salman','DP Conway','Ishan Kishan','GD Phillips','DJ Mitchell','Sikandar Raza','Shadab Khan',"MP O'Dowd",'LV van Beek','Ali Khan','S Atal','R Gurbaz','A Omarzai'] #3 remainig

######### Team List Enda ############

all_teams = {'attackers':attackers,
             'blazing_titans':blazing_titans,
             'eleven_stars':eleven_stars,
             'thalasons':thalasons,
             'the_og_xi':the_og_xi,
             'rcb':rcb,
             'sonu_48':sonu_48,
             'super_knights':super_knights,
             'xi_strikers':xi_strikers
}

def fantasy_points(df,total_points_df_download=0,rank_df_download=0):

    #Match Info
    match_info = df.groupby(['match_id']).agg({'batting_team':'first','bowling_team':'first'}).reset_index()

    match_info.rename(columns={'batting_team':'team_1','bowling_team':'team_2'}, inplace=True)

    #######################################################
    
    #######################################################

    afg_match_info = pd.DataFrame({'match_id':[1,2,3,4],
                                   'team_1':['Afghanisthan','Afghanisthan','Afghanisthan','Afghanisthan'],
                                   'team_2':['New Zealand','South Africa','United Arab Emirates','Canada']})
    
    match_info = pd.concat([match_info,afg_match_info])
    
    #######################################################
    
    #######################################################

    #captain and Vice-Captain Boost
    boost_df = pd.DataFrame({'player':['SA Yadav','Abhishek Sharma','C Green','HH Pandya','AK Markram','D Brevis','Tilak Varma','MR Marsh','Ishan Kishan',
                                       'Saim Ayub','TM Head','Q de Kock','SM Curran','S Dube','CV Varun','MP Stoinis','FA Allen','GD Phillips'],
                             'BOOST':[2,2,2,2,2,2,2,2,2,
                                      1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5]})
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


    #######################################
    #######################################
    #######################################

    afg_nz_batting_df = pd.DataFrame({'match_id':[1,1,1,1,1,1,1,1,1,1,1,1,
                                                  2,2,2,2,2,2,2,2,2,2,2,2,2,2],
                               'striker':['R Gurbaz','S Atal','I Zadran','M Nabi','A Omarzai','MS Chapman','TL Seifert','FA Allen','GD Phillips','DJ Mitchell','R Ravindra','MJ Santner',
                                          'R Gurbaz','S Atal','I Zadran','M Nabi','Rashid Khan','A Omarzai','Noor Ahmad',
                                          'D Brevis','DA Miller','M Jansen','RD Rickelton','Q de Kock','AK Markram','T Stubbs'], #'R Gurbaz','S Atal','I Zadran','M Nabi','A Omarzai'
                               'runs_off_bat':  [27,29,10,10,14,28,65,1,42,25,0,17,
                                                 84,0,12,5,20,22,15,23,20,16,61,59,5,1],
                               'is_batter_ball':[22,24,12,7,7,17,42,2,25,14,1,8,
                                                 42,3,10,6,12,17,9,19,15,7,28,41,8,2],
                               'is_batter_dot':[np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,
                                                np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan,np.nan],
                               'isfour':[2,2,1,0,0,2,7,0,7,1,0,2,
                                         4,0,1,0,3,3,0,1,1,2,5,5,1,0],
                               'issix': [1,0,0,1,2,1,3,0,1,1,0,1,
                                         7,0,1,0,0,0,2,1,1,1,4,3,0,0]})
    
    print("----------------\n",afg_nz_batting_df,"\n--------------")

    
    batting_df =
pd.concat([batting_df,afg_nz_batting_df])

    #########################################
    #########################################
    #########################################

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

    ####################################################
    ####################################################
    ####################################################

    afg_nz_bowling_df = pd.DataFrame({'match_id':[1,1,1,1,1,1,1,1,1,1,
                                                  2,2,2,2,2,2,2,2,2,2],
                               'bowler':['MJ Henry','JA Duffy','LH Ferguson','GD Phillips','JDS Neesham','R Ravindra','MJ Santner','M Nabi','Rashid Khan','A Omarzai',
                                         'L Ngidi','GF Linde','KA Maharaj','AK Markram','M Jansen','K Rabada','M Nabi','Rashid Khan','A Omarzai','Noor Ahmad'],
                               'is_bowler_runs':[27,30,40,12,33,14,23,18,36,40,
                                                 26,39,27,14,42,38,20,28,41,35],
                               'is_ball':[24,18,24,6,18,6,24,6,24,23,
                                          24,18,24,6,24,22,12,24,21,18],
                               'is_bowl_out':[1,1,2,0,0,1,0,1,1,1,
                                              3,1,1,0,1,1,0,2,3,0],
                               'isdot':[9,8,5,0,3,2,6,21,5,7,
                                        13,4,7,0,8,8,1,9,6,4],
                               'is_maiden':[0,0,0,0,0,0,0,0,0,0,
                                            0,0,0,0,0,0,0,0,0,0]})
    

    print('-----------------------\n',afg_nz_bowling_df,'\n-------------------------')
    bowling_df = pd.concat([bowling_df,afg_nz_bowling_df
])
    
    ####################################################
    ####################################################
    ####################################################
    # Economy, Wkt points, dot points, economy points
    bowling_df['economy'] = round(bowling_df['is_bowler_runs']/bowling_df['is_ball'] *6, 2)
    bowling_df['bowling_wkt_points'] = bowling_df['is_bowl_out'] * 35
    bowling_df['bowling_dot_points'] = bowling_df['isdot']
    bowling_df['bowling_economy_points'] = bowling_df.apply(lambda x: 0 if x['is_ball']<12 else
                                                            6 if x['economy'] < 5 else
                                                            4 if x['economy'] < 6 else
                                                            2 if x['economy'] < 7 else
                                                            -6 if x['economy'] > 12 else
                                                            -4 if x['economy'] > 11 else
                                                            -2 if x['economy'] > 10 else 0, axis=1)
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
                                                                      'blazing titans' if x in blazing_titans else
                                                                      'eleven_stars' if x in eleven_stars else
                                                                      'the_og_xi' if x in the_og_xi else
                                                                      'rcb' if x in rcb else
                                                                      'sonu_48' if x in sonu_48 else
                                                                      'super_knights' if x in super_knights else
                                                                      'xi_strikers' if x in xi_strikers else
                                                                      'thalasons' if x in thalasons else
                                                                      
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
    rank_df = pd.DataFrame({'teams': final_team_names[:len(all_teams)],
                        'points': final_team_points[:len(all_teams)]})

    rank_df['rank'] = rank_df['points'].rank(ascending=False, method='min')


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
matches_completed = total_points_df[(total_points_df['team_1'].isin([
'Afghanisthan','Australia','Canada','New Zealand',
'Netherlands','Pakistan','South Africa','West Indies','Scotland','India','United States of America','England','Nepal','Sri Lanka','Ireland','Oman','Zimbabwe','Namibia','United Arab Emirates','Italy'
]))|(total_points_df['team_2'].isin(['Afghanisthan','Australia','Canada','New Zealand','Netherlands','Pakistan','South Africa','West Indies','Scotland','India','United States of America','England','Nepa','Sri Lanka','Ireland','Oman','Zimbabwe','Namibia','United Arab Emirates','Italy'
])) ]['match_id'].nunique()

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

