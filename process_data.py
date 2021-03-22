import pandas as pd
import os
import glob
import re

# 日付の書き方を全て(yyyy/mm/dd)という表記に直すための処理
def change_date_form(date_list):
    changed_date_list = []
    for i in date_list:
        changed_date = re.sub("-","/",i)
        changed_date_list.append(changed_date)
    return changed_date_list

# DATEのカラムは全て(yyyy/mm/dd)という表記に直す
# データフレームに終値の前日からの変化率カラムを追加
# 第二引数に指定した証券コードのものは値上がりの結果フラグカラムも追加(翌日に値上がりして1%以上値上がりして居たら1,それ以外は0)
def add_column_csv(csv_list,main_data_nm,read_path,out_path):
    for i in csv_list:
        if not i.startswith('.'):
            df = pd.read_csv(read_path+i,engine='python')
            filename = os.path.split(i)[1]
            add_column_nm_rate = filename.split(".")[0] + "_rate"
            close_data = df['CLOSE'].tolist()
            add_column_rate = [0]
            
            # DATEカラムの表記を揃える
            df["DATE"] = pd.Series(change_date_form(df["DATE"].tolist()))

            #前日からの上がり率のカラムを追加
            for j in range (1, len(close_data)):
                rate = (close_data[j]-close_data[j-1])/close_data[j-1]*100
                add_column_rate.append(rate)

            df[add_column_nm_rate] = add_column_rate

            #メインに指定したファイルの場合は上がり判定カラムも追加
            if main_data_nm in filename:
                add_column_nm_result = "RESULT"
                add_column_result = []

                for k in add_column_rate:
                    if k >= 0.5:
                        add_column_result.append(1)
                    else:
                        add_column_result.append(0)
                #翌日上がったかどうかを判定したいので末尾にもう一つ0を足して先頭を削除
                add_column_result.append(0)
                add_column_result.pop(0)
                df[add_column_nm_result] = add_column_result
        
            df.to_csv(out_path+'/'+filename.split(".")[0]+'_add_column.csv',index = None)
        else:
            pass
# add_column_csv(os.listdir("./data"),"4307")

# 第二引数に予測したい証券コードを入力しそのファイルのみrateとresultの2カラムを持ってくる
def make_df(csv_list,path,main_data_nm):
    for i in csv_list:
        if not i.startswith('.'):
            if main_data_nm in i:
                result_df = pd.read_csv(path+i,engine='python').set_index("DATE")
                result_df = result_df.iloc[:,-2:]
            else:
                pass
        else:
            pass
    for j in csv_list:
        if not j.startswith('.'):
            if main_data_nm in j:
                pass
            else:
                temp_df = pd.read_csv(path+j,engine='python').set_index("DATE")
                temp_df = temp_df.iloc[:,-1]
                result_df = pd.merge(result_df,temp_df,left_index=True,right_index=True)
        else:
            pass
    return result_df

# make_df(os.listdir("./column_add_data"),"4307")
    





    

