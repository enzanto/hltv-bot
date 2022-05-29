from calendar import month
import time
import logging
from datetime import datetime
import requests
from lxml import html
import tweepy
import re
from credentials import *

debug = True
#Setup logging
if debug == True:
    logging.basicConfig(level=logging.DEBUG, filename="log.log", filemode="w",
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
else:
    logging.basicConfig(level=logging.INFO, filename="/log.log", filemode="w",
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.debug("debug is active")
print("debugging is set to: ", debug)
#get date of latest ranking
def rank_date():
    now = datetime.now()
    month = now.strftime("%B")
    day = now.strftime("%-d")
    monday = int(day) - now.weekday()
    top30 = "https://www.hltv.org/ranking/teams/2022/" + month.lower() + "/" + str(monday)
    while requests.get(top30).status_code != 200:
        time.sleep(2)
    req30 = requests.get(top30)
    tree30 = html.fromstring(req30.content)
    date = tree30.xpath('string(//div[@class="regional-ranking-header"]/text())').replace('CS:GO World ranking on ', '')
    sanitized = date.split()
    date = sanitized[0] + " " + sanitized[1] + " " + sanitized[2]
    time.sleep(0.2)
    logging.info("retrieved the latest rank date: %s", date)
    return date

Client = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)
#get old tweets and check if the date from HLTV has been tweeted before
def old_tweets():
    date = rank_date()
    userID = Client.get_user(username="HLTV_NOR").data.id #change name to your twitter handle
    oldTweet = Client.get_users_tweets(id=userID).data
    num_tweets = len(oldTweet)
    for i in range(num_tweets):
        tweet = oldTweet[i].text
        if date in tweet:
            return True
    return date
# get the newest link to regional rankings for Norway
def getRegionalLink():
    now = datetime.now()
    month = now.strftime("%B")
    day = now.strftime("%-d")
    monday = int(day) - now.weekday()
    link = "https://www.hltv.org/ranking/teams/2022/" + month.lower() + "/" + str(monday) + "/country/Norway"
    #check if valid link
    while requests.get(link).status_code != 200:
        time.sleep(5)
    logging.info("returning regional link: %s", link)
    return link


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
    url_date = str(date).split()
    url_month = url_date[0]
    url_day = re.split("([0-9]+)", url_date[1])[1]
    url_date_sanitized = url_month.lower() + "/" + url_day
    for regionalURL in regionalList:
        req = requests.get(regionalURL)
        tree = html.fromstring(req.content)
        rank = tree.xpath('string(//html/body/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a/text())')
        tries = 0
        skip = False
        while rank == "":
            time.sleep(30)
            tries = tries + 1
            logging.info("try: " + str(tries))
            if tries >= 20:
                skip = True
                break
        if skip == False:
            regional_rank_date = tree.xpath('/html/body/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a')[0].attrib["href"]
            while url_date_sanitized not in regional_rank_date:
                logging.debug("regional loop")
                req = requests.get(regionalURL)
                tree = html.fromstring(req.content)
                regional_rank_date = tree.xpath('/html/body/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a')[0].attrib["href"]
                time.sleep(5)
            teamname = tree.xpath('string(//h1[@class="profile-team-name text-ellipsis"]/text())')
            rank = tree.xpath('string(//html/body/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a/text())')
            regionalRank.append(rank + " " + teamname)
            logging.info(rank + " " + teamname + " " + regional_rank_date)
        elif skip == True:
            teamname = tree.xpath('string(//h1[@class="profile-team-name text-ellipsis"]/text())')
            logging.info("skipping " + teamname)
        time.sleep(0.5)
    for url in url:
        req = requests.get(url)
        tree = html.fromstring(req.content)
        rank = tree.xpath('string(//html/body/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a/text())')
        tries = 0
        skip = False
        while rank == "":
            time.sleep(30)
            tries = tries + 1
            logging.info("try: " + str(tries))
            if tries >= 10:
                skip = True
                break
        if skip == False:
            list_rank_date = tree.xpath('/html/body/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a')[0].attrib["href"]
            while url_date_sanitized not in list_rank_date:
                req = requests.get(regionalURL)
                tree = html.fromstring(req.content)
                list_rank_date = tree.xpath('/html/body/div[2]/div[1]/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a')[0].attrib["href"]
                time.sleep(5)
            teamname = tree.xpath('string(//h1[@class="profile-team-name text-ellipsis"]/text())')
            rank = tree.xpath('string(//html/body/div[2]/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/span/a/text())')
            teamrank.append(rank + " " + teamname)
            logging.info(rank + " " + teamname + " " + list_rank_date)
        elif skip == True:
            teamname = tree.xpath('string(//h1[@class="profile-team-name text-ellipsis"]/text())')
            logging.info("skipping " + teamname)
        time.sleep(0.5)
    regionalRankSorted = sorted(regionalRank, key=lambda rank: int(re.split(r'([0-9]+)', rank)[1]))
    teamrank_sorted = sorted(teamrank, key=lambda rank: int(re.split(r'([0-9]+)', rank)[1]))
    #message = rank_date() + '\n' + "Norske lag:" + '\n' + '\n'.join(regionalRankSorted) + '\n \n' + "norske organisasjoner:" + '\n' + '\n'.join(teamrank_sorted)
    message = []
    index = 0
    regional_msg1 = date + '\n\n' + 'Norske lag\n'
    for i in range(len(regionalRankSorted)):
        if len(regional_msg1) + len(regionalRankSorted[i]) > 270:
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
    for i in range(len(tweet)):
        if i == 0:
            if debug == True:
                logging.info(tweet[i])
            elif debug == False:
                tweet_id = Client.create_tweet(text=tweet[i]).data["id"]
                logging.info(tweet[i])
        else:
            if debug == True:
                logging.info(tweet[i])
            elif debug == False:
                tweet_id = Client.create_tweet(in_reply_to_tweet_id=tweet_id, text=tweet[i]).data["id"]
                logging.info(tweet[i])
if __name__ == '__main__':
    date = old_tweets()
    if date == True:
        if debug == True:
            logging.debug("old tweet found, but debugging is set to True")
            date = rank_date()
            send_tweet()
        elif debug != True:
            logging.error("Aborting, no new ranks found or tweet already sent")
    else:
        send_tweet()