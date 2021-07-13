#!/bin/bash 

case $1 in
	"start" )
        	echo "uruchomienie serwera"
		nohup python3 -u /home/debian/appMTS.py >> /home/debian/appMTS.log 2>&1&
		;;
	"stop" )
		echo "zatrzymanie serwera"
		/usr/bin/pkill -f appMTS.py
		;;
	"restart" )
		echo "restart serwera"
  	    /usr/bin/pkill -f appMTS.py
  	   	nohup python3 -u /home/debian/appMTS.py >> /home/debian/appMTS.log 2>&1&
		;;
	*)
		echo "app.sh [start|stop|restart]"
		exit 1
esac
