#!/usr/bin/python3
""" reddit api"""

import json
import requests


def count_words(subreddit, word_list, after="", count=[]):
    """count all words"""

    if after == "":
        count = [0] * len(word_list)

    url = "https://www.reddit.com/r/{}/hot.json".format(subreddit)
    request = requests.get(url,
                           params={'after': after},
                           allow_redirects=False,
                           headers={'user-agent': 'bhalut'})

    if request.status_code == 200:
        data = request.json()

        for topic in (data['data']['children']):
            for word in topic['data']['title'].split():
                for i in range(len(word_list)):
                    if word_list[i].lower() == word.lower():
                        count[i] += 1

        after = data['data']['after']
        if after is None:
            save = []
            for i in range(len(word_list)):
                for j in range(i + 1, len(word_list)):
                    if word_list[i].lower() == word_list[j].lower():
                        save.append(j)
                        count[i] += count[j]

            for i in range(len(word_list)):
                for j in range(i, len(word_list)):
                    if (count[j] > count[i] or
                            (word_list[i] > word_list[j] and
                             count[j] == count[i])):
                        aux = count[i]
                        count[i] = count[j]
                        count[j] = aux
                        aux = word_list[i]
                        word_list[i] = word_list[j]
                        word_list[j] = aux

            for i in range(len(word_list)):
                if (count[i] > 0) and i not in save:
                    print("{}: {}".format(word_list[i].lower(), count[i]))
        else:
            count_words(subreddit, word_list, after, count)
'''A module containing functions for working with the Reddit API.
'''
import requests


def sort_histogram(histogram={}):
    '''Sorts and prints the given histogram.
    '''
    histogram = list(filter(lambda kv: kv[1], histogram))
    histogram_dict = {}
    for item in histogram:
        if item[0] in histogram_dict:
            histogram_dict[item[0]] += item[1]
        else:
            histogram_dict[item[0]] = item[1]
    histogram = list(histogram_dict.items())
    histogram.sort(
        key=lambda kv: kv[0],
        reverse=False
    )
    histogram.sort(
        key=lambda kv: kv[1],
        reverse=True
    )
    res_str = '\n'.join(list(map(
        lambda kv: '{}: {}'.format(kv[0], kv[1]),
        histogram
    )))
    if res_str:
        print(res_str)


def count_words(subreddit, word_list, histogram=[], n=0, after=None):
    '''Counts the number of times each word in a given wordlist
    occurs in a given subreddit.
    '''
    api_headers = {
        'Accept': 'application/json',
        'User-Agent': ' '.join([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'AppleWebKit/537.36 (KHTML, like Gecko)',
            'Chrome/97.0.4692.71',
            'Safari/537.36',
            'Edg/97.0.1072.62'
        ])
    }
    sort = 'hot'
    limit = 30
    res = requests.get(
        '{}/r/{}/.json?sort={}&limit={}&count={}&after={}'.format(
            'https://www.reddit.com',
            subreddit,
            sort,
            limit,
            n,
            after if after else ''
        ),
        headers=api_headers,
        allow_redirects=False
    )
    if not histogram:
        word_list = list(map(lambda word: word.lower(), word_list))
        histogram = list(map(lambda word: (word, 0), word_list))
    if res.status_code == 200:
        data = res.json()['data']
        posts = data['children']
        titles = list(map(lambda post: post['data']['title'], posts))
        histogram = list(map(
            lambda kv: (kv[0], kv[1] + sum(list(map(
                lambda txt: txt.lower().split().count(kv[0]),
                titles
            )))),
            histogram
        ))
        if len(posts) >= limit and data['after']:
            count_words(
                subreddit,
                word_list,
                histogram,
                n + len(posts),
                data['after']
            )
        else:
            sort_histogram(histogram)
    else:
        return
