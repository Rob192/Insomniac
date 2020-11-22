from src.counters_parser import parse, LanguageChangedException
from src.navigation import navigate, Tabs
from src.utils import *
from insomniac import _run_safely

import colorama
import uiautomator

from src.action_get_my_profile_info import get_my_profile_info
from src.session_state import SessionState, SessionStateEncoder
from src.storage import StorageFollowers
from src.device_facade import create_device, DeviceFacade

import argparse
import random
import sys
import traceback
from enum import Enum, unique
from functools import partial
from http.client import HTTPException
from socket import timeout

import colorama

from src.action_get_my_profile_info import get_my_profile_info
from src.action_handle_blogger import handle_blogger
from src.action_unfollow import unfollow, UnfollowRestriction
from src.counters_parser import LanguageChangedException
from src.device_facade import create_device, DeviceFacade
from src.filter import Filter
from src.navigation import navigate, Tabs
from src.persistent_list import PersistentList
from src.report import print_full_report, print_short_report
from src.session_state import SessionState, SessionStateEncoder
from src.storage import Storage
from src.utils import *

device_id = None


def main(device):
    random.seed()
    colorama.init()

    # create device from insomniac main()
    global device_id
    device_id = device
    if not check_adb_connection(is_device_id_provided=(device_id is not None)):
        return

    print("Instagram version: " + get_instagram_version())

    device = create_device(False, device_id)
    if device is None:
        return

    session_state = SessionState()

    print_timeless(COLOR_WARNING + "\n-------- START: " + str(session_state.startTime) + " --------" + COLOR_ENDC)
    open_instagram(device_id)
    session_state.my_username, \
    session_state.my_followers_count, \
    session_state.my_following_count = get_my_profile_info(device)
    storage_followers = StorageFollowers(session_state.my_username)

    get_my_followers(device, storage_followers)


def get_my_followers(device, storage_followers):
    navigate(device, Tabs.PROFILE)

    username = None
    follower_info = device.find(resourceId="com.instagram.android:id/row_profile_header_followers_container")

    follower_info.click()
    _iterate_over_followers(device, storage_followers)

    return True


def _iterate_over_followers(device, storage_followers):
    # Wait until list is rendered
    device.find(resourceId='com.instagram.android:id/follow_list_container',
                className='android.widget.LinearLayout').wait()

    def scrolled_to_top():
        row_search = device.find(resourceId='com.instagram.android:id/row_search_edit_text',
                                 className='android.widget.EditText')
        return row_search.exists()

    prev_screen_iterated_followers = []
    while True:
        print("Iterate over visible followers")
        random_sleep()
        screen_iterated_followers = []
        screen_skipped_followers_count = 0

        try:
            for item in device.find(resourceId='com.instagram.android:id/follow_list_container',
                                    className='android.widget.LinearLayout'):
                user_info_view = item.child(index=1)
                user_name_view = user_info_view.child(index=0).child()
                if not user_name_view.exists(quick=True):
                    print(COLOR_OKGREEN + "Next item not found: probably reached end of the screen." + COLOR_ENDC)
                    break

                username = user_name_view.get_text()
                screen_iterated_followers.append(username)
                cnt_already_following = store_follower(username, storage_followers)
                if cnt_already_following > 10:
                    print('These followers were already saved, exit')
                    return
                # TODO: change this code to track the people that are not following anymore

        except IndexError:
            print(COLOR_FAIL + "Cannot get next item: probably reached end of the screen." + COLOR_ENDC)

        if len(screen_iterated_followers) > 0:
            load_more_button = device.find(resourceId='com.instagram.android:id/row_load_more_button')
            load_more_button_exists = load_more_button.exists()

            if not load_more_button_exists and screen_iterated_followers == prev_screen_iterated_followers:
                print(COLOR_OKGREEN + "Iterated exactly the same followers twice, finish." + COLOR_ENDC)
                return

            need_swipe = screen_skipped_followers_count == len(screen_iterated_followers)
            list_view = device.find(resourceId='android:id/list',
                                    className='android.widget.ListView')

            pressed_retry = False
            if load_more_button_exists:
                retry_button = load_more_button.child(className='android.widget.ImageView')
                if retry_button.exists():
                    retry_button.click()
                    random_sleep()
                    pressed_retry = True

            if need_swipe and not pressed_retry:
                print(COLOR_OKGREEN + "All followers skipped, let's do a swipe" + COLOR_ENDC)
                list_view.swipe(DeviceFacade.Direction.BOTTOM)
                need_swipe = False
            else:
                print(COLOR_OKGREEN + "Need to scroll now" + COLOR_ENDC)
                list_view.scroll(DeviceFacade.Direction.BOTTOM)

            prev_screen_iterated_followers.clear()
            prev_screen_iterated_followers += screen_iterated_followers
        else:
            print(COLOR_OKGREEN + "No followers were iterated, finish." + COLOR_ENDC)
            return


def store_follower(username, storage):
    print(username)
    if storage.was_already_following(username):
        print("@" + username + ": already listed in followers. Skip.")
    else:
        print("@" + username + ": save")
        storage.add_follower(username)
    return storage.count_already_following


if __name__ == "__main__":
    main("818HGBWJ224P3")
