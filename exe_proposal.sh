#!/usr/bin/zsh

#vehicle_{}.csvのファイルをdata_for_proposalにコピペする
#引数にフォルダ名 e.g. data_12からなら12
#seq 800 819 は 800から819までの車両を読み取るため

if [ $# -eq 1 ]; then
	mkdir ./Result/$1

	for var in `seq 800 819`
	do
		echo $var
		python3 ./proposal.py $var
		mkdir ./Result/$1/result_${var}
		mv proposal_result_x.csv ./Result/$1/result_${var}/result_x_${var}.csv
		mv img_x.png ./Result/$1/result_${var}/vehicle_${var}_x.png
		mv proposal_result_y.csv ./Result/$1/result_${var}/result_${var}_y.csv
		mv img_y.png ./Result/$1/result_${var}/vehicle_${var}_y.png

	done

else
	echo "Need Argumen"
fi
#if [ $# -eq 1 ]; then
#	python3 ./proposal.py $1
#	mkdir ./Result/result_$1
#	mv proposal_result_x.csv ./Result/result_$1/result_x.csv
#	mv proposal_result_y.csv ./Result/result_$1/result_y.csv
#	mv img_x.png ./Result/result_$1/result_x.png
#	mv img_y.png ./Result/result_$1/result_y.png
#elif [ $# -eq 2 ]; then
#	python3 ./proposal.py $1
#	mkdir ./Result/result_$1_$2
#	mv proposal_result_x.csv ./Result/result_$1_$2/vehicle_$1_x_$2vehicles.csv
#	mv img_x.png ./Result/result_$1_$2/vehicle_$1_x_$2vehicles.png
#	mv proposal_result_y.csv ./Result/result_$1_$2/vehicle_$1_y_$2vehicles.csv
#	mv img_y.png ./Result/result_$1_$2/vehicle_$1_y_$2vehicles.png
#else
#	echo "Need Argumen"
#fi
