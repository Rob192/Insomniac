import json
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path
import os
from datetime import datetime

def transform_date (string_date):
    datestr = string_date.split('.')[0] #remove the last bit of the data (ms) we don't need that
    return datetime.strptime(datestr,'%Y-%m-%d %H:%M:%S') #convert the data into datetime object

def extract_sessions (sessions):
    sessions_dict = {}
    with open(sessions, 'r') as f:
        file = json.load(f)
    for session in file:
        start_time = session['start_time']
        sessions_dict[start_time] = session['args']['interact'][0]
    return sessions_dict

def get_list_session_dates(sessions_dict):
    return sorted(list(sessions_dict.keys()))

def get_influencer (date, sessions_dict):
    session_dates = get_list_session_dates(sessions_dict)
    #case when the date checked is below the date registered in sessions_dict
    if transform_date(date) < transform_date(session_dates[0]):
        return None
    for i, session_date in enumerate(session_dates):
        if i == (len(session_dates) - 1):
            if transform_date(date) > (transform_date(session_date) + timedelta(days=1)):
                #if the date check is above the last date by one day, there is no influencer
                return None
            else:
                return sessions_dict[session_date]
        elif transform_date(date) < transform_date(session_date):
            return sessions_dict[last_date]
        last_date = session_date


def get_stats(user):
    interacted_users_path = Path(f'{user}/interacted_users.json')
    followers_path = Path(f'{user}/followers.json')
    sessions = Path(f'{user}/sessions.json')

    df_interacted = pd.read_json(interacted_users_path, orient='index').reset_index(level=0, inplace=False)
    df_followers = pd.read_json(followers_path, orient='index').reset_index(level=0, inplace=False)
    sessions_dict = extract_sessions(sessions)

    df = pd.merge(df_interacted, df_followers, how='left')
    df.fillna(0, inplace= True)
    df['is_following'] = df['date_follower_stored'].apply(lambda x: 0 if x == 0 else 1)

    df['influencer'] = df['last_interaction'].apply(lambda x: get_influencer(x, sessions_dict))
    df.last_interaction = df.last_interaction.apply(lambda x: transform_date(x))

    tot = df.groupby('influencer')['is_following'].count()
    sum = df.groupby('influencer')['is_following'].sum()

    data = {'ratio': sum/tot, 'nb_follow_from_influencer': sum, 'total_interactions_influencer': tot}
    res = pd.DataFrame(data)
    print(sum / tot * 100)
    print('the total number of followers gained with the bot is :'+ str(sum.sum()))

    return res

if __name__ == '__main__':
    user = 'flushroyale.le.jeu'
    res = get_stats(user)
    print('done')
