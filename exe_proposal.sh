#!/usr/bin/zsh

#第一引数にファイル名を使命 must
#第二引数にフォルダ名 e.g. data_12からなら12

for var in `seq 802 819`
do
	echo $var
	if [ $# -eq 1 ]; then
		python3 ./proposal.py $var
		mkdir ./Result/result_$var
		mv proposal_result_x.csv ./Result/result_$var/result_x.csv
		mv proposal_result_y.csv ./Result/result_$var/result_y.csv
		mv img_x.png ./Result/result_$var/result_x.png
		mv img_y.png ./Result/result_$var/result_y.png
	elif [ $# -eq 2 ]; then
		python3 ./proposal.py $var
		mkdir ./Result/result_${var}_$2
		mv proposal_result_x.csv ./Result/result_${var}_$2/vehicle_${var}_x_$2.csv
		mv img_x.png ./Result/result_${var}_$2/vehicle_${var}_x_$2.png
		mv proposal_result_y.csv ./Result/result_${var}_$2/vehicle_${var}_y_$2.csv
		mv img_y.png ./Result/result_${var}_$2/vehicle_${var}_y_$2.png
	else
		echo "Need Argumen"
	fi

done

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
