#%matplotlib inline
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import scipy
import pandas as pd
from itertools import islice
import sys

plt.style.use("seaborn-whitegrid")

class ProposalWay:
    def __init__(self):
        pass

    #SSAの窓関数の作成
    def window(self, seq, n):
        it = iter(seq)
        #itをn個ずつ取得し，タプルとして生成
        result = tuple(islice(it, n))
        #要素数がnならresultを戻す
        if len(result) == n:
            yield result
        #resultタプルの先頭を削除し，一つ要素の追加
        #要素数が一つの場合，コンマをつける
        for elem in it:
            result = result[1:] + (elem, )
            yield result

    def SSA_anomaly(self, test, traject, window_size, ncol_t, ncol_h, ns_t, ns_h, normalize = False):
        #test: テスト行列用の部分時系列データ
        #traject: 履歴行列を作る部分時系列
        #ns_h: 履歴行列から取り出す特異ベクトルの数
        #ns_t: テスト行列から取り出す特異ベクトルの数

        # window_size*ncol_tの行列
        test_matrix = np.array(
            tuple(x[:ncol_t] for x in self.window(test, window_size))[:window_size])
        #X = np.column_stack([F[i:i+L] for i in range(0,K)])
        #F:データ, L:行数, K:列数
        #の書き方も可能

        history_matrix = np.array(
            tuple(x[:ncol_h] for x in self.window(traject, window_size))[:window_size])

        #正規化により単調増加などの変化は検知できなくなる
        if normalize:
            #平均0 分散1に正規化
            test_matrix = (test_matrix - test_matrix.mean(
                axis = 0, keepdims = True)) /test_matrix.std(axis = 0)

            history_matrix = (history_matrix - history_matrix.mean(
                axis = 0, keepdims= True)) / history_matrix.std(axis = 0)

        #特異分解
        #[0] U, [1] x, [2] V
        left_singular_vector_Q, singular_value_vector_Q = np.linalg.svd(test_matrix)[0:2]

        #print("特異値寄与率")
        #x = (singular_value_vector_Q[0])/np.sum(singular_value_vector_Q)
        #if x > 0.8:
        #    print("safe")
        #else:
        #    print(x)
        #    print("no")

        left_singular_vector_Q = left_singular_vector_Q[:, 0:ns_t]
        ratio_test = sum(singular_value_vector_Q[0:ns_t]) / sum(singular_value_vector_Q)

        left_singular_vector_U, singular_value_vector_U = np.linalg.svd(history_matrix)[0:2]
        left_singular_vector_U = left_singular_vector_U[:, 0:ns_h]
        ratio_history = sum(singular_value_vector_U[0:ns_t]) / sum(singular_value_vector_U)

        anomaly = 1 - np.linalg.svd(np.matmul(left_singular_vector_U.T, left_singular_vector_Q),
                                    compute_uv=False)[0]

        return (anomaly, ratio_test, ratio_history)


    def SSA_change_detection(self, series, window_size, lag, ncol_h=None, ncol_t=None, ns_h=None, ns_t=None,
                             standardize=False, normalize=False, fill=True):
        if ncol_h is None:
            #履歴行列の列数
            ncol_h = round(window_size / 2)

        if ncol_t is None:
            #テスト行列の列数
            ncol_t = round(window_size / 2)

        if ns_h is None:
            ns_h = np.min([1, ncol_h])
        if ns_t is None:
            ns_t = np.min([1, ncol_t])
        if min(ncol_h, ncol_t) > window_size:
            print("ncol and ncol must be <= window_size")

        if ns_h > ncol_h or ns_t > ncol_t:
            print("Recommended to set ns_h >= ncol_h and ns_t >= ncol_t")

        start_at = lag + window_size + ncol_h
        end_at = len(series) + 1
        res = []
        for time in range(start_at, end_at):
            res = res + [self.SSA_anomaly(series[time - window_size - ncol_t:time],
                                     series[time - lag - window_size - ncol_h: time - lag],
                                     window_size = window_size, ncol_t = ncol_t, ncol_h = ncol_h,
                                     ns_t = ns_t, ns_h = ns_h,
                                     normalize = normalize)]

        anomaly_array = [round(anomaly, 14) for anomaly, ratio1, ratio2 in res] #res = [anomaly, ratio_test, ratio_history]
        ratio_t_array = [ratio1 for anomaly, ratio1, ratio2 in res]
        ratio_h_array = [ratio2 for anomaly, ratio1, ratio2 in res]
        if fill == True:
            #NaNの作成
            anomaly_array = [np.nan] * (start_at -1) + anomaly_array

        if standardize:
            #nansumでNaN以外の値の和
            c = np.nansum(anomaly_array)
            if c!= 0:
                anomaly_array = [anomaly/c for anomaly in anomaly_array]
        return [anomaly_array, ratio_t_array, ratio_h_array]

def print_result(data, index):
    if index == 0:
        #index == 0ならx
        df = pd.DataFrame(data, columns=["x", "s=1", "s=2","s=3"])
        df.round({"s=1":5, "s=2":5}).to_csv("proposal_result_x.csv")
    else:
        #index == 1ならy
        df = pd.DataFrame(data, columns=["y", "s=1", "s=2", "s=3"])
        df.round({"s=1":5, "s=2":5}).to_csv("proposal_result_y.csv")

    #df = pd.DataFrame(data, columns=["x", "s=1", "s=2"])
    #pd.options.display.float_format = '{:.2f}'.format
    #df.round({"s=1":5, "s=2":5}).to_csv("proposal_result.csv")

if __name__ == "__main__":

    args = sys.argv

    file_name = "./data_for_proposal/vehicle_{}.csv".format(args[1])
    #file_name2 = "./data_for_proposal/vehicle_11.csv"
    #file_name2 = "./data_12_0km_40km/vehicle_803.csv"
    #df = pd.read_csv(file_name, names=["x"])

    df_x = pd.read_csv(file_name, names = ["NodeId", "x", "y", "sourceNodeId", "BSNodeId", "is_misbehavior"])
    df_y = pd.read_csv(file_name, names = ["NodeId", "x", "y", "sourceNodeId", "BSNodeId", "is_misbehavior"])

    #sst = df["x"].copy()
    #print(sst.values)
    #for s in range(1,5):
    #    score = SSA_change_detection(series = sst["x"], standardize = False,
    #                                  window_size = 10, lag = 5, ns_h = s, ns_t =1)
    #    sst["s={}".format(s)] = score[0]
    #sst.plot(subplots = True)

    proposal_way = ProposalWay()
    lag = 10
    window_size = 20
    ns_t = 1

    #x座標のグラフ表示
    for s in range(1, 10):
        score_x = proposal_way.SSA_change_detection(series=df_x["x"], standardize=True, window_size=window_size,
                                                    lag=lag, ns_h=s, ns_t=ns_t)
        score_y = proposal_way.SSA_change_detection(series=df_y["y"], standardize=True, window_size=window_size,
                                                    lag=lag, ns_h=s, ns_t=ns_t)
        df_x["s={}".format(s)] = score_x[0]
        df_y["s={}".format(s)] = score_y[0]

    df_x.loc[:, ["x","s=1", "s=2", "s=3", "s=4", "s=5", "s=6"]].plot(subplots = True, title = "Normal Vehicle's Result", xlabel="t[s]")
    print_result(df_x.loc[:, ["x","s=1", "s=2", "s=3", "s=4", "s=5", "s=6"]], 0)

    # ファイルに保存
    plt.savefig("img_x.png")

    df_y.loc[:, ["y","s=1", "s=2", "s=3", "s=4", "s=5", "s=6"]].plot(subplots = True, title = "Normal Vehicle's Result", xlabel="t[s]")
    print_result(df_y.loc[:, ["y","s=1", "s=2", "s=3", "s=4", "s=5", "s=6"]], 1)

    # ファイルに保存
    plt.savefig("img_y.png")


    #plt.show()

    #系列相関
    #cols = df.columns
    #corr = pd.DataFrame(data={x: [df[x].autocorr(l) for l in range(24 * 7)] for x in cols})
    #corr[0:100].plot(kind='bar', subplots=True, figsize=(20, 5))


    #np.random.seed(42)
    #T = 24 * 7 * 4
    #pt = (150, 200, 250)
    #slope = .01
    #test = pd.DataFrame(data={'time': range(T),  # pd.date_range('2018-01-01', periods=T),
    #                          'change': [slope * (t - pt[0]) * (t in range(pt[0], pt[1])) +
    #                                     slope * (pt[1] - pt[0]) * (t in range(pt[1], pt[2])) +
    #                                     (-slope * (t - pt[2]) + slope * (pt[1] - pt[0])) * (
    #                                                 t in range(pt[2], pt[2] + (pt[1] - pt[0]))) for t in range(T)],
    #                          }).set_index('time')
    #test['+sin'] = test['change'] + 0.2 * np.sin(
    #    [2 * np.pi * t / 24.0 * np.pi for t in range(T)])
    #test['+sin+noise'] = test['+sin'] + np.random.normal(size=T, scale=.01)
    #test.plot(subplots=True, figsize=(20, test.shape[1] * 5))

    #test = test[['+sin+noise']]
    #cols = test.columns
    #corr = pd.DataFrame(data={x: [test[x].autocorr(l) for l in range(24 * 7)] for x in cols})
    #corr[0:100].plot(kind='bar', subplots=True, figsize=(20, 5))

    #sst = test.copy()
    #sst = sst[['+sin+noise']]
    #sst.rename(columns={'+sin+noise': 'original'}, inplace=True)
    #for s in range(1, 6):
    #    score = SSA_change_detection(series=sst['original'].values,
    #                   standardize=False,
    #                   window_size=8, lag=24, ns_h=s, ns_t=1)
    #    sst['s={}'.format(s)] = score[0]
    #sst.plot(subplots=True, figsize=(20, sst.shape[1] * 5))





