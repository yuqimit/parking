
# coding: utf-8


import pandas as pd
import numpy as np

import datetime
import calendar

import matplotlib.pyplot as plt
from IPython.display import display



## parameters

end_time = datetime.datetime(2019, 3, 1, 0, 0)  # use transactions from the starting date to the end of 2/28/2019

## downtown data 
# s extract --garages 571548 --start-time 2019-01-01 --end


## Load and modify the data

df = pd.read_csv('transactions.csv')
df['exitTime'] = pd.to_datetime(df['exit_time'])
df['entryTime'] = pd.to_datetime(df['entry_time'])
df = df.loc[(df['exitTime'] < end_time) & (df['user_type'] != 'Transient')] # only Contract parking before certain time

df2 = df[['card_number','entryTime','exitTime','user_type']]

df2['exit_date'] = [x.date() for x in df2['exitTime']]
df2['ent_date'] = [x.date() for x in df2['entryTime']]
monthOnly = [x.month for x in df2['exit_date']]
weekNo = [x.weekday() for x in df2['exit_date']]
df2['month'] = monthOnly
df2['dow'] = weekNo

df2.loc[df2['user_type'] == 'ZIPCAR', 'user_type'] = 'ZIP CAR' # clean acount names


## How many unique cards made transactions each month for each account

uniqCard = df2.groupby(['user_type','month'])['card_number'].nunique()
print(uniqCard)
uniqCard.to_csv('uniqueCard.csv')


## How many transactions each cards made each month by account

transPerCard = df2.groupby(['user_type','month']).card_number.value_counts().reset_index(name='count')
print(transPerCard)
transPerCard.to_csv('transPerCard.csv')


## How many transactions each cards made per month
uses = df2.groupby(['card_number']).size().reset_index(name='count').sort_values(['count'],ascending=False)
uses['count_perMonth'] = uses['count']/2
uses.hist(column='count_perMonth',bins = 30)


## How many days each card was used per month

uses2 = df2.groupby('card_number').agg({'exit_date': 'nunique'}).sort_values('exit_date',ascending=False)
uses2['exit_date_perMonth'] = uses2['exit_date']/2
uses2.hist(column='exit_date_perMonth',bins = 30)
#uses2.to_csv('usesByCard2.csv')


## Cards with more than one entries within one day

use_daily = df2.groupby(['card_number','exit_date'])['exit_date'].size().reset_index(name='count')
use_daily.to_csv('dailyUse.csv')
use_daily_multi = use_daily.loc[use_daily['count'] > 1]
use_daily_multi
#use_daily_multi.to_csv('dailyUse_mul.csv')

