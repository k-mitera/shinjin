import os
import shutil
import process_data
import read_exchange
import anl_df
from read_nikkei import GET_KABUDATA
from selenium.webdriver.chrome.options import Options

############# メインプログラム ##################

#指定した銘柄の株価を取得する。
if __name__ == '__main__':
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    
    STOCKNUMS=["^N225","^DJI"]
    RELEATEDSTOCKS=[]

    main_stock_cd = int(input("分析したい証券コードを入力してください:"))
    STOCKNUMS.append(main_stock_cd)

    while True:
        related_stock_cd = int(input("追加で一緒に分析したい会社の証券コードを入力してください。(入力終了時は0を入力):"))
        if related_stock_cd == 0:
            break
        else:
            RELEATEDSTOCKS.append(related_stock_cd)

    EXECUTABLE_PATH=os.getcwd()+"/chromedriver" #/chromedriver.exeのパス(同じディレクトリを指定)
    HOME_PATH= os.getcwd()+"/basic_datalist/" #基本の株価データを保存する場所を指定する。
    PROCESS_HOME_PATH = os.getcwd() + "/basic_add_column/"

    # # 基本となるデータリストを作る(分析対象株価、日経平均、ダウ、為替)
    # if not os.path.isdir(HOME_PATH):
    #     os.makedirs(HOME_PATH)
    # for stock in STOCKNUMS:
    #     GET_KABUDATA(stock,2020,options,EXECUTABLE_PATH,HOME_PATH)
    # read_exchange.add_exchange_data(HOME_PATH) # 為替の情報を追加
    
    if not os.path.isdir(PROCESS_HOME_PATH):
        os.makedirs(PROCESS_HOME_PATH)
    process_data.add_column_csv(os.listdir(HOME_PATH),str(main_stock_cd),HOME_PATH,PROCESS_HOME_PATH)

    # 追加する関連企業のデータリストを作る
    RELATED_PATH=os.getcwd()+"/related_datalist/"
    PROCESS_RELATED_PATH = os.getcwd() + "/related_add_column/"
    if not os.path.isdir(RELATED_PATH):
        os.makedirs(RELATED_PATH)
    if not os.path.isdir(PROCESS_RELATED_PATH):
        os.makedirs(PROCESS_RELATED_PATH)
    # for stock in RELEATEDSTOCKS:
    #     GET_KABUDATA(stock,2020,options,EXECUTABLE_PATH,RELATED_PATH)
    process_data.add_column_csv(os.listdir(RELATED_PATH),str(main_stock_cd),RELATED_PATH,PROCESS_RELATED_PATH)

    # メインデータの分析
    csv_files = os.listdir(PROCESS_HOME_PATH)
    main_df = process_data.make_df(csv_files,PROCESS_HOME_PATH,str(main_stock_cd))
    mainscore = anl_df.anl_df(main_df)
    print("元のモデル")
    print(mainscore)

    improve_rate = {}
    # メインデータと関連企業データを一つずつ加えたTEMPデータフォルダを作成し、分析
    for f in os.listdir(PROCESS_RELATED_PATH):
        TEMP_PATH=os.getcwd()+"/temp_datalist"+f.split(".")[0]+"/"
        try:
            # 一企業のみくわえて分析するようのディレクトリを作る
            shutil.copytree(PROCESS_HOME_PATH,TEMP_PATH)
            shutil.copyfile(PROCESS_RELATED_PATH+f,TEMP_PATH+f)
        except FileExistsError:
            pass
        # TEMPのデータに対して分析を開始
        csv_files = os.listdir(TEMP_PATH)
        campare_df = process_data.make_df(csv_files,TEMP_PATH,str(main_stock_cd))
        comparescore = anl_df.anl_df(campare_df)
        # モデルの改善率を格納
        improve_rate[f.split(".")[0]] = comparescore[0]/mainscore[0]
    
    print(improve_rate)
    sorted_improved_rate = sorted(improve_rate.items(), key=lambda x:x[1], reverse=True)
    print(sorted_improved_rate)
    print("リストの長さ")
    print(len(sorted_improved_rate))

    # 改善率トップ10の企業をFINALデータフォルダを作成し、分析する
    FINAL_PATH=os.getcwd()+"/final_datalist/"

    try:
        # メインのデータたちをコピー
        shutil.copytree(PROCESS_HOME_PATH,FINAL_PATH)
    except FileExistsError:
        pass

    for num in range(0,10):
        filenm = sorted_improved_rate[num][0]
        for g in os.listdir(PROCESS_RELATED_PATH):
            if filenm in g:
                if sorted_improved_rate[num][1] >= 1:
                    shutil.copyfile(PROCESS_RELATED_PATH+g,FINAL_PATH+g)
                else:
                    pass
            else:
                pass
    

    # 最終分析
    final_csv_files = os.listdir(FINAL_PATH)
    final_df = process_data.make_df(final_csv_files,FINAL_PATH,str(main_stock_cd))
    finalscore = anl_df.anl_df(final_df)
    print("最終結果")
    print(finalscore)





