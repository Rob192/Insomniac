import sys

import uiautomator

from src.use_comment_api import find_a_relevant_comment


def comment_picture(device):
    try:
        button_like = device(resourceId="com.instagram.android:id/row_feed_button_like",
                              className="android.widget.ImageView")
        see_comments = device(resourceId="com.instagram.android:id/row_feed_view_all_comments_text",
                              className="android.widget.TextView")
        if not see_comments.exists:
            print('No Comment on this picture')
            return False

        current_picture_comment = None
        for comment in see_comments:
            if button_like.bounds['bottom'] < comment.bounds['top']:
                current_picture_comment = comment

        if not current_picture_comment.exists:
            print('No Comment on this picture')
            return False

        current_picture_comment.click.wait()

        last_comments = get_all_comments(device)
        relevant_comment, score = find_a_relevant_comment(last_comments)
        if score > 0.80:
            comment_with_relevant_comment(device, relevant_comment)  # TODO uncomment for usage
        else:
            print('No relevant comment found in comment DataBase')
        button_back = device(resourceId="com.instagram.android:id/action_bar_button_back",
                             className="android.widget.ImageView")
        button_back.click.wait()
        return True
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return False


def get_all_comments(device):
    """Get all comments from a picture"""
    _scroll_to_top(device)
    all_comments = last_comments = previous_comment = []
    last_comments = get_comments_displayed(device)
    while last_comments != previous_comment:  # detects that there are no more comments to scroll
        previous_comment = last_comments
        all_comments += last_comments
        last_comments = get_comments_displayed(device)
    return all_comments


def get_comments_displayed(device):
    """Returns the comments currently displayed and then scroll to end"""
    # TODO : do not take the comment of the target
    list_of_comments = []
    list_view = device(resourceId="com.instagram.android:id/row_comment_container",
                       className="android.widget.LinearLayout")
    try:
        for item in list_view:
            comment = item.child(index=1).child(index=0).text # get all comments
            list_words = comment.split(' ')[1:] # remove the first part that is the user name
            if len(list_words) > 0: # remove empty comments that are associated with owner answer
                list_of_comments.append(' '.join(word for word in list_words))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        button_back = device(resourceId="com.instagram.android:id/action_bar_button_back",
                             className="android.widget.ImageView")
        button_back.click.wait()
    _scroll_a_bit(device)
    return list_of_comments


def comment_with_relevant_comment(device, relevant_comment):
    """Post a comment with the relevant comment passed as parameter"""
    text_area = device(resourceId="com.instagram.android:id/layout_comment_thread_edittext",
                       className="android.widget.EditText")
    text_area.click.wait()
    text_area.set_text(relevant_comment)

    publish_button = device(resourceId="com.instagram.android:id/layout_comment_thread_post_button",
                            className="android.widget.TextView")
    publish_button.click.wait()
    return True


def _scroll_a_bit(device):
    """Scroll the list of comment to the end"""
    list_view = device(resourceId='android:id/list',
                       className='android.widget.ListView')
    list_view.scroll.toEnd(max_swipes=1)

def _scroll_to_top(device):
    """Scroll the list of comment to the end"""
    list_view = device(resourceId='android:id/list',
                       className='android.widget.ListView')
    list_view.fling.vert.toBeginning(max_swipes=10)


if __name__ == "__main__":
    device = uiautomator.Device()
    # Get the comments of the picture
    comment_picture(device)

    print('done')
