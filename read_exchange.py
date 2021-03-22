import pandas_datareader.data as web
import datetime

HOME_PATH="/Users/mitera/Documents/data/" #株価データを保存する場所を指定する。

def add_exchange_data(HOME_PATH):
    df=web.DataReader('JPY=X','yahoo',start='2010-01-01',end='2020-12-31')
    df=df.drop(columns='Adj Close') #列Aを削除する。
    df.reset_index("Date",inplace=True)
    df= df.rename(columns={'Date': 'DATE','High': 'HIGH', 'Low': 'LOW',  'Open': 'OPEN', 'Close': 'CLOSE',  'Volume': 'VOL' })#各列名を所望の列名に変更する。
    df = df[['DATE','CLOSE','HIGH','LOW','OPEN','VOL']]
    df.set_index("DATE",inplace=True)
    df.to_csv(HOME_PATH + 'JPY_X.csv') #dfを外部のcsvファイルに書き込む 