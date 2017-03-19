#!/usr/bin/env bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games
cd /home/u231/spider
for spider in guangxidj nmgdj ningxiadj xinjiangdj xizangdj
do
    if [ ! -e dj_log ]
    then
        mkdir dj_log
    fi
    nohup scrapy crawl $spider --logfile=dj_log/$spider.log &
    #pid=`ps -ef | grep $spider1.log | grep -v grep | awk '{print $2}'`
    #wait $pid
done
