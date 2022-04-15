# HLTV-bot
A simple twitterbot for tweeting the HLTV-rank of one or more teams.
https://twitter.com/HLTV_NOR

---

To use with Docker, just mount a file of your own called teams.txt to root directory.

you can also mount a cron file of your own to /etc/crontab to make it trigger at another time.
note: HLTV updates ranks approx. 19.00CET. But often a bit later. 19.30ish works fine.
