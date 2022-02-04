import time
import requests
from lxml import html
import tweepy
from credentials import *

#get date of latest ranking
def rank_date():
    top30 = 'https://www.hltv.org/ranking/teams/'
    req30 = requests.get(top30)
    tree30 = html.fromstring(req30.content)
    date = tree30.xpath('string(//div[@class="regional-ranking-header"]/text())').replace('CS:GO World ranking on ', '')
    return date

Client = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)
#get old tweets and check if the date from HLTV has been tweeted before
def old_tweets():
    date = rank_date()
    userID = Client.get_user(username="HLTV_NOR").data.id
    oldTweet = Client.get_users_tweets(id=userID).data
    num_tweets = len(oldTweet)
    for i in range(num_tweets):
        tweet = oldTweet[i].text
        if date in tweet:
            return True
        else:
            return date
#check if date have been tweeted before. If HLTV has not yet updated the ranks, we will retry once a minute for 10 minutes.
date = old_tweets()
if date == True:
    print("old tweet found, retrying")
    for i in range(10):
        status = old_tweets()
        if status:
            print("attempt: ", i + 1)
            time.sleep(120)
        else:
            date = status
            break
    
def message():
    teams = open("/teams.txt")
    url = teams.readlines()

    teamrank = []
    for url in url:
        req = requests.get(url)
        tree = html.fromstring(req.content)
        teamname = tree.xpath('string(//h1[@class="profile-team-name text-ellipsis"]/text())')
        rank = tree.xpath('string(//html/body/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a/text())')
        if len(teamname) == 0:
            return "error"
        else:
            if rank != "":
                teamrank.append(teamname + " er rangert som " + rank)
            else:
                print(teamname + " has no rank")
    message = rank_date() + '\n' + '\n'.join(teamrank) + "\n"
    return message

tweet = message()
#sends the tweet, but will check for errors when we checked for team ranks.
def send_tweet():
    if "error" in tweet:
        print("error in fetching data")
        for i in range(10):
            time.sleep(60)
            print("retrying attempt ", i + 1)
            tweet_checked = message()
            if "error" not in tweet_checked:
                print(tweet_checked)
                Client.create_tweet(text=tweet_checked)
                print("tweet sent after ", i + 1, " attempts")
                break

    else:
        print(tweet)
        Client.create_tweet(text=tweet)
        print("tweet sent without errors")
send_tweet()