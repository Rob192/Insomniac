import pandas as pd
from pathlib import Path
import os
from datetime import datetime

def transform_date (string_date):
    datestr = string_date.split('.')[0] #remove the last bit of the data (ms) we don't need that
    return datetime.strptime(datestr,'%Y-%m-%d %H:%M:%S') #convert the data into datetime object


if __name__ == '__main__':
    import pandas as pd
    from pathlib import Path
    import os
    from datetime import datetime

    user = 'charlie_mamas'

    interacted_users_path = Path(os.getcwd()).parent / user / 'interacted_users.json'
    followers_path = Path(os.getcwd()).parent / user / 'followers.json'

    df_interacted = pd.read_json(interacted_users_path, orient='index').reset_index(level=0, inplace=False)
    df_followers = pd.read_json(followers_path, orient='index').reset_index(level=0, inplace=False)

    df = pd.merge(df_interacted, df_followers, how='left')
    df.fillna(0, inplace= True)
    df['is_following'] = df['date_follower_stored'].apply(lambda x: 0 if x == 0 else 1)
    df.last_interaction = df.last_interaction.apply(lambda x: transform_date(x))

    tot = df.groupby(pd.Grouper(key='last_interaction', freq='d'))['is_following'].count()
    sum = df.groupby(pd.Grouper(key = 'last_interaction', freq = 'd'))['is_following'].sum()

    print(sum / tot * 100)

    #TODO : wrap this inside nice and neat functions
