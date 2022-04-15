import time
from datetime import datetime
import requests
from lxml import html
import tweepy
import re
from credentials import *

debug = True
print("debugging is set to: ", debug)
#get date of latest ranking
def rank_date():
    top30 = 'https://www.hltv.org/ranking/teams/'
    req30 = requests.get(top30)
    tree30 = html.fromstring(req30.content)
    date = tree30.xpath('string(//div[@class="regional-ranking-header"]/text())').replace('CS:GO World ranking on ', '')
    time.sleep(0.2)
    return date

Client = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)
#get old tweets and check if the date from HLTV has been tweeted before
def old_tweets():
    if debug == True:
        date = "debuggig"
    elif debug == False:
        date = rank_date()
    userID = Client.get_user(username="HLTV_NOR").data.id #change name to your twitter handle
    oldTweet = Client.get_users_tweets(id=userID).data
    num_tweets = len(oldTweet)
    for i in range(num_tweets):
        tweet = oldTweet[i].text
        #print(tweet)
        if date in tweet:
            return True
        else:
            return date
# get the newest link to regional rankings for Norway
def getRegionalLink():
    now = datetime.now()
    month = now.strftime("%B")
    day = now.strftime("%-d")
    monday = int(day) - now.weekday()
    link = "https://www.hltv.org/ranking/teams/2022/" + month.lower() + "/" + str(monday) + "/country/Norway"
    #check if valid link
    response = requests.get(link).status_code
    if response == 404:
        return response
    return link
#check if date have been tweeted before. If HLTV has not yet updated the ranks, we will retry once a minute for 10 minutes.

if old_tweets() == True or getRegionalLink() == 404:
    print("rank not ready")
    for i in range(10):
        if old_tweets() == True or getRegionalLink() == 404:
            print("attempt: ", i + 1)
            time.sleep(120)
        else:
            break
date = old_tweets()

def message():
    # find regional teams first
    regionalList = []
    regional = getRegionalLink()
    regionalReq = requests.get(regional)
    regionalTree = html.fromstring(regionalReq.content)
    numTeams = len(regionalTree.xpath('//div[@class="ranked-team standard-box"]/div/div[2]/div/a[1]'))
    for i in range(numTeams):
        link = regionalTree.xpath('//div[@class="ranked-team standard-box"]/div/div[2]/div/a[1]')[i].attrib["href"]
        regionalList.append("https://www.hltv.org" + link)
    #Other teams
    if debug == True:
        teams = open("teams.txt")
    elif debug == False:
        teams = open("/teams.txt")
    url = teams.readlines()
    regionalRank = []
    teamrank = []
    for regionalURL in regionalList:
        req = requests.get(regionalURL)
        tree = html.fromstring(req.content)
        teamname = tree.xpath('string(//h1[@class="profile-team-name text-ellipsis"]/text())')
        rank = tree.xpath('string(//html/body/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a/text())')
        if len(teamname) == 0:
            return "error"
        else:
            if rank != "":
                regionalRank.append(rank + " " + teamname)
            else:
                print(teamname + " has no rank")
        time.sleep(0.5)
    for url in url:
        req = requests.get(url)
        tree = html.fromstring(req.content)
        teamname = tree.xpath('string(//h1[@class="profile-team-name text-ellipsis"]/text())')
        rank = tree.xpath('string(//html/body/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a/text())')
        if len(teamname) == 0:
            return "error"
        else:
            if rank != "":
                teamrank.append(rank + " " + teamname)
            else:
                print(teamname + " has no rank")
        time.sleep(0.5)
    regionalRankSorted = sorted(regionalRank, key=lambda rank: int(re.split(r'#| ', rank)[1]))
    teamrank_sorted = sorted(teamrank, key=lambda rank: int(re.split(r'#| ', rank)[1]))
    #message = rank_date() + '\n' + "Norske lag:" + '\n' + '\n'.join(regionalRankSorted) + '\n \n' + "norske organisasjoner:" + '\n' + '\n'.join(teamrank_sorted)
    message = []
    index = 0
    regional_msg1 = date + '\n\n' + 'Norske lag\n'
    for i in range(len(regionalRankSorted)):
        if len(regional_msg1) + len(regionalRankSorted[i]) > 280:
            index = i
            break
        else:
            regional_msg1 = regional_msg1 + ''.join(regionalRankSorted[i]) + '\n'
    message.append(regional_msg1)
    if index > 0:
        regional_msg2 = ''
        for i in range(index, len(regionalRankSorted)):
            regional_msg2 = regional_msg2 + ''.join(regionalRankSorted[i]) + '\n'
        message.append(regional_msg2)
    orgs = 'Norske organisasjoner\n'
    for i in range(len(teamrank_sorted)):
        orgs = orgs + ''.join(teamrank_sorted[i]) + '\n'
    message.append(orgs)
    return message

#sends the tweet, but will check for errors when we checked for team ranks.
def send_tweet():
    tweet = message()
    if "error" in tweet:
        print("error in fetching data")
        for i in range(10):
            time.sleep(10)
            print("retrying attempt ", i + 1)
            tweet_checked = message()
            if "error" not in tweet_checked:
                print(tweet_checked)
                #Client.create_tweet(text=tweet_checked)
                print("tweet sent after ", i + 1, " attempts")
                break

    else:
        for i in range(len(tweet)):
            if i == 0:
                if debug == True:
                    print(tweet[i])
                elif debug == False:
                    tweet_id = Client.create_tweet(text=tweet[i]).data["id"]
            else:
                if debug == True:
                    print(tweet[i])
                elif debug == False:
                    tweet_id = Client.create_tweet(in_reply_to_tweet_id=tweet_id, text=tweet[i]).data["id"]
if date == True:
    print("Aborted")
else:
    send_tweet()
