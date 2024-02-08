



GW=10.1.23.1
IF=wlan0


while [ 1 ]
do

	ping $GW -c 1 >/dev/null || iwlist $IF scanning >/dev/null


	sleep 5

done

