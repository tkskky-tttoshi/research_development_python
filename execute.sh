#!/usr/bin/zsh

#引数に車両数を入れることによってデータの管理を行う
mkdir data_$1
if [ -e ./result_sheet1.csv ]; then
  python3 ./result_sheet1_arranger.py
else
  mv ./data_$1/result_sheet1.csv ./result_sheet1.csv
  python3 ./result_sheet1_arranger.py
fi

mv ./result_sheet1.csv ./data_$1/result_sheet1.csv
wait

python3 ./azuma_proposal.py
mv ./data/* ./data_$1/
mv ./previous_proposal_result.csv ./data_$1/previous_proposal_result.csv
