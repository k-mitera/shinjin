#-*- coding:utf-8 -*-
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import datetime
from pyvirtualdisplay import Display
from selenium.webdriver.common.by import By
import os.path
import pandas_datareader.data as web #米国株データの取得ライブラリを読み込む


####(1)取得する株価番号,取得基準年を記載します。#######

# STOCKNUMS=[4307,"^N225","^DJI"]   #取得する株価番号を入力します。
# #STOCKNUMS=[1570]
# YEAR=2020 #取得基準年を記入します。取得基準年から過去2年分の株価データを取得します。

# ####(2)chromedriverの設定を行います。#######

# options = Options() 
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')

# ####(3)X環境がない(コンソール上で実施)場合、以下のdisplayコマンドを有効にする。jupyterで実行する場合は、以下のdisplayコマンドは無効にする#######

# #pyvirtualdisplayパッケージを使って仮想ディスプレイ（Xvfb）を起動させてSeleniumを使う方法
# # display = Display(visible=0, size=(1024, 1024))
# # display.start()


# ####(4) 各種フォルダの設定を行います ##############

# EXECUTABLE_PATH="/Users/mitera/Documents/chromedriver" #/chromedriver.exeのパスを指定する。
# HOME_PATH="/Users/mitera/Documents/data/" #株価データを保存する場所を指定する。


#### (5)株価取得クラス GET_KABUDATA #####

class GET_KABUDATA():

    ### (5-1)コンストラクターを定義する ###
    def __init__(self,stocknum,year,options,EXECUTABLE_PATH,HOME_PATH):

        stocknum=str(stocknum)


        try:
            print('銘柄番号' + str(stocknum)+'の株価データを取得します')

            #csvファイルが存在しない(今回初めてデータを取得する銘柄)場合
            if os.path.exists(HOME_PATH + str(stocknum)+'.csv')==False:
                #stocknum(銘柄名)が数値型ではない(=日本個別株ではない場合)
                if stocknum.isnumeric()==False:
                    self.get_PandasDR(stocknum,year,HOME_PATH) #pandas_readerを実行する

                #stocknum(銘柄名)が数値型の場合(=日本個別株の場合)
                else:
                    self.get_new_stockdat(stocknum,year,options,EXECUTABLE_PATH,HOME_PATH) #株式投資メモから過去10年分のデータをスクレイピングする。

            #csvファイルが存在する場合(過去にデータを取得したことのある銘柄の場合)           
            else:
                #stocknum(銘柄名)が数値型ではない(=日本個別株ではない場合)
                if str(stocknum).isnumeric()==False:
                    self.get_PandasDR(stocknum,year,HOME_PATH) #pandas_readerを実行する

                #stocknum(銘柄名)が数値型の場合(=日本個別株の場合)
                else:
                    self.get_add_stockdat(stocknum,year,options,EXECUTABLE_PATH,HOME_PATH) #現在保有していない日にちの株価データを株式投資メモから取得し、csvファイルに追記する。

            print('銘柄番号' + str(stocknum)+'の株価データ取得を完了しました')
            print('**********')

        #エラー処理(存在しない銘柄番号を指定した。株式投資メモのサイトがダウンしておりデータがスクレイピングできない) 
        except Exception as e:
            print(e)
            print('株価取得失敗')                


    ### (5-2)過去に株価を取得した銘柄の場合、サーバーにある株価データと、取得した株価データの差分比較を行い、差分のみを取得しcsvファイルに書き込みを行う            
    def get_add_stockdat(self,stocknum,year,options,EXECUTABLE_PATH,HOME_PATH):


        #(5-2-1)各種変数を初期化する。
        s_date=[]
        s_open=[]
        s_high=[]
        s_low=[]
        s_close=[]
        s_volume=[]
        dfstock=[]
        add_s_date=[]
        add_s_open=[]
        add_s_high=[]
        add_s_low=[]
        add_s_close=[]
        add_s_volume=[]  
        add_s_stock=[] 
        add_dfstock=[]       

        #(5-2-2)株式投資メモに表示される個別株の株価表にアクセスする(スクレイピングを行う)。
        browser = webdriver.Chrome(options=options,executable_path=EXECUTABLE_PATH)
        url='https://kabuoji3.com/stock/'+ str(stocknum) + '/'+ str(year) + '/'
        browser.get(url)
        elem_tmp0 = browser.find_element_by_class_name('data_contents')
        elem_tmp1 = elem_tmp0.find_element_by_class_name('data_block')
        elem_tmp2 = elem_tmp1.find_element_by_class_name('data_block_in')
        elem_tmp3 = elem_tmp2.find_element_by_class_name('table_wrap')
        elem_table= elem_tmp3.find_element_by_class_name('stock_table.stock_data_table')
        elem_table_kabuka=elem_table.find_elements(By.TAG_NAME, "tbody")

        #(5-2-3)株価表の１行ずつ指定し、各日の株価を読み取る
        for i in range(0,len(elem_table_kabuka)):

            kabudat=elem_table_kabuka[i].text.split()   
            s_date.append(str(kabudat[0].split('-')[0]) +'/'+ str(kabudat[0].split('-')[1]) +'/'+ str(kabudat[0].split('-')[2])) #日付けを取得    
            s_open.append(kabudat[1]) #始値を取得する
            s_high.append(kabudat[2]) #高値を取得する。
            s_low.append(kabudat[3]) #低値を取得する。
            s_close.append(kabudat[4]) #終値を取得する。
            s_volume.append(kabudat[5]) #出来高を取得する。
            s_stock={'DATE':s_date,'CLOSE':s_close,'OPEN':s_open,'HIGH':s_high,'LOW':s_low,'VOL':s_volume} #始値,高値,低値,終値,出来高をリストに入れる      


        dfstock=pd.DataFrame(s_stock,columns=["DATE","CLOSE","OPEN","HIGH","LOW","VOL"]) #リストs_stockをDataFrame化する。
        dfstock.set_index("DATE",inplace=True)
        dfstock=dfstock.sort_index() #取得した株価データを日付順に並べる。
        dfstock.reset_index("DATE",inplace=True)


        dfstock_csv= pd.read_csv(HOME_PATH + str(stocknum)+'.csv', index_col=0) #サーバーに保存している株価データをcsvファイルから読み出す。
        dfstock_csv.reset_index("DATE",inplace=True)  #index指定を解除する


        #(5-2-4)サイトから新規にスクレイピングした株価データの最新の日付を取得する
        dfstock_latest = dfstock['DATE'].iloc[dfstock['DATE'].count()-1]
        dfstock_latest=datetime.datetime.strptime(dfstock_latest, '%Y/%m/%d') #日付けを文字型に設定する
        dfstock_latest_date=datetime.date(dfstock_latest.year, dfstock_latest.month, dfstock_latest.day) #日付けを文字型から日付け型に変更する


        #(5-2-5)サーバーに保存されている株価データの最新の日付を取得する。  
        dfstock_csv_latest = dfstock_csv['DATE'].iloc[dfstock_csv['DATE'].count()-1]
        dfstock_csv_latest=datetime.datetime.strptime(dfstock_csv_latest, '%Y/%m/%d') #日付けを文字型に設定する
        dfstock_csv_latest_date =datetime.date(dfstock_csv_latest.year, dfstock_csv_latest.month, dfstock_csv_latest.day) #日付けを文字型から日付け型に変更する

        #(5-2-6)サイトから新規にスクレイピングした株価データの最新の日付と、サーバーに保存されている株価データの最新の日付の差を算出する。
        difday=dfstock_latest_date - dfstock_csv_latest_date 



        #(5-2-7)サーバーに保存されている株価データに対し、不足分の株価データを加え最新の状態にする。
        for i in range(len(elem_table_kabuka)-difday.days,len(elem_table_kabuka)):


            kabudat=elem_table_kabuka[i].text.split()   
            add_s_date.append(str(kabudat[0].split('-')[0]) +'/'+ str(kabudat[0].split('-')[1]) +'/'+ str(kabudat[0].split('-')[2]))     
            add_s_open.append(kabudat[1])
            add_s_high.append(kabudat[2])
            add_s_low.append(kabudat[3])
            add_s_close.append(kabudat[4])
            add_s_volume.append(kabudat[5])
            add_s_stock={'DATE':add_s_date,'CLOSE':add_s_close,'OPEN':add_s_open,'HIGH':add_s_high,'LOW':add_s_low,'VOL':add_s_volume} 


        #不足分の株価データをリスト形式からDataFrame形式に変換する
        add_dfstock=pd.DataFrame(add_s_stock,columns=["DATE","CLOSE","OPEN","HIGH","LOW","VOL"])    

        #(5-2-8)サーバーに保存されている株価データに対し、不足分の株価データを加える。
        dfstock=pd.concat([dfstock_csv, add_dfstock])  

        #(5-2-9)更新分を追加した株価データをcsvに書き出しする        
        dfstock.set_index("DATE",inplace=True)
        dfstock.to_csv(HOME_PATH + str(stocknum)+'.csv')


        browser.close()#ブラウザを閉じる  for文の外に書かないとエラーになる         


     ### (5-3)新規に株価データを取得する。
    def get_new_stockdat(self,stocknum,year,options,EXECUTABLE_PATH,HOME_PATH):

         #(5-3-1)各種変数を初期化する。       
        s_date=[]
        s_open=[]
        s_high=[]
        s_low=[]
        s_close=[]
        s_volume=[]
        dfstock=[]

        #(5-3-2)株式投資メモに表示される個別株の株価表にアクセスする(スクレイピングを行う)。
        browser = webdriver.Chrome(options=options,executable_path=EXECUTABLE_PATH)

        #(5-3-3)株式投資メモから過去10年分の株価データを取得する
        for j in range(0,11):
            url='https://kabuoji3.com/stock/'+ str(stocknum) + '/'+ str(year-j) + '/'
            browser.get(url)
            elem_tmp0 = browser.find_element_by_class_name('data_contents')
            elem_tmp1 = elem_tmp0.find_element_by_class_name('data_block')
            elem_tmp2 = elem_tmp1.find_element_by_class_name('data_block_in')
            elem_tmp3 = elem_tmp2.find_element_by_class_name('table_wrap')
            elem_table= elem_tmp3.find_element_by_class_name('stock_table.stock_data_table')
            elem_table_kabuka=elem_table.find_elements(By.TAG_NAME, "tbody")

             #(5-2-4)株価表の１行ずつ指定し、各日の株価を読み取る
            for i in range(0,len(elem_table_kabuka)):

                kabudat=elem_table_kabuka[i].text.split()   
                s_date.append(str(kabudat[0].split('-')[0]) +'/'+ str(kabudat[0].split('-')[1]) +'/'+ str(kabudat[0].split('-')[2]))     
                s_open.append(kabudat[1])
                s_high.append(kabudat[2])
                s_low.append(kabudat[3])
                s_close.append(kabudat[4])
                s_volume.append(kabudat[5])
                s_stock={'DATE':s_date,'CLOSE':s_close,'OPEN':s_open,'HIGH':s_high,'LOW':s_low,'VOL':s_volume}


        dfstock=pd.DataFrame(s_stock,columns=["DATE","CLOSE","OPEN","HIGH","LOW","VOL"]) #リスト -> DataFrameに変更
        dfstock.set_index("DATE",inplace=True)
        dfstock=dfstock.sort_index() #取得した株価データを日付順に並べる。
        dfstock.to_csv(HOME_PATH + str(stocknum)+'.csv') #株価データをCSVファイルに書き出す。

        browser.close()#ブラウザを閉じる  for文の外に書かないとエラーになる 




     ### 米国株や指数系の株価データを取得する。
    def get_PandasDR(self,stocknum,year,HOME_PATH):
        ed=datetime.datetime(year,12,31)
        st=datetime.datetime(year-10,1,1)
        df=web.DataReader(stocknum, 'yahoo',st,ed) #日経225の株価データを取得する
        df=df.drop(columns='Adj Close') #列Aを削除する。
        df.reset_index("Date",inplace=True)
        df= df.rename(columns={'Date': 'DATE','High': 'HIGH', 'Low': 'LOW',  'Open': 'OPEN', 'Close': 'CLOSE',  'Volume': 'VOL' })#各列名を所望の列名に変更する。
        df = df[['DATE','CLOSE','HIGH','LOW','OPEN','VOL']]
        df.set_index("DATE",inplace=True)
        df.to_csv(HOME_PATH + str(stocknum)+'.csv') #dfを外部のcsvファイルに書き込む 




############# メインプログラム ##################

#指定した銘柄の株価を取得する。
# if __name__ == '__main__':        

#     for stock in STOCKNUMS:
#         GET_KABUDATA(stock,YEAR)

#     print('株価取得終了しました。')
