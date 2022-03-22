#!interpreter [optional-arg]
# -*- coding: utf-8 -*-

"""
This script contains a seasonality plotter. The plotter takes in different time frames and plots the seasonality of a wished asset.

THERE IS NO RESPONSIBILITY FOR ACCURACY OF THE RESULTS BY THE AUTHOR!


MIT License to Korbinian Gabriel

Change-log:
    - 01.03.2022: Created.
    - 22.03.2022: Published to github
    
Issue-log:
    - 01.03.2022: 
"""


# Built-in/Generic Imports
import os
import sys
sys.path.append(".")
import argparse

# Libs
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime as dt

# Own modules
from Utilities.utils import add_value_labels


__author__ = 'Korbinian Gabriel'
__copyright__ = 'Copyright 2022, seasonality plotter'
__license__ = 'MIT'
__version__ = '1.0.0'
__status__ = 'Finished'

# ---------------------------------------------------------------------------- #

# This class creates an object for an asset to store seasonalities.
class Seasonalities(object):
    
    
    def __init__(self, symbol, interval, period = "max", daily_measure = 'wd'):
        """Initialize class for each symbol

        Args:
            symbol (str): String of the symbol. Use yahoo finance symbols
            interval (str): State the interval that you want to use. E.g. days, weeks, months...
            period (str, optional): Takes in the period, e.g. 60 days. Defaults to "max".
            daily_measure (str, optional): --. Defaults to 'wd'.
        """
        self.data = pd.DataFrame()
        self.symbol = symbol
        self.interval = interval
        self.period = period
        self.daily_measure = daily_measure
        self.seasonality_mean = pd.DataFrame()
        self.seasonality_std = pd.DataFrame()
        self.seasonality_prob = pd.DataFrame()
        
        
    def get_data(self):
        
        # Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo Intraday data cannot extend last 60 days
        
        print('Obtaining data from yahoo finance....')
        self.data = yf.download(tickers = self.symbol, interval = self.interval, period = self.period)
        self.data.index = pd.to_datetime(self.data.index)
        print(f'Data for {self.symbol} loaded.')
        
        self.data = self.data.pct_change()
        print('Returns calculated.')
        print('')
        
        
    def calculate_seasonality(self):
        
        # Monthly Seasonality - Average across the year
        if self.interval == '1mo':
            self.seasonality_mean = self.data.groupby(self.data.index.month).mean()['Adj Close']
            self.seasonality_std = self.data.groupby(self.data.index.month).std()['Adj Close']
            self.seasonality_prob = self.data['Adj Close'].groupby(self.data.index.month).apply(lambda x: x[x>0].count()/len(x))
        
        # Weekly Seasonality - Average across the year
        if self.interval == '1wk':
            self.seasonality_mean = self.data.groupby(self.data.index.week).mean()['Adj Close']
            self.seasonality_std = self.data.groupby(self.data.index.week).std()['Adj Close']
            self.seasonality_prob = self.data['Adj Close'].groupby(self.data.index.week).apply(lambda x: x[x>0].count()/len(x))
            
        if self.interval == '1d':
            if self.daily_measure == 'wd':
                self.seasonality_mean = self.data.groupby(self.data.index.weekday).mean()['Adj Close']
                self.seasonality_std = self.data.groupby(self.data.index.weekday).std()['Adj Close']
                self.seasonality_prob = self.data['Adj Close'].groupby(self.data.index.weekday).apply(lambda x: x[x>0].count()/len(x))
                
            # Daily Seasonality - Average across the week
            elif self.daily_measure == 'm':
                self.seasonality_mean = self.data.groupby([self.data.index.day, self.data.index.month]).mean()['Adj Close'].groupby(level=0).mean()
                self.seasonality_std = self.data.groupby([self.data.index.day, self.data.index.month]).std()['Adj Close'].groupby(level=0).mean()
                self.seasonality_prob = self.data['Adj Close'].groupby([self.data.index.day, self.data.index.month]).apply(lambda x: x[x>0].count()/len(x)).groupby(level=0).mean()
            
        
    def backtest(self, season):
        """Run a short backtest with the strategy. Pay attention, there is no accounting for any costs, e.g. slippage or commission, nor the sizing or timing. 
        This backtest is a wild guess on how the seasonality could perform, and not anywhere near the reality.

        Args:
            season (str): Takes in the month or the week number
        """
        print('Calculating backtest....')
        
        strategy = None
        if self.interval == '1mo':
            strategy = self.data[self.data.index.month == season]['Adj Close'].cumsum()
        if self.interval == '1wk':
            strategy = self.data[self.data.index.week == season]['Adj Close'].cumsum()
        if self.interval == '1d':
            if self.daily_measure == 'wd':
                strategy = self.data[self.data.index.weekday == season]['Adj Close'].cumsum()
            elif self.daily_measure == 'm':
                strategy = self.data[self.data.index.day == season]['Adj Close'].cumsum()
            
        fig = plt.figure(figsize = (10, 5))
        plt.plot(strategy, alpha = 0.8)
        plt.axhline(0, color = 'k')
        plt.title(f'Data since {self.data.index[0]} with {self.interval} frequency.', fontname="Times New Roman", size=12)
        plt.suptitle(f'Buying the {season} seasonality in {self.interval} frequency.')
        plt.show()
        
        print('Backtest completed.')
        
        
    
    def plotting_seasonality(self):
        
        print('Plotting graph...')
        
        fig, ax = plt.subplots(2, figsize = (10, 8), gridspec_kw={'height_ratios': [3, 1]})
        ax[0].bar(x = self.seasonality_mean.index, height = self.seasonality_mean.iloc[:], yerr = self.seasonality_std, alpha=0.5, ecolor='black', capsize=10)
        ax[0].axhline(0, alpha=0.5)
        ax[0].set_xlabel(self.interval)
        ax[0].set_ylabel("Performance in %")
        #add_value_labels(ax[0])
        
        ax[1].bar(x = self.seasonality_prob.index, height = self.seasonality_prob.iloc[:], alpha = 0.5, capsize = 10)
        #add_value_labels(ax[1])
        
        # Set arrow
        if self.interval == '1mo':
            ax[0].arrow(x = dt.date.today().month, y = -0.5, dx = 0, dy = 0, head_width=0.3, head_length=0.05, fc='r', ec='r')
            ax[1].arrow(x = dt.date.today().month, y = 0.05, dx = 0, dy = 0, head_width=0.3, head_length=0.05, fc='r', ec='r')
        if self.interval == '1wk':
            ax[0].arrow(x = dt.date.today().isocalendar()[1], y = -0.2, dx = 0, dy = 0, head_width=0.3, head_length=0.02, fc='r', ec='r')
            ax[1].arrow(x = dt.date.today().isocalendar()[1], y = 0.05, dx = 0, dy = 0, head_width=0.3, head_length=0.02, fc='r', ec='r')
        if self.interval == '1d':
            ax[0].arrow(x = dt.date.today().day, y = -0.05, dx = 0, dy = 0, head_width=0.3, head_length=0.005, fc='r', ec='r')
            ax[1].arrow(x = dt.date.today().day, y = 0.05, dx = 0, dy = 0, head_width=0.3, head_length=0.005, fc='r', ec='r')
        
        plt.suptitle(f'{self.interval} seasonalities for {self.symbol}', size=28, fontweight="bold")
        ax[0].set_title(f'Data since {self.data.index[0]} with {self.interval} frequency.', fontname="Times New Roman", size=12)
        ax[1].set_title('Probability of a positive seasonality', fontname="Times New Roman", size = 12)

        
        plt.tight_layout()
        plt.show()
        
        print('Graph plotted.')
        
        
        
# Running the main programm
if __name__ == '__main__':
    """Requires command line entry!
    """
    
    print('Running seasonality analysis tool....')
    
    parser = argparse.ArgumentParser(description='Process relevant inputs.')
    parser.add_argument('--symbol', type=str, help='Input symbol according to yahoo finance symbols.')
    parser.add_argument('--interval', type=str, help='Input interval for seasonality analysis.')
    parser.add_argument('--period', type=str, help='Input period for seasonality analysis time horizon.', default = 'max')
    parser.add_argument('--daily', type=str, help='Decide, which daily seasonality shall be measured. Daily per weekday or over the month: wd vs. m', default = 'wd')
    parser.add_argument('--backtest', type=int, help='If you want to have a backtest, insert the number of the traded seasonality', default = None)
    args = parser.parse_args()
    
    S = Seasonalities(symbol = args.symbol, interval = args.interval, period = args.period, daily_measure = args.daily)
    S.get_data()
    S.calculate_seasonality()
    S.plotting_seasonality()
    if args.backtest != None:
        S.backtest(season = args.backtest)
    
    print('Program executed.')
    
    
        