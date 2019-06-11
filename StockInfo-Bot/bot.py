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
from datetime import datetime, timedelta
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
                valid_av_data = False
                
                while not valid_av_data:
                    try:
                        av_url_daily = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}".format(symbol, config.av_apikey)
                        av_url_daily_data = pd.DataFrame(requests.get(av_url_daily).json()['Time Series (Daily)']).T
                        price = av_url_daily_data['4. close'][0]
                        
                        #time.sleep(5)
                        
                        av_url_weekly = "https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol={}&apikey={}".format(symbol, config.av_apikey)
                        av_url_weekly_data = pd.DataFrame(requests.get(av_url_weekly).json()['Weekly Time Series']).T
                        weekly_high = av_url_weekly_data['2. high'][1]
                        weekly_low = av_url_weekly_data['3. low'][1]
                        
                        #time.sleep(5)
                        
                        av_url_monthly = "https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={}&apikey={}".format(symbol, config.av_apikey)
                        av_url_monthly_data = pd.DataFrame(requests.get(av_url_monthly).json()['Monthly Time Series']).T
                        monthly_high = av_url_monthly_data['2. high'][1]
                        monthly_low = av_url_monthly_data['3. low'][1]
                        
                        valid_av_data = True
                        
                        if valid_av_data:
                            continue
                    except:
                        print("Too many API Calls! Sleeping for a minute")
                        time.sleep(60)
                
                company_name = nasdaq.loc[nasdaq['Symbol'] == symbol, 'Company Name'].iloc[0]
                
                valid_bc_data = False
                
                while not valid_bc_data:
                    try:
                        bc_url = "https://marketdata.websol.barchart.com/getQuote.csv?apikey={}&symbols={}&fields=fiftyTwoWkHigh%2CfiftyTwoWkHighDate%2CfiftyTwoWkLow%2CfiftyTwoWkLowDate".format(config.bc_apikey, symbol)
                        bc_df = pd.read_csv(bc_url)
                        fiftyTwoWkLow = bc_df["fiftyTwoWkLow"].iloc[0]
                        fiftyTwoWkHigh = bc_df["fiftyTwoWkHigh"].iloc[0]
                        valid_bc_data = True
                        
                        if valid_bc_data:
                            continue
                    except:
                        print("Too many API Calls! Sleeping for a minute")
                        time.sleep(60)
               
                # Appending comment.id to the txt file
                comments_replied_to.append(comment.id)
                
                # Writing the comment.id to the txt file
                with open ("replied_comments.txt", "a") as f:
                    f.write(comment.id + "\n")
                    
                est_time = datetime.now(est_timezone)
                
                last_month_name = (pd.Period(datetime.now(), 'M') - 1).strftime('%B %Y')
                
                now = datetime.now()
                closest_friday = now + timedelta(days = (4 - now.weekday()))
                last_friday = closest_friday if closest_friday < now else closest_friday - timedelta(days = 7)
                
                # Defining the variables to show in our comment reply
                stock_info = "The last price for {} (Nasdaq: {}) was **${:.2f}**".format(company_name, symbol, float(price))
                high_low_info = "\n\n The 52 week high is **${}** and 52 week low is **${}**".format(fiftyTwoWkHigh, fiftyTwoWkLow)
                price_action_info = "\n\n Price action (weekly and monthly):"
                weekly_info = "\n\n **Weekly:** {} made a weekly high of **${:.2f}** and a low of **${:.2f}** (for the week ending on {})".format(symbol, float(weekly_high), float(weekly_low), last_friday.strftime("%b %d, %Y"))
                monthly_info = "\n\n **Monthly:** {} made a monthly high of **${:.2f}** and a low of **${:.2f}** (for the month of {})".format(symbol, float(monthly_high), float(monthly_low), last_month_name)
                time_info = " (as of {})".format(est_time.strftime("%I:%M %p EST on %b %d, %Y"))
                bot_info = "\n\n ^^I ^^am ^^a ^^new ^^bot ^^and ^^I'm ^^still ^^improving, ^^you ^^can ^^provide ^^feedback ^^by ^^DMing ^^me ^^your ^^suggestions!"
                
                # Replying to the comment on reddit
                comment.reply(stock_info + time_info + high_low_info + price_action_info + weekly_info + monthly_info + bot_info)
                
                # Print statements for debugging
                print("Replied to comment {}".format(comment.id))
                print(stock_info + time_info + high_low_info)
                
                # Sleeping for 60 seconds to limit 5 API Calls per minute
                print("Sleeping for 60 seconds...")
                time.sleep(60)
                
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
    except prawcore.ResponseException:
        print("PRAW 503 HTTP REsponse! SLeeping for 10 minutes")
        time.sleep(60)
