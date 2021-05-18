import requests
import pandas as pd
from io import StringIO
# StringIO顧名思義就是在內存中讀寫str。
import sqlite3

# 參考 # https://markjong001.pixnet.net/blog/post/235358810
#      https://www.learncodewithmike.com/2021/05/pandas-and-sqlite.html

url = r'http://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL?response=open_data'
res =  requests.get(url)
# <class 'requests.models.Response'>
# res.json() # error 可能要加 cookie

res_df = pd.read_csv(StringIO(res.text))
res_df.head()

conn = sqlite3.connect('test.sqlite3')
#存檔
res_df.to_sql('daily',conn,if_exists='replace')
# 讀檔
df = pd.read_sql('select * from daily',conn)