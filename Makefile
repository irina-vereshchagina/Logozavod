# detatch run

run:
	nohup python3 bot.py > output.log 2>&1 &

stop:
	pkill -f python

mockon:
	export USE_PLACEHOLDER=true

mockoff:
	export USE_PLACEHOLDER=false

push:
	git add .
	git commit -m 'upd'
	git push

pull:
	git pull