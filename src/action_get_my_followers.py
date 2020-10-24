from src.counters_parser import parse, LanguageChangedException
from src.navigation import navigate, Tabs
from src.utils import *


def get_my_followers(device, storage_followers):
    navigate(device, Tabs.PROFILE)

    username = None
    follower_info = device(resourceId="com.instagram.android:id/row_profile_header_followers_container")

    follower_info.click.wait()
    _iterate_over_followers(device, storage_followers)

    """
    if title_view.exists:
        username = title_view.text
    else:
        print(COLOR_FAIL + "Failed to get username" + COLOR_ENDC)

    try:
        followers = _get_followers_count(device)
    except LanguageChangedException:
        # Try again on the correct language
        navigate(device, Tabs.PROFILE)
        followers = _get_followers_count(device)

    report_string = ""
    if username:
        report_string += "Hello, @" + username + "!"
    if followers:
        report_string += " You have " + str(followers) + " followers so far."

    if not report_string == "":
        print(report_string)
    """
    return True #username, followers

def _iterate_over_followers(device, storage_followers):
    followers_per_screen = None

    def scrolled_to_top():
        row_search = device(resourceId='com.instagram.android:id/row_search_edit_text',
                            className='android.widget.EditText')
        return row_search.exists

    while True:
        print("Iterate over visible followers")
        screen_iterated_followers = 0

        for item in device(resourceId='com.instagram.android:id/follow_list_container',
                           className='android.widget.LinearLayout'):
            try:
                user_info_view = item.child(index=1)
                user_name_view = user_info_view.child(index=0).child()
                username = user_name_view.text
            except uiautomator.JsonRPCError:
                print(COLOR_OKGREEN + "Next item not found: probably reached end of the screen." + COLOR_ENDC)
                if followers_per_screen is None:
                    followers_per_screen = screen_iterated_followers
                break

            screen_iterated_followers += 1
            print(screen_iterated_followers)

            store_follower(username, storage_followers)
            # TODO: change this code to track the people that are not following anymore

            if followers_per_screen and screen_iterated_followers >= followers_per_screen:
                print(COLOR_OKGREEN + str(screen_iterated_followers) +
                      " items iterated: probably reached end of the screen." + COLOR_ENDC)
                break
        """
        if is_myself and scrolled_to_top():
            print(COLOR_OKGREEN + "Scrolled to top, finish." + COLOR_ENDC)
            return"""
        if screen_iterated_followers > 0:
            print(COLOR_OKGREEN + "Need to scroll now" + COLOR_ENDC)
            list_view = device(resourceId='android:id/list',
                               className='android.widget.ListView')

            list_view.scroll.toEnd(max_swipes=1)
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

if __name__ == "__main__":
    import colorama
    import uiautomator

    from src.action_get_my_profile_info import get_my_profile_info
    from src.session_state import SessionState, SessionStateEncoder
    from src.storage import StorageFollowers

    session_state = SessionState()

    device = uiautomator.Device()
    session_state.my_username, session_state.my_followers_count = get_my_profile_info(device)
    storage_followers = StorageFollowers(session_state.my_username)

    get_my_followers(device, storage_followers)