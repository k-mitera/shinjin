import numpy as np
import pandas as pd
import os
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
import process_data

warnings.simplefilter('ignore')

# ランダムフォレストで分析し、適合率、再現率、F値のリストを返す
def anl_df(df):
    # 特徴量の標準化用
    std_model = StandardScaler()

    X = df[df.columns[df.columns != "RESULT"]].values
    y = df.loc[:,"RESULT"].values

    #正規化
    X = std_model.fit_transform(X)

    # logreg = LogisticRegression(penalty="l2",solver="saga",C=1)
    # print("ロジスティック回帰")
    # print(cal_by_model(X,y,logreg))

    randomforest = RandomForestClassifier(n_estimators=100)
    # print("ランダムフォレスト")
    return cal_by_model(X,y,randomforest)

    # svc = SVC()
    # print("SVC")
    # print(cal_by_model(X,y,svc))

    # linear_svc = LinearSVC()
    # print("線形SVC")
    # print(cal_by_model(X,y,linear_svc))

def cal_by_model(X,y,model):
    kfold = StratifiedKFold(n_splits=10)
    scores = []
    precision_scores = []
    recall_scores = []
    f1_scores = []
    for train, test in kfold.split(X,y):
        model.fit(X[train], y[train])
        y_pred = model.predict(X[test])

        #適合率、陽性と予測したもののうち、実際に陽性
        precision_scores.append(precision_score(y_true=y[test], y_pred=y_pred))
        #再現率、実際の陽性のうち、正解
        recall_scores.append(recall_score(y_true=y[test], y_pred=y_pred))
        #F値、適合率と再現率の調和平均
        f1_scores.append(f1_score(y_true=y[test], y_pred=y_pred))
        print(confusion_matrix(y[test],y_pred))
    # print(confusion_matrix(y[test],y_pred))
    scores.append(np.mean(precision_scores))
    scores.append(np.mean(recall_scores))
    scores.append(np.mean(f1_scores))

    return scores

# df = process_data.make_df(os.listdir("./column_add_data"),"4307")
# anl_df(df)

