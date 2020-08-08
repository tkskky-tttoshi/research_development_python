import glob
import pandas as pd
import numpy as np

class FileOpperator:
    def __init__(self):
        #dataディレクトリにある全てのcsvファイル名，ファイル数を取得する
        #pandasのDataFrameを作成する
        self.files_names = self.get_files_names_from_data_folder()
        self.files_sizes = len(self.files_names)
        self.csv_dataframe = self.make_data_frame(self.files_names)

    def get_files_names_from_data_folder(self):
        files_names = []
        for file_name in glob.glob("./data/*.csv"):
            files_names.append(file_name)
        return files_names

    def make_data_frame(self, files_names):
        csv_dataframe = []
        for (file_name, i) in zip(files_names, range(len(files_names))):
            df = pd.read_csv(file_name,
                             names=["NodeId", "x", "y", "sourceNodeId", "BSNodeId", "is_misbehavior"], header=None)
            csv_dataframe.append(df)
        return csv_dataframe

class MisbehaviorVehiclePreviousDetector:
    V2V_DISTANCE = 300000
    ROAD_WIDTH = 30000
    V2V_DIRECT_DISTANCE = 800000
    def __init__(self, files_names, csv_dataframe):
        self.csv_dataframe = csv_dataframe
        self.files_names = files_names

    def search_vehicle(self, index, threshold_number_of_vehicle):
        #時刻indexでのなりすましを検知する
        #必要周辺車両台数はthreshold_number_of_vehicle

        misbehaviored_on_bs = 0
        misbehaviored_on_v2v = 0
        no_peripheral_vehicles = 0
        not_enough_vehicles = 0
        number_of_vehicles = len(self.files_names)

        recognized = 0
        not_recognized = 0
        print("")
        print("**********************************")

        for i in range(number_of_vehicles):
            
            my_sourceNodeId_array = self.get_source_nodeId_array_from_a_dataframe(i, index)
            my_position = self.get_position_from_a_dataframe(i, index)  #`.x`でxを抽出
            my_BS_nodeId = self.get_BS_nodeId_from_a_dataframe(i, index)
            
            print("============================")
            print("my_nodeid "+str(i))
            print("my_position "+str(my_position/1000))

            #なりすましの種類は2種類
            #1. BS 2.周辺車両の台数 3.周辺車両との位置比較

            #1. BS
            if(not self.the_vehicle_exists_within_BS(my_position, my_BS_nodeId)):
                print("index"+str(index))
                print("BSでのなりすましが行われています")
                misbehaviored_on_bs = misbehaviored_on_bs + 1
                #recognized = recognized + 1
                continue

            #新提案手法のため
            if(len(my_sourceNodeId_array) == 0):
                print("周辺車両が存在しません")
                no_peripheral_vehicles = no_peripheral_vehicles + 1
                continue

            #2. 周辺車両の台数
            #if(len(my_sourceNodeId_array) < threshold_number_of_vehicle):
            #    print("周辺車両台数がたりません")
            #    not_enough_vehicles = not_enough_vehicles + 1
            #    continue

            #3. 周辺車両との位置比較
            number_of_normal_vehicels = 0
            number_of_abnormal_vehicle = 0
            for my_sourceNodeId in my_sourceNodeId_array:
                print("--------------------")
                print("another_nodeId "+str(my_sourceNodeId))
                j = [j for j in range(number_of_vehicles)
                     if self.csv_dataframe[j].at[0, "NodeId"] == int(my_sourceNodeId)]
                another_nodeId_index = j[0]
                another_position = self.get_position_from_a_dataframe(another_nodeId_index, index)
                print("another_position "+str(another_position/1000))
                if(self.two_vehicles_exist_within_V2V_DISTANCE(my_position, another_position)):
                    print("True!!")
                    number_of_normal_vehicels = number_of_normal_vehicels + 1
                else:
                    number_of_abnormal_vehicle = number_of_abnormal_vehicle + 1
                    print("False...")

            if(number_of_normal_vehicels < threshold_number_of_vehicle):
                #number_of_normal_vehicles > number_of_abnormal_vehicel　とかも入れた方がいい気する
                misbehaviored_on_v2v = misbehaviored_on_v2v + 1
                if(self.is_a_misbehavior_vehicle(i)):
                    recognized = recognized + 1
                else:
                    not_recognized = not_recognized + 1



                #query('NodeId = {0}'.format(my_sourceNodeId_array[0])))]


            #for another_nodeId in my_sourceNodeId_array:
        print("")
        print("index "+str(index))

        print("周辺車両なし " + str(no_peripheral_vehicles))
        #print("周辺車両たりない " + str(not_enough_vehicles))

        print("Mis on BS " + str(misbehaviored_on_bs))
        print("Mis on V2V " + str(misbehaviored_on_v2v))

        print("recognized " + str(recognized))
        print("NOT recognized " + str(not_recognized))

        normal_vehicles = number_of_vehicles - misbehaviored_on_v2v - misbehaviored_on_bs
        result_data = [number_of_vehicles, normal_vehicles, misbehaviored_on_bs, no_peripheral_vehicles,
                       misbehaviored_on_v2v, recognized, not_recognized]
        return result_data

    #東さんの提案手法
    def previous_proposal_way(self):
        threshold_number_of_vehicle = 2
        result_datum = []
        for index in range(len(self.csv_dataframe[0])):
            result_datum.append(self.search_vehicle(index, threshold_number_of_vehicle))

        self.print_result_on_csv(result_datum)

    def print_result_on_csv(self, result_datum):
        df = pd.DataFrame(result_datum, columns=["車両数", "通常車両", "BSでのなりすまし車両数", "周辺車両が存在しない車両数",
                                                 "V2Vでのなりすまし車両数", "正しい認識数", "誤った認識数"])
        df.to_csv("previous_proposal_result.csv")

    def is_a_misbehavior_vehicle(self, file_number):
        return self.csv_dataframe[file_number].loc[0, "is_misbehavior"] == 1

    def get_nodeId_from_a_dataframe(self, file_number):
        return self.csv_dataframe[file_number].loc[0,"NodeId"]

    def the_vehicle_exists_within_BS(self, my_position, BS_nodeId):
        #BSの位置によってなりすましを検知
        if ( BS_nodeId == 900):
            #第2象限
            if(my_position.x <= 0 and my_position.y >= 0):
                return True
        elif( BS_nodeId == 901):
            #第3象限
            if(my_position.x < 0 and my_position.y < 0):
                return True
        elif( BS_nodeId == 902):
            #第4象限
            if(my_position.x > 0 and my_position.y < 0):
                return True
        elif( BS_nodeId == 903):
            #第1象限
            if(my_position.x > 0 and my_position.y > 0):
                return True
        return False

    def get_position_from_a_dataframe(self, file_number, index):
        return self.csv_dataframe[file_number].loc[index, "x":"y"]

    def get_source_nodeId_array_from_a_dataframe(self, file_number, index):
        source_nodeId = self.get_one_row_from_a_dataframe(file_number, index).sourceNodeId
        #周辺車両が存在しない場合
        if (type(source_nodeId) is float):
            return []
        #周辺車両が存在する場合
        source_nodeId_array = source_nodeId.split()
        return source_nodeId_array

    def get_BS_nodeId_from_a_dataframe(self, file_number, index):
        BS_nodeId = self.get_one_row_from_a_dataframe(file_number, index).BSNodeId
        return BS_nodeId

    def get_one_row_from_a_dataframe(self, file_number, index):
        return self.csv_dataframe[file_number].loc[index, :]

    def get_one_row_from_dataframes(self, index):
        one_row_from_dataframes=[]
        for i in range(len(self.files_names)):
            one_row_from_dataframes.append(self.get_one_row_from_a_dataframe(i, index))
        return one_row_from_dataframes

    def two_vehicles_exist_within_V2V_DISTANCE(self, my_position, another_position):
        if np.linalg.norm(my_position-another_position) < MisbehaviorVehiclePreviousDetector.V2V_DISTANCE:
            print("Detected Surround")
            print(np.linalg.norm(my_position-another_position)/1000)
            return True
        #マンハッタンの場合，以下を考慮してもいい
        #elif (my_position.x-another_position.x <= MisbehaviorVehiclePreviousDetector.ROAD_WIDTH) \
        #        and (np.abs(my_position.y-another_position.y) < MisbehaviorVehiclePreviousDetector.V2V_DIRECT_DISTANCE):
        #    #同一道路上の場合
        #    print("Detected Direct")
        #    print(np.linalg.norm(my_position-another_position)/1000)
        #    return True
        #elif (np.abs(my_position.y - another_position.y) <= MisbehaviorVehiclePreviousDetector.ROAD_WIDTH) \
        #        and (my_position.x - another_position.x < MisbehaviorVehiclePreviousDetector.V2V_DIRECT_DISTANCE):
        #    #同一道路上の場合
        #    print("Detected Direct")
        #    print(np.linalg.norm(my_position-another_position)/1000)
        #    return True
        else:
            print(np.linalg.norm(my_position-another_position)/1000)
            return False



if __name__ == "__main__":
    fileoperator = FileOpperator()
    files_names = fileoperator.files_names
    csv_dataframe = fileoperator.csv_dataframe
    #print(fileoperator.csv_dataframe[0])

    previous_detector = MisbehaviorVehiclePreviousDetector(files_names, csv_dataframe)

    #print(previous_detector.get_one_row_from_dataframes(0))
    #print("split")
    #print(previous_detector.get_source_nodeId_array_from_a_dataframe(0, 0))
    #print(previous_detector.get_position_from_a_dataframe(0,0))

    print(previous_detector.files_names)
    #previous_detector.search_vehicle(5,1)
    #previous_detector.search_vehicle(6,2)
    previous_detector.previous_proposal_way()






