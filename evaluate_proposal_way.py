import pandas as pd
import glob
import csv

#def get_csv_file():
#    file_name = "./Result/result_800_100vehicles/vehicle_800_x_100vehicles.csv"
#    df = pd.read_csv(file_name)
#    return df

#def split_csv_data(df):
#    size = 60
#    list_of_dfs = [df.loc[i:i+size-1, :] for i in range(0, len(df), size)]
#    print(len(list_of_dfs))
#    return list_of_dfs

def get_files_names_from_evaluation_folder():
    files_names = []
    for file_name in glob.glob("./Result/evaluation_folder/*.csv"):
        files_names.append(file_name)
    return files_names

def evaluate_datum_for_all_files(files_names):
    # 閾値を0.005
    threshold_array = [0.02, 0.01, 0.005, 0.0025, 0.001]
    for threshold in threshold_array:
        result_array=[]
        data_frame = pd.DataFrame([])
        for (file_name, i) in zip(files_names, range(len(files_names))):
            df = pd.read_csv(file_name)
            result, series_data = evaluate_data_for_file(df, threshold)

            data_frame[file_name.split("/")[-1]] = series_data

            result_dictionary = {"ファイル名":file_name, "なりすましと判断された数":result[0],
                                 "正しい認識数":result[1], "誤った認識数":result[2]}
            result_array.append(result_dictionary)
        data_frame.to_csv("./Result/evaluation_folder/series_{}.csv".format(threshold), mode='a')
        print_result(result_array, threshold)

def evaluate_data_for_file(df, threshold):

    #主成分のみ取得
    anomaly_values_array = df["s=1"]
    times_of_anomaly = 0
    correct_recognized = 0
    incorrect_recognized = 0
    series_data=[]
    for (anomaly_value, i) in zip(anomaly_values_array, range(len(anomaly_values_array))):
        if (i >= 120 and i < 180) or (i >= 420 and i < 480):
            if ( threshold <= anomaly_value):
                series_data.append(1)
            else:
                series_data.append(0)

        if (threshold <= anomaly_value):
            times_of_anomaly = times_of_anomaly + 1
            #なりすましの時間は120~180，420~480と決めている
        if (i >= 120 and i < 180) or (i >= 420 and i < 480):
            correct_recognized = correct_recognized + 1
        else:
            incorrect_recognized = incorrect_recognized + 1

    #[なりすまし数，正解数, 誤認識数]
    return [times_of_anomaly, correct_recognized, incorrect_recognized], series_data


def print_result(result_array, threshold):
    csv_file = "./Result/evaluation_folder/evaluation_{}.csv".format(threshold)

    with open(csv_file, "a") as file:
        writer = csv.DictWriter(file, fieldnames=["ファイル名", "なりすましと判断された数", "正しい認識数", "誤った認識数"])
        writer.writeheader()
        for result in result_array:
            writer.writerow(result)

if __name__ == "__main__":
    #df = get_csv_file()
    evaluate_datum_for_all_files(get_files_names_from_evaluation_folder())
