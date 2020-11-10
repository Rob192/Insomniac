import sys
from insomniac import main
import json
from datetime import date

class AutoInsomniac:
    def __init__(self, account):
        self.id = 0
        self.account = account
        self.device, self.list_influencers = self.read_param(account)
        self.len_max = len(self.list_influencers)
        self.current_influencer = self.list_influencers[self.id]

    def read_param(self, account):
        """
        Read the json file containing parameters for running insomniac. The json file must have
        {"device": the name of the device per adb
        "list_users": the list of the influencers the bot will visit (one each day)
        }
        :param account: the name of the account in string. There must be a matching json file
        :return:
        """
        with open(f'./automate/automate_param/{account}.json', 'r') as f:
            param = json.load(f)
        return param['device'], param['list_users']

    def use_insomniac(self):
        sys.argv = [
            "insomniac.py",
            "--device",
            f"{self.device}",
            "--interact",
            f"{self.current_influencer}",
            "--likes-count",
            "6",
            "--total-likes-limit",
            "124"
        ]
        main()

    def increase_id (self):
        self.id += 1
        self.id %= self.len_max
        return self.id

    def select_and_save_new_influencer(self):
        self.increase_id()
        self.current_influencer = self.list_influencers[self.id]
        print(f'The influencer for the day is :{self.current_influencer}')
        self.save_influencer()

    def save_influencer(self):
        with open(f'./stats/{self.account}.csv', 'a') as f:
            f.write('\n' + self.current_influencer + ',' + date.today().strftime('%d-%m-%Y'))
        print(f'The influencer used today is saved in: ./stats/{self.account}.csv')

if __name__ == "__main__":
    ai = AutoInsomniac('flush_royale')