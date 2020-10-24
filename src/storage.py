import json
from datetime import timedelta
from enum import Enum, unique
from pathlib import Path

from src.utils import *

FILENAME_INTERACTED_USERS = "interacted_users.json"
FILENAME_FOLLOWERS = "followers.json"
USER_LAST_INTERACTION = "last_interaction"
USER_FOLLOWING_STATUS = "following_status"
FOLLOWING_DATE = "date_follower_stored"

FILENAME_WHITELIST = "whitelist.txt"


class Storage:
    interacted_users_path = None
    interacted_users = {}
    whitelist = []

    def __init__(self, my_username):
        if my_username is None:
            print(COLOR_FAIL + "No username, thus the script won't get access to interacted users and sessions data" +
                  COLOR_ENDC)
            return

        if not os.path.exists(my_username):
            os.makedirs(my_username)
        self.interacted_users_path = my_username + "/" + FILENAME_INTERACTED_USERS
        if os.path.exists(self.interacted_users_path):
            with open(self.interacted_users_path) as json_file:
                self.interacted_users = json.load(json_file)
        whitelist_path = my_username + "/" + FILENAME_WHITELIST
        if os.path.exists(whitelist_path):
            with open(whitelist_path) as file:
                self.whitelist = [line.rstrip() for line in file]

    def check_user_was_interacted(self, username):
        return not self.interacted_users.get(username) is None

    def check_user_was_interacted_recently(self, username):
        user = self.interacted_users.get(username)
        if user is None:
            return False

        last_interaction = datetime.strptime(user[USER_LAST_INTERACTION], '%Y-%m-%d %H:%M:%S.%f')
        return datetime.now() - last_interaction <= timedelta(days=3)

    def get_following_status(self, username):
        user = self.interacted_users.get(username)
        return user is None and FollowingStatus.NONE or FollowingStatus[user[USER_FOLLOWING_STATUS].upper()]

    def add_interacted_user(self, username, followed=False, unfollowed=False):
        user = self.interacted_users.get(username, {})
        user[USER_LAST_INTERACTION] = str(datetime.now())

        if followed:
            user[USER_FOLLOWING_STATUS] = FollowingStatus.FOLLOWED.name.lower()
        elif unfollowed:
            user[USER_FOLLOWING_STATUS] = FollowingStatus.UNFOLLOWED.name.lower()
        else:
            user[USER_FOLLOWING_STATUS] = FollowingStatus.NONE.name.lower()

        self.interacted_users[username] = user
        self._update_file()

    def is_user_in_whitelist(self, username):
        return username in self.whitelist

    def _update_file(self):
        if self.interacted_users_path is not None:
            with open(self.interacted_users_path, 'w') as outfile:
                json.dump(self.interacted_users, outfile, indent=4, sort_keys=False)


class StorageFollowers:
    followers_path = ""
    followers = {}

    def __init__(self, my_username):
        self.storage_folder = Path(os.getcwd()).parent / my_username
        self.followers_path = self.storage_folder / FILENAME_FOLLOWERS

        if not self.storage_folder.exists():
            os.makedirs(self.storage_folder)

        if self.followers_path.exists():
            with open(self.followers_path) as json_file:
                self.followers = json.load(json_file)

    def was_already_following(self, username):
        return not self.followers.get(username) is None

    def add_follower(self, username):
        follower_info = self.followers.get(username, {})
        follower_info[FOLLOWING_DATE] = str(datetime.now())

        self.followers[username] = follower_info
        self._update_file()

    def _update_file(self):
        with open(self.followers_path, 'w') as outfile:
            json.dump(self.followers, outfile, indent=4, sort_keys=False)


@unique
class FollowingStatus(Enum):
    NONE = 0
    FOLLOWED = 1
    UNFOLLOWED = 2


if __name__ == "__main__":
    storage = StorageFollowers('test')
    storage.add_follower('robin')
