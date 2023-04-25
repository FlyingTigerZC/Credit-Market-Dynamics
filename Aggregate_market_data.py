#########################################
# created on 2023 @author: FlyingTigerZC
########################################
# This is distributed in the hope that it will be useful, but WITHOUT any warrant.


import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt  #for plot charts
from functools import reduce
from dateutil.relativedelta import relativedelta, MO
from matplotlib.pyplot import figure
import matplotlib
#time frame 
from pandas.tseries.offsets import MonthEnd
from pandas.tseries.offsets import BQuarterEnd   #quarterend
from pandas.tseries.offsets import BYearEnd

#To define the market terms
Ratings=['AAA','AA','A','BBB','BB','B','CCC', 'mixed','na']
Asset_class_category=['Stock','Treasury','HY','IG','LevLoan', 'Corp','PrivateDebt', 'CLO','CDS', 'Distressed]
Market =['New_Issue', 'Secondary']
Measures = ['Yield', 'OAS','Spread', 'Price', 'Total_Return', 'Volume' ] #to add
DataTimeframe={'daily':1, 'monthly':2, 'quarterly':3, 'yearly':4}
ExpectedLifeCategory={'3-5yr':1, '5-7yr':2, '10yr':3, 'na':4}
                      
                      
#To read the files from different sources. This will be updated to scrape the unstructured data like in the formats of website, txt etc
# to automate the task of updating data up-to-date
# Data sources include https://fred.stlouisfed.org/, Bloomberg, MCR LSTA LL Index, and others that will be added
# High Yield: 
#   Effective Yield
#     --- ICE BofA US High Yield index Effective Yield(BAMLH0A0HYM2EY)
#     --- ICE BofA Single-B US High Yield Index Effective Yield (BAMLH0A2HYBEY)
#.    --- ICE BofA 5-7 Year US Corporate Index Effective Yield,(BAMLC3A0C57YEY)
#    OAS
#.    --- ICE BofA US High Yield Index Option-Adjusted Spread(BAMLH0A0HYM2); 
#     --- ICE BofA Single-B US High Yield Index Option-Adjusted Spread(BAMLH0A2HYB),

# Treasury: US 5-yr Teasury yield that is more commensurate to the expected life of leveraged loans/High yields

# Stock: S&P500, Rusell 2000 and other stock indices that are more commensurate to the composition of credit market in terms of the obligors to be added 
#LL: Leveraged Loan Indice
#CLO:   CLO AAA, BBB, and BB spreads                   
#CDS:
#Private Credit:

data_files_dict={0:['DGS5.xls', 'FRED Graph', 'US_5yT_Yield' , 'US_5yT_Yield', 11, 'A:B', True, 'Treasury', 'AAA', 2],
                 1:['BAMLH0A0HYM2EY.xls', 'FRED Graph','BAMLH0A0HYM2EY','ICE_US_HY_Yield', 11,'A:B', True, 'HY', 'B',2],
                 2:['BAMLH0A2HYBEY.xls','FRED Graph','BAMLH0A2HYBEY','ICE_US_HY_B_Yield', 11, 'A:B', True, 'HY', 'B',2],
                 3:['BAMLC3A0C57YEY.xls', 'FRED Graph','BAMLC3A0C57YEY','ICE_57yr_US_Corp_Yield', 11, 'A:B', True, 'Corp', 'mixed', 2],
                 4:['BAMLH0A0HYM2.xls', 'FRED Graph', 'BAMLH0A0HYM2','ICE_US_HY_OAS', 11, 'A:B', True, 'HY', 'mixed',2],
                 5:['BAMLH0A2HYB.xls', 'FRED Graph', 'BAMLH0A2HYB','ICE_US_HY_B_OAS', 11, 'A:B', True, 'HY', 'B',2],
                 6:['SP500.xls','FRED Graph', 'SP500','SP500',11, 'A:B', True, 'Stock', 'na',4]
                 }

Spread_names_list = []
for key in data_files_dict:
    Spread_names_list.append(data_files_dict[key][2])
                      
#Main df
df_All=pd.DataFrame()
 
def Read_Convert_value(df):
    # to use Monthly data

    df.Date=pd.to_datetime(df.Date) + pd.offsets.MonthEnd(0)
    # to clear and clean data by removing 0, nan, inf
    df=df[~df.isin([0, np.nan, np.inf, -np.inf]).any(1)]
    column_name = df.columns[1]
    df_grp=df.groupby(df.columns[0])
    
    tmp_df= pd.DataFrame(columns=['Date',column_name, column_name+'_change', column_name+'_%change'])
    
    for group_date, df_group in df_grp:
        Periodic_Date = group_date
        Periodic_Begining_value = df_group.head(1)[column_name].tolist()[0]
        Periodic_Ending_value = df_group.tail(1)[column_name].tolist()[0]
        M_delta =  Periodic_Ending_value - Periodic_Begining_value
        #if bps:
        #    M_delta = M_delta * 100
        if M_delta == 0:
            percentage_change =0
        else:
            percentage_change = M_delta / Periodic_Begining_value
        tmp_df.loc[len(tmp_df.index)] = [group_date, Periodic_Ending_value, M_delta, percentage_change]
        #print(tmp_df)
    return tmp_df
                      
#To read all the market data files in the dict
col_Date_list=[]
col_value1_list=[]
col_value2_list=[]
col_value3_list=[]  
                      
                      
for key in data_files_dict:
                      
  df_tmp=pd.read_excel(data_files_dict[key][0],sheet_name=data_files_dict[key][1],usecols=data_files_dict[key][5],names=['Date', data_files_dict[key][3]]).iloc[data_files_dict[key][4]:]
  column_name = data_files_dict[key][3]
  df_tmp[column_name] = pd.to_numeric(df_tmp[column_name])
  #to read the date to Monthly, and get the Monthly value on each
  if key ==0:

    df_tmp=Read_Convert_value(df_tmp)
    # to add the columns in df_tmp to the master df that is df_All
    col_Date_list=df_tmp['Date'].tolist()
    col_value1_list=df_tmp[df_tmp.columns[1]].tolist()
    col_value2_list=df_tmp[df_tmp.columns[2]].tolist()
    col_value3_list=df_tmp[df_tmp.columns[3]].tolist()                  
    df_All['Date'] = col_Date_list
    df_All['Date'] = pd.to_datetime(df_All['Date'])
    df_All[df_tmp.columns[1]] = col_value1_list
    df_All[df_tmp.columns[2]] = col_value2_list
    df_All[df_tmp.columns[3]] = col_value3_list                  
  #to merge dataframes
  df_tmp=Read_Convert_value(df_tmp)
  df_tmp["Date"]= pd.to_datetime(df_tmp['Date'])
  df_All= pd.merge(df_All, df_tmp, how='outer', on='Date')
  #to remove rows with any Nan                    
  df_All=df_All.dropna(how='any')  
                      
#to plot the chart
plt.figure(figsize=(18, 6))
#for key in data_files_dict:
#    plt.plot(df_All['Date'],df_All['US_5yT_Yield_x'],linewidth=2.0,label ='5Yr Treasury Yield')
plt.xlabel('Date')
plt.ylabel('Yields(monthly) % change')
plt.plot(df_All['Date'],df_All['US_5yT_Yield_%change_x'],linewidth=2.0,label ='5Yr Treasury Yield % change')
plt.plot(df_All['Date'],df_All['ICE_US_HY_Yield_%change'],linewidth=2.0,label ='ICE BofA US HY Index Yield % change')
plt.plot(df_All['Date'],df_All['ICE_US_HY_B_Yield_%change'],linewidth=2.0,label ='ICE BofA US HY "B" rated Yield % change')
plt.plot(df_All['Date'],df_All['ICE_57yr_US_Corp_Yield_%change'],linewidth=2.0,label ='ICE BofA 5-7yr US Corp Index Yield % change')
plt.legend()

plt.title('Effective Yield % change across different asset classes in the credit market')
plt.show()
                      
                   
