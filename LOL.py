
from pickle import TRUE
from re import A
import pandas as pd
import time
import csv

api_key = 'RGAPI-2b6ab534-51a6-4680-9a1b-53c11b0a6030'

def get_summoner_rank(summoner_name):
    link = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + summoner_name +'?api_key=' + api_key 
    r = requests.get(link)

    return r.json()['puuid']

def get_rankINF_from_id(id):
    rank_url = 'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/' + id +'?api_key=' + api_key 
    r = requests.get(rank_url)
    return r.json()


def get_grandmaster_id():
    grandmaster = 'https://na1.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key=' + api_key
    r = requests.get(grandmaster)
    league_df = pd.DataFrame(r.json())
    
    league_df.reset_index(inplace=True)
    league_entries_df = pd.DataFrame(dict(league_df['entries'])).T
    league_df = pd.concat([league_df, league_entries_df], axis=1)
    
    league_df = league_df.drop(['index', 'queue', 'name', 'leagueId', 'entries', 'rank'], axis = 1)
    league_df.info()
    league_df['puuid'] = "NULL"
    for i in range(len(league_df)):
        try:
            puuid_url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + league_df['summonerName'].iloc[i] +'?api_key=' + api_key 
            r2 = requests.get(puuid_url)
        
            while r2.status_code == 429:
                print("sleep")
                time.sleep(5)
                puuid_url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + league_df['summonerName'].iloc[i] +'?api_key=' + api_key 
                r2 = requests.get(puuid_url)
        
            puuid = r2.json()['puuid']
            league_df.iloc[i, -1] = puuid
           
        except:
            pass
        
    league_df.to_csv("grandmaster_data.csv", index=False)
    return league_df

def get_match_id():
    file = open('grandmaster_data.csv')
    csvreader = csv.reader(file)
    puuid = []
    for row in csvreader:
        i = row[-1]
        if i == "NULL":
            continue
        else:
            puuid.append(i)
    puuid = puuid[1:]
    
    match_id = []

    for i in range(len(puuid)):
        try:
            match_url = 'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/'+ puuid[i] + '/ids?start=0&count=100' + "&api_key=" + api_key
            r = requests.get(match_url)
        
            while r.status_code == 429:
                print("sleep")
                time.sleep(5)
                match_url = 'https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/'+ puuid[i] + '/ids?start=0&count=100' + "&api_key=" + api_key
                r = requests.get(match_url)
        
            matches = r.json()
            match_id.append(matches)
            
        except:
            pass
        
    match_df = pd.DataFrame(match_id).T
    match_df.to_csv("match_id_data.csv", index=False)

def get_matchINF():
    file = open("match_id_data.csv")
    match_id = csv.reader(file)
    match_df = pd.DataFrame(match_id)
    match_df = match_df.drop(index=0, axis = 0)
    
    matchINF = []    
    for i in range(match_df.shape[1]):
        for j in range(match_df.shape[0]):
            try:
                url = 'https://americas.api.riotgames.com/lol/match/v5/matches/' + match_df.iat[i, j] + '?api_key=' + api_key
                r = requests.get(url)
                
                while r.status_code == 429:
                    print("sleep", r.status_code)
                    time.sleep(5)
                    url = 'https://americas.api.riotgames.com/lol/match/v5/matches/' + match_df.iat[i, j] + '?api_key=' + api_key                 
                    r = requests.get(url)
                    
                print("break", r.status_code)
                matchINF.append(r.json())
            
            except:
                pass
        
    matchINF = pd.DataFrame(matchINF)
    matchINF.to_csv('match_ionformation.csv', index=False)

def match_information_edit():
    '''
    matchINF_df.drop(index = 0, inplace=True)
    list1 = []
    list2 = []
    for i in range(matchINF_df.shape[0]):
        list1.append(ast.literal_eval(matchINF_df.iloc[i][0]))
        list2.append(ast.literal_eval(matchINF_df.iloc[i][1]))

    dataFrame1 = pd.DataFrame.from_dict(list1)
    dataFrame2 = pd.DataFrame.from_dict(list2)
    print(dataFrame2['participants'][0])

    dataFrame3 = pd.concat([dataFrame1, dataFrame2], axis = 1)
    dataFrame3.drop(['dataVersion', 'gameCreation', 'gameEndTimestamp', 'gameName', 'gameStartTimestamp', 'gameVersion', 'platformId'], axis = 1 , inplace=True)
    dataFrame3.to_csv("match_information_4.csv")
    '''   
    matchINF_df = pd.read_csv('/Users/hyunsukbang/match_information_4.csv')
    matchINF_df.drop(['Unnamed: 0'], axis = 1 , inplace=True)
    #print(matchINF_df['teams'])
    lst = list(matchINF_df['teams'])
    for i in range(len(lst)):
        lst[i] = eval(lst[i])
    
    #create inital data Frame
    lst[i][0].pop('bans', None)
    team1 = pd.DataFrame(list(lst[i][0].items()), index = list(lst[i][0].keys())).T
    team1 = team1.drop([0], axis = 0)

    lst[i][1].pop('bans', None)
    team2 = pd.DataFrame(list(lst[i][1].items()), index = list(lst[i][1].keys())).T
    team2 = team2.drop([0], axis = 0)
    
    #append with 
    for i in range(1, len(lst)):
        try:
            lst[i][0].pop('bans', None)
            team = pd.DataFrame(list(lst[i][0].items()), index = list(lst[i][0].keys())).T
            team = team.drop([0], axis = 0)
            team1 = team1.append(team, ignore_index=True)
            
        except:
            pass
    
    for i in range(1, len(lst)):
        try:
            lst[i][1].pop('bans', None)
            team = pd.DataFrame(list(lst[i][1].items()), index = list(lst[i][1].keys())).T
            team = team.drop([0], axis = 0)
            team2 = team2.append(team, ignore_index=True)
            
        except:
            pass
        
    
    final_data = pd.concat([team1, team2 ,matchINF_df[['gameDuration']]], axis = 1)
    final_data.to_csv("final_data.csv", index = False)

    '''
    lst[0][0].pop('bans', None)
    lst[0][1].pop('bans', None)
    team1 = pd.DataFrame(list(lst[0][0].items()), index = list(lst[0][0].keys())).T
    team1 = team1.drop([0], axis = 0)
    team2 = pd.DataFrame(list(lst[0][1].items()), index = list(lst[0][1].keys())).T
    team2 = team2.drop([0], axis = 0)
    team1 = team1.append(team2, ignore_index=True)
    team1.to_csv("1.csv", index=False) 
    '''

def team_sep(df):
    data = pd.read_csv(df)
    gameDuration = data['gameDuration']
    team1 = data.iloc[:,[0,1,2]]
    team2 = data.iloc[:, [3,4,5]]
    team1 = pd.concat([team1, gameDuration], axis = 1)
    team2 = pd.concat([team2, gameDuration], axis = 1)
    return [team1, team2]

def final_data(data):
    try:
        lst = list(data['objectives'])
        data = data.drop('objectives', axis = 1)
    except:
        lst = list(data['objectives.1']) 
        data = data.drop('objectives.1', axis = 1)
    
    
    final = pd.DataFrame(columns=['baron_fst',  'baron_kills', 'champ_fst', 'champ_kills', 'drg_fst', 'drg_kill', 'inhib_fst', 'inhib_kills', 'rf_fst', 'rf_kills', 'tw_fst', 'tw_kills'])
    

    for i in range(len(lst)):
        try:
            a = eval(lst[i])

            baron_fst = a['baron']['first']
            baron_kill = a['baron']['kills']
            
            champ_fst = a['champion']['first']
            champ_kill = a['champion']['kills']
            
            drg_fst = a['dragon']['first']
            drg_kill = a['dragon']['kills']
            
            inhib_fst = a['inhibitor']['first']
            inhib_kill = a['inhibitor']['kills']

            rf_fst = a['riftHerald']['first']
            rf_kill = a['riftHerald']['kills']
            
            tw_fst = a['tower']['first']
            tw_kill = a['tower']['kills']
            
            l = [baron_fst, baron_kill, champ_fst, champ_kill, drg_fst, drg_kill, inhib_fst, inhib_kill, rf_fst,rf_kill, tw_fst, tw_kill]
            final.loc[i] = l
        except:
            pass

    final = pd.concat([final, data], axis = 1)
    return final

data = team_sep("final_data.csv")
team1 = final_data(data[0])
team2 = final_data(data[1])
team2.rename(columns={'teamId.1': 'teamId', 'win.1': 'win'}, inplace= True)
print(team1) 
print(team2)

fin = pd.concat([team1, team2], axis = 0)
print(fin)
fin.to_csv('lol_data.csv', index= False)
