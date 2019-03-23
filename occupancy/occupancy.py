
# coding: utf-8

# In[2]:


import os
import pandas as pd
import numpy as np
from glob import glob
import json
from pprint import pprint
import datetime
import calendar

import matplotlib.pyplot as plt
from pprint import pprint
from IPython.display import display


# In[4]:


## set parameters to modify the raw hourly occupancy data

def modify(df):
    startDate = datetime.datetime(2015, 7, 1, 0, 0) # replace with the starting date
    endDate = datetime.datetime(2019, 3, 1, 0, 0)   # replace with the ending date
    diff = endDate - startDate
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    date_list = [startDate + datetime.timedelta(minutes=60*x) for x in range(0, hours)]
    datetext=[x.strftime('%Y-%m-%d T%H:%M Z') for x in date_list]
    
    fy15 = datetime.datetime(2016, 7, 1, 0, 0).date()
    fy16 = datetime.datetime(2017, 7, 1, 0, 0).date()
    fy17 = datetime.datetime(2018, 7, 1, 0, 0).date()
    
    dateOnly = [x.date() for x in date_list]
    hourOnly = [x.hour for x in date_list]
    monthOnly = [x.month for x in date_list]
    weekNo = [x.weekday() for x in date_list]
    
    df['time'] = datetext
    df['hr'] = hourOnly
    df['date'] = dateOnly
    df['month'] = monthOnly
    df['weekNo'] = weekNo
    df['weekday'] = np.where(df['weekNo'] < 5, 'weekday', 'weekend')
    df['season'] = np.where((df['month'] > 3) & (df['month'] < 11), 'summer','winter')
    df['fy'] = np.where(df['date'] < fy15, 'fy15', np.where((df['date'] < fy16) & (df['date'] >= fy15),'fy16',np.where((df['date'] < fy17) & (df['date'] >= fy16),'fy17','fy18')))


# In[ ]:


df_avgOcc = pd.DataFrame(columns=['totl','Contract','Transient','Validations','loct'])
df_dailyPeak = pd.DataFrame(columns = ['Contract','Transient','Validations','date','fy','hr','loct','month','season','totl','weekday'])

## two versions of code to accommodate raw hourly occupancy data with different dimensions

# Version 1, "user_Type" dimension

for filename in sorted(glob('/userType/*.txt')):
    basename = os.path.split(filename)[1][:-4]
    with open(filename,'r') as file:
        df = pd.DataFrame()
        d = json.load(file)
        for item in d['value']:
            if item['group'] in item['group'] :
                col_name = '{} - {}'.format(basename,item['group'])
                col_name = item['group']
                df[col_name] = item['value']
        df['loct'] = basename
        df['totl'] = df.loc[:,df.columns].sum(axis = 1)
        modify(df)
        
        avgOcc = df.groupby(['fy','weekday','hr']).mean().drop(['weekNo','month'], axis=1)
        avgOcc['loct'] = basename
        df_avgOcc = df_avgOcc.append(avgOcc)
        
        
        peakOcc = df.sort_values(['totl'], ascending=False).drop_duplicates(['date']).sort_values(['date'])
        peakOcc = peakOcc.drop(['time','weekNo'],axis = 1)
        df_dailyPeak = df_dailyPeak.append(peakOcc)


# In[ ]:


# Version 2, "system" dimension

for filename in sorted(glob('/syst/*.txt')):
    basename = os.path.split(filename)[1][:-4]
    with open(filename,'r') as file:
        df = pd.DataFrame()
        d = json.load(file)
        for item in d['value']:
            if item['group'] in item['group'] :
                col_name = '{} - {}'.format(basename,item['group'])
                col_name = 'Transient'
                df[col_name] = item['value']
        df['loct'] = basename
        df['totl'] = df['Transient']
        
        modify(df)
        
        avgOcc = df.groupby(['fy','weekday','hr']).mean().drop(['weekNo','month'], axis=1)
        avgOcc['loct'] = basename
        df_avgOcc = df_avgOcc.append(avgOcc)
        
        peakOcc = df.sort_values(['Transient'], ascending=False).drop_duplicates(['date']).sort_values(['date'])
        peakOcc = peakOcc.drop(['time','weekNo'],axis = 1)
        df_dailyPeak = df_dailyPeak.append(peakOcc)                              


# In[ ]:


## potential type conversion

cols = ['Contract', 'Transient', 'Validations','totl']
df_dailyPeak[cols] = df_dailyPeak[cols].apply(pd.to_numeric, errors='coerce', axis=1)
df_avgOcc[cols] = df_avgOcc[cols].apply(pd.to_numeric, errors='coerce', axis=1)


# In[ ]:


## export

df_avgOcc.to_csv('avgOcc.csv')
df_dailyPeak.to_csv('dailyPeak.csv')

peakByFY = df_dailyPeak.groupby(['loct','fy','weekday']).mean()
peakByFY.to_csv('avgPeak_ByFY.csv')

peakByFYSeason = df_dailyPeak.groupby(['loct','fy','weekday','season']).mean()
peakByFYSeason.to_csv('avgPeak_BySeason.csv')

