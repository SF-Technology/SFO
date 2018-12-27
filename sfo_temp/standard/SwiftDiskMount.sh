#!/bin/bash -
for i in $(blkid|grep '/dev/sd*'|grep -v 'sda'|awk '{match($0,/LABEL=\"(d[0-9]+)\"/,a);print a[1]}')
do
    mount -t xfs -o noatime,nodiratime,nobarrier,logbufs=8 -L $i /srv/node/$i >/dev/null 2>&1
done

exit 0
