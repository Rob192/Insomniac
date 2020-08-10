import requests


url = "http://51.15.229.170/" # TODO move this in a env variable

def find_a_relevant_comment(last_comments):
    max_score = 0
    best_answer = ''
    for comment in last_comments:
        payload = {'sentence': f'{comment}'}
        r = requests.get(url, params=payload)
        answer = r.json()
        if answer['score'] > max_score:
            max_score = answer['score']
            best_answer = answer['comment']
    print('The most relevant comment is:' + best_answer + " with a score of :" + str(max_score))
    return best_answer, max_score

if __name__ == '__main__':
    last_comments = ['Love this 😍', '✨😍✨', 'Omg love this! So so beautiful ✨🙌🏻😍 thank you!! 🙏🏻', 'Beautiful 😍💓', 'These are amazing!', 'How beautiful ❤️']
    # # comment = last_comments[0]
    # last_comments = ["J'adore ta photo !", "Ton bébé est trop beau", "Trop stylé"]
    print(find_a_relevant_comment(last_comments))