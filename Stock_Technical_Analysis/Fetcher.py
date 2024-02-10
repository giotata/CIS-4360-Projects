'''
@project       : Temple University CIS 4360 Computational Methods in Finance
@Instructor    : Dr. Alex Pang

@Student Name  : Giorgio Tatarelli

@Date          : 9/1/2023

Download daily stock price from Yahoo

'''


import os
import pandas as pd
import numpy as np
import sqlite3

# pip install pandas-datareader
import pandas_datareader as pdr

import yfinance as yf

import option

# https://www.geeksforgeeks.org/python-stock-data-visualisation/

class Fetcher(object):

    def __init__(self, opt, db_connection):
        # opt is an option instance
        self.opt = opt
        self.db_connection = db_connection

    def get_daily_from_yahoo(self, ticker, start_date, end_date):
        # gets df of stock info between two dates
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        return(df)

    def download_data_to_csv(self, list_of_tickers):
        # downloads all df for tickers from yahoo api and makes csv for each
        
        for ticker in list_of_tickers:
            stock = self.get_daily_from_yahoo(ticker, self.opt.start_date, self.opt.end_date) 
            daily = os.path.join(self.opt.output_dir, f"{ticker}_daily.csv") #specify name of csv file to store daily price data
            stock['Ticker'] = ticker #add column 'Ticker' and fills all rows with the ticker
            stock.to_csv(daily)
        
    def csv_to_table(self, csv_file_name, fields_map, db_table):
        # insert data from a csv file to a table

        df = pd.read_csv(csv_file_name)
        if df.shape[0] <= 0:
            return
        # change the column header
        df.columns = [fields_map[x] for x in df.columns]

        # move ticker columns
        new_df = df[['Ticker']]
        for c in df.columns[:-1]:
            new_df[c] = df[c]

        ticker = os.path.basename(csv_file_name).replace('.csv','').replace("_daily", "")
        print(ticker)
        cursor = self.db_connection.cursor()

        #turns dataframe into list of tuples
        new_df = list(new_df.itertuples(index=False, name=None))

        #insert data from dataframe into sql database
        sql = f"INSERT INTO {db_table} (Ticker, AsOfDate, Open, High, Low, Close, Volume, Dividend, StockSplit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.executemany(sql, new_df)

        self.db_connection.commit()
        
    def save_daily_data_to_sqlite(self, daily_file_dir, list_of_tickers):
        # read all daily.csv files from a dir and load them into sqlite table
        db_table = 'EquityDailyPrice'

        cursor = self.db_connection.cursor()
        sql = f"DELETE FROM {db_table}"
        cursor.execute(sql)

        fields_map = {'Date': 'AsOfDate', 'Dividends': 'Dividend', 'Stock Splits': 'StockSplits'}
        for f in ['Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']:
            fields_map[f] = f

        for ticker in list_of_tickers:
            file_name = os.path.join(daily_file_dir, f"{ticker}_daily.csv")
            print(file_name)
            self.csv_to_table(file_name, fields_map, db_table)

        self.db_connection.close()

def run():
    #
    parser = option.get_default_parser()
    parser.add_argument('--data_dir', dest = 'data_dir', default='./data', help='data dir')    
    
    args = parser.parse_args()
    opt = option.Option(args = args)

    opt.output_dir = os.path.join(opt.data_dir, "daily")
    opt.sqlite_db = os.path.join(opt.data_dir, "sqlitedb/Equity.db")
    
    if opt.tickers is not None:
        list_of_tickers = opt.tickers.split(',')
    else:
        fname = os.path.join(opt.data_dir, "S&P500.txt")
        list_of_tickers = list(pd.read_csv(fname, header=None).iloc[:, 0])
        print(f"Read tickers from {fname}")
        

    print(list_of_tickers)
    print(opt.start_date, opt.end_date)

    db_file = opt.sqlite_db
    db_connection = sqlite3.connect(db_file)
    
    fetcher = Fetcher(opt, db_connection)
    print(f"Download data to {opt.data_dir} directory")

    # Call the fetcher download and save_daily methods
    if 1:
        print(f"Download data to {opt.data_dir} directory")
        fetcher.download_data_to_csv(list_of_tickers)

    if 1:
        # read the csv file back and save the data into sqlite database
        fetcher.save_daily_data_to_sqlite(opt.output_dir, list_of_tickers)
    
if __name__ == "__main__":
    run()
