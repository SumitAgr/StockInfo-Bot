<p align="center">
  <a href="" rel="noopener">
 <img width=200px height=200px src="https://i.imgur.com/KHIluJM.png" alt="Bot logo"></a>
</p>

<h3 align="center">Stock Info Bot for Reddit</h3>

<div align="center">

![Language](https://img.shields.io/badge/Python-3.7-blue.svg) 
![License](https://img.shields.io/badge/license-MIT-blue.svg)
[![CodeFactor](https://www.codefactor.io/repository/github/sumitagr/stockinfo-bot/badge)](https://www.codefactor.io/repository/github/sumitagr/stockinfo-bot)

</div>

---

<p align="center"> 🤖 A reddit bot that displays the last closing price information of a stock. Simply enter: $(stock ticker) and the bot will reply to you with the name of the company, closing price, 52 week high and low prices.
    <br> 
</p>

## 📝 Table of Contents
+ [About](#about)
+ [How it works](#howitworks)
+ [Usage](#usage)
+ [Example](#example)
+ [Built Using](#built_using)
+ [Author](#author)
+ [License](#license)
+ [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>
A convenient bot that displays a snippet of a stock by showing the full name of the company, last closing price (latest) and the 52 week high and 52 week low price of the bot. 

Stock Info Bot uses the Alpha Vantage API for the closing price and Barchart API for 52 week prices. 

The bot is running on Ubuntu which is hosted on Amazon's AWS EC2.

## 💭 How it works <a name = "howitworks"></a>

The bot first connects to reddit by logging in with the login credentials and reddit's client id and client secret. After successfully authenticating the bot, it scans all of reddit's comments to search for the keyword $(stock ticker) and whenever it finds it, it triggers the bot to reply. 

The bot searches for the ticker symbol in the Pandas Dataframe (converted from a csv file) and then returns the stock ticker and the corresponding name of the company. It then uses Alpha Vantage's realtime API to get closing price information and returns the last closing price. It also uses Barchart's API (delayed by 15 minutes) to return the stock's 52 week high and low prices. After getting all the information necessary to reply to the original user, Stock Info Bot replies to the comment in under a minute.

The entire bot is written in Python 3.7

## 🖋️ Usage <a name = "usage"></a>

To use the bot, type the following in a reddit comment box:
```
> $SBUX
```
There has to be a $ in front of the stock ticker, otherwise it will not work.

The bot will then swiftly reply.

### 📷 Example: <a name = "example"></a>

<p align="center">
  <a href="" rel="noopener">
 <img src="https://i.imgur.com/imGH3qP.png" alt="Bot example for $SBUX"></a>
</p>

## ⛏️ Built Using <a name = "built_using"></a>
+ [PRAW](https://praw.readthedocs.io/en/latest/) - Reddit's Python wrapper
+ [Amazon AWS EC2](https://aws.amazon.com/ec2/) - Amazon AWS's cloud computing service
+ [Alpha Vantage API](https://www.alphavantage.co/) - Alpha Vantage's realtime API
+ [Barchart API](https://www.barchart.com/ondemand/api/getQuote) - Barchart's financial data API
+ Pandas - Library for data manipulation and analysis
+ Requests - Library for HTTP requests
+ Time / DateTime / PyTZ - Time libraries for time usage
+ OS - Library to read/write files

## ✍️ Author <a name = "author"></a>
+ Sumit Agrawal

## 📗 License <a name = "license"></a>
This project is licensed under the MIT License - see the LICENSE file for more details.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>
+ Thank you to [Datahub](https://datahub.io/core/nasdaq-listings) for providing the NASDAQ listing data in a clean, readable format.
+ A big thank you to all the developers of the python libraries used in this bot, it wouldn't be possible without them.
