# -*- coding: utf-8 -*-
# Importing Reddit library and Error handlers
import praw
from praw.exceptions import APIException
import prawcore

# Importing config file with information
import config

# Importing pandas for data manipulation
import pandas as pd

# Importing requests library for HTTP requests
import requests

# Importing datetime library for debugging and time libraries for displaying time
from datetime import datetime
import time
from pytz import timezone

# Adding EST timezone
est_timezone = timezone('US/Eastern')

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
                
                # Defining the url to get data from and creating a DataFrame and then extracting price and company name
                try:
                    av_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}".format(symbol, config.av_apikey)
                    data = pd.DataFrame(requests.get(av_url).json()['Time Series (Daily)']).T
                    price = data['4. close'][0]
                except:
                    print("Too many API Calls! Sleeping for a minute")
                    time.sleep(60)
                    pass
                
                company_name = nasdaq.loc[nasdaq['Symbol'] == symbol, 'Company Name'].iloc[0]
                
                bc_url = "https://marketdata.websol.barchart.com/getQuote.csv?apikey={}&symbols={}&fields=fiftyTwoWkHigh%2CfiftyTwoWkHighDate%2CfiftyTwoWkLow%2CfiftyTwoWkLowDate".format(config.bc_apikey, symbol)
                bc_df = pd.read_csv(bc_url)
                
                fiftyTwoWkLow = bc_df["fiftyTwoWkLow"].iloc[0]
                fiftyTwoWkHigh = bc_df["fiftyTwoWkHigh"].iloc[0]
               
                # Appending comment.id to the txt file
                comments_replied_to.append(comment.id)
                
                # Writing the comment.id to the txt file
                with open ("replied_comments.txt", "a") as f:
                    f.write(comment.id + "\n")
                    
                est_time = datetime.now(est_timezone)
                
                # Defining the variables to show in our comment reply
                stock_info = "The last price for {} (Nasdaq: {}) was **${:.2f}**".format(company_name, symbol, float(price))
                high_low_info = "\n\n The 52 week high is **${}** and 52 week low is **${}**".format(fiftyTwoWkHigh, fiftyTwoWkLow)
                time_info = " (as of {})".format(est_time.strftime("%I:%M %p EST on %b %d, %Y"))
                bot_info = "\n\n ^^I ^^am ^^a ^^new ^^bot ^^and ^^I'm ^^still ^^improving, ^^you ^^can ^^provide ^^feedback ^^by ^^DMing ^^me ^^your ^^suggestions!"
                
                # Replying to the comment on reddit
                comment.reply(stock_info + time_info + high_low_info + bot_info)
                
                # Print statements for debugging
                print("Replied to comment {}".format(comment.id))
                print(stock_info + time_info + high_low_info)
                
                # Sleeping for 15 seconds to limit 5 API Calls per minute
                print("Sleeping for 15 seconds...")
                time.sleep(15)
                
# Creating comment saving function
def get_replied_comments():
    # Creating a list if txt file is unavailable else reading the txt file
    if not os.path.isfile("replied_comments.txt"):
        replied_comments = []
    else:
        with open("replied_comments.txt", "r") as f:
            replied_comments = f.read()
            replied_comments = replied_comments.split("\n")
    
    return replied_comments

# Assigning a variable to the get_replied_comments() function
comments_replied_to = get_replied_comments()

# While loop to continuosly run the run_bot function
while True:
    try:
        print("\n", datetime.now())
        run_bot(bot_login(), comments_replied_to)
    except APIException:
        print("PRAW API Exception was raised! Sleeping for 10 minutes")
        time.sleep(600)
    except prawcore.exceptions.Forbidden:
        print("PRAW 403 HTTP RESPONSE occured! Sleeping for 10 minutes")
        time.sleep(600)
