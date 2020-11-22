import sys
import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from automate.analysis_get_interaction_ratio import get_stats
from src.action_get_my_followers import main as get_my_followers
from insomniac import main

class AutoInsomniac:
    def __init__(self, account):
        self.id = 0
        self.account = account
        self.device, self.stats = self.read_param()
        self.list_influencers = self.select_influencers()
        self.len_max = len(self.list_influencers)
        self.current_influencer = self.list_influencers[self.id]

    def read_param(self):
        """
        Read the json file containing parameters for running insomniac. The json file must have
        {"device": the name of the device per adb
        "list_users": the list of the influencers the bot will visit (one each day)
        }
        :param account: the name of the account in string. There must be a matching json file
        :return:
        """
        with open(f'./automate/automate_param/{self.account}.json', 'r') as f:
            param = json.load(f)
        stats = pd.read_csv(Path(f'{self.account}/stats.csv'), index_col='influencer')
        #TODO create case when this file does not exists
        return param['device'], stats

    def select_influencers(self):
        df = self.stats.copy()
        df_not_done = df[df['total_interactions_influencer'] < 200]
        df_best = df.sort_values(by='ratio',ascending=False).head(10)
        return list(set(df_best.index.to_list() + df_not_done.index.to_list()))

    def use_insomniac(self):
        self.select_new_influencer()
        sys.argv = [
            "insomniac.py",
            "--device",
            f"{self.device}",
            "--interact",
            f"{self.current_influencer}",
            "--likes-count",
            "6",
            "--total-likes-limit",
            "1000"
        ]
        main()

    def increase_id (self):
        self.id += 1
        self.id %= self.len_max
        return self.id

    def select_new_influencer(self):
        self.increase_id()
        self.current_influencer = self.list_influencers[self.id]
        print(f'The influencer selected is :{self.current_influencer}')

    def save_influencer(self):
        with open(f'./stats/{self.account}.csv', 'a') as f:
            f.write('\n' + self.current_influencer + ',' + datetime.today().strftime(
                '%d-%m-%Y') + ',' + datetime.today().strftime('%H:%M'))
        print(f'The influencer used today is saved in: ./stats/{self.account}.csv')

    def save_stats(self):
        df = pd.read_csv(Path(f'{self.account}/stats.csv'), index_col='influencer')
        df.update(self.stats)
        df.to_csv(Path(f'{self.account}/stats.csv'))

    def get_follow_stats(self):
        get_my_followers(self.device)
        self.stats = get_stats(self.account)
        self.save_stats()
        self.stats = pd.read_csv(Path(f'{self.account}/stats.csv'), index_col='influencer') #reload updated stats
        self.list_influencers = self.select_influencers() #perform new selection of influencers

    def update_influencers_list(self):
        #TODO read followings and add them to the influencers list
        return None

if __name__ == "__main__":
    ai = AutoInsomniac('charlie_mamas')
    ai.get_follow_stats()
    print('hello')