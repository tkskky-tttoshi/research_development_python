import csv

#result_sheet1.csvファイルを各ノード毎に変更

with open("./result_sheet1.csv") as csv_file:
  reader = csv.reader(csv_file)
  csv_file_array=[row for row in reader]

print(csv_file_array)
index = csv_file_array[1][0]
for i in range(len(csv_file_array)):
  index = csv_file_array[i][0]
  csv_file_name = "vehicle_"+index+".csv"
  with open("./data/"+csv_file_name, "a") as file:
      writer = csv.writer(file)
      writer.writerow(csv_file_array[i][:])




