# -*- coding: utf-8 -*-
# Importing Reddit library
import praw

# Importing config file with information
import config

# Importing pandas for data manipulation
import pandas as pd

# Import requests library for HTTP requests
import requests

# Importing datetime library for debugging
from datetime import datetime

# Importing OS library to read/write files
import os

# Creating Pandas DataFrame
nasdaq = pd.read_csv('nasdaq-listed-symbols.csv')

# Assigning a variable to the Symbol column in the DataFrame
nasdaq_list = nasdaq.Symbol.values

# Creating login function for PRAW
def bot_login():
    bot_login_info = praw.Reddit(username = config.username,
                password = config.password,
                client_id = config.client_id,
                client_secret = config.client_secret,
                user_agent = config.user_agent)
    
    print("Successfully logged in the bot as {}".format(bot_login_info.user.me()))
    
    return bot_login_info


# Creating function to run bot and reply to comments
def run_bot(bot_login_info, comments_replied_to):
    
    print("Running the bot and getting the latest comments...")
    
    for comment in bot_login_info.subreddit('all').comments(limit = None):
        
        for symbol in nasdaq_list:
            stock_comment = '${}'.format(symbol)
            if stock_comment in comment.body and comment.id not in comments_replied_to and comment.author != config.username :
                
                url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}".format(symbol, config.av_apikey)
                data = pd.DataFrame(requests.get(url).json()['Time Series (Daily)']).T
                price = data['4. close'][0]
                
                print("The last closing price for {} was {}".format(stock_comment, price))
                print("Replied to comment {}".format(comment.id))
                comments_replied_to.append(comment.id)
                
                with open ("replied_comments.txt", "a") as f:
                    f.write(comment.id + "\n")
                
                comment.reply("The last closing price for {} was ${}".format(symbol, price))
                
# Creating comment saving function
def get_replied_comments():
    if not os.path.isfile("replied_comments.txt"):
        replied_comments = []
    else:
        with open("replied_comments.txt", "r") as f:
            replied_comments = f.read()
            replied_comments = replied_comments.split("\n")
    
    return replied_comments

comments_replied_to = get_replied_comments()


while True:
    print("\n", datetime.now())
    run_bot(bot_login(), comments_replied_to)
   