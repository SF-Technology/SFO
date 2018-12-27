#!/bin/bash
if [ "$2" == "account" -o "$2" == "container" -o "$2" == "object" -o "$2" == "proxy" ];then
    srvs=`ls /usr/lib/systemd/system/ |grep -E "openstack-swift-$2" |grep -v '@'`
else
    srvs=`ls /usr/lib/systemd/system/ |grep -E "$2" |grep -v '@'|grep "service"`
fi
if [ "$srvs" ];then
    srv=$srvs
    OLD_IFS="$IFS"
    IFS=" "
    arr=($srv)
    IFS="$OLD_IFS"
    for s in ${arr[@]}
    do
       srvstat=`systemctl "$1" "$s"|grep "Active"`
       if [ "$1" == "status" ];then
           echo "$s:$srvstat"
       else
           srvstat=`systemctl status $s|grep "Active"`
           echo "$s:$srvstat"
       fi
    done
else
    echo "Operation failed"
fi
