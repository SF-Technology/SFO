#!/bin/bash
#add disk
#sh *.sh add /dev/sd*
#sh *.sh add all
result=true
sys_disk=`df -h|grep /boot |awk '{print $1}'|sed 's/[0-9]*//g'`
if [ "$1" == "add" -o "$1" == "ADD" -o "$1" == "Add" -o "$1" == "ADd" ];then
    if [[ "$2" == "" ]];then
        echo "target disk device is null"
    #add all disks
    elif [ "$2" == "all" -o "$2" == "All" -o "$2" == "ALL" ];then
        disks=($(fdisk -l |grep "Disk" |grep "/dev/sd*" |grep -v "$sys_disk[0-9]*"|awk '{print $2}'|tr ':\n' ' '|sed 's/ $/\n/'))
        label=`blkid |grep "LABEL"|awk '{print $2}'|cut -d \" -f 2|grep -oE "[0-9]*"|sort -n|sed -n '$p'`
        if [[ "$label" == "" ]];then
            let label=1
        else
            let label="$label"+1
        fi
        if [[ "$disks" != "" ]];then
            for disk in ${disks[@]}
            do
                lab=d"$label"
                fstype=`blkid |grep "$disk" |awk '{print $NF}' |sed s/TYPE=//g |sed s/\"//g`
                if [[ "$fstype" != "xfs" ]];then
                    if mkfs.xfs "$disk" -f -L "$lab">/dev/null;then
                        let label="$label"+1
                    fi
                else
                    islabel=`blkid |grep "$disk"|grep "LABEL"`
                    if [[ "$islabel" == "" ]];then
                        ismounted=`df -h |grep "$disk" |awk '{print $1}'`
                        if [[ "$ismounted" == "$disk" ]];then
                            continue
                        else
                            if xfs_admin -f -L "$lab" "$disk">/dev/null;then
                                let label="$label"+1
                            fi
                        fi
                    fi
                    ismounted=`df -h |grep "$disk" |awk '{print $1}'`
                    if [[ "$ismounted" == "$disk" ]];then
                        continue
                    else
                        lab=`blkid |grep "$disk"|awk '{print $2}'|cut -d \" -f 2`
                        if mkdir -p /srv/node/"$lab">/dev/null;then
                            if mount -t xfs -o noatime,nodiratime,nobarrier,logbufs=8 -L $lab /srv/node/$lab >/dev/null;then
                                echo -e "mount -t xfs -o noatime,nodiratime,nobarrier,logbufs=8 -L $lab /srv/node/$lab">>/etc/rc.local
                                if [[ $? -eq 0 ]];then
                                    if [[ "$result" && true ]];then
                                        result=true
                                    else
                                        result=false
                                    fi
                                else
                                    result=false
                                fi
                            fi
                        fi
                    fi
                fi
            done
            if "$result";then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        else
            echo "there is no disk available on this server,please check it manual"
        fi
    else
        isexist=`ls /dev|grep ${2##*/}`
        if [[ "$isexist" == "" ]];then
            echo "the target disk is not exist,please check your input value."
        else
            label=`blkid |grep "LABEL"|awk '{print $2}'|cut -d \" -f 2|grep -oE "[0-9]*"|sort -n|sed -n '$p'`
            if [[ "$label" == "" ]];then
                let label=1
            else
                let label="$label"+1
            fi
            lab=d"$label"
            fstype=`blkid |grep "$2" |awk '{print $NF}' |sed s/TYPE=//g |sed s/\"//g`
            if [[ "$fstype" != "xfs" ]];then
                mkfs.xfs "$2" -f -L "$lab">/dev/null
            else
                islabel=`blkid |grep "$2"|grep "LABEL"`
                if [[ "$islabel" == "" ]];then
                    ismounted=`df -h |grep "$2" |awk '{print $1}'`
                    if [[ "$ismounted" != "$2" ]];then
                        xfs_admin -f -L "$lab" "$2">/dev/null
                    fi
                fi
                ismounted=`df -h |grep "$disk" |awk '{print $1}'`
                if [[ "$ismounted" == "$disk" ]];then
                    continue
                else
                    lab=`blkid |grep "$2"|awk '{print $2}'|cut -d \" -f 2`
                    if mkdir -p /srv/node/"$lab">/dev/null;then
                        if mount -t xfs -o noatime,nodiratime,nobarrier,logbufs=8 -L $lab /srv/node/$lab>/dev/null;then
                            echo -e "mount -t xfs -o noatime,nodiratime,nobarrier,logbufs=8 -L $lab /srv/node/$lab">>/etc/rc.local
                            if [[ $? -eq 0 ]];then
                                echo "SUCCESS"
                            else
                                echo "$2" "Failed"
                            fi
                        fi
                    fi
                fi
            fi
        fi
    fi
#delete disk
#sh *.sh del /dev/sd*
#sh *.sh del all
elif [ "$1" == "delete" -o "$1" == "del" -o "$1" == "DETELE" -o "$1" == "DEL" -o "$1" == "Del" ];then
    if [[ "$2" == "" ]];then
        echo "target disk device is null"
    #delete all disks
    elif [ "$2" == "all" -o "$2" == "All" -o "$2" == "ALL" ];then
        disks=($(fdisk -l |grep "Disk" |grep "/dev/sd*" |grep -v "$sys_disk[0-9]*"|awk '{print $2}'|tr ':\n' ' '|sed 's/ $/\n/'))
        label=`blkid |grep "LABEL"|awk '{print $2}'|cut -d \" -f 2|grep -oE "[0-9]*"|sort -n|sed -n '$p'`
        if [[ "$label" == "" ]];then
            echo "no disk label found"
        elif [[ "$label" -ge 0 ]];then
            for i in $(seq 1 "$label")
            do
                mount_dir=/srv/node/d"$i"
                if [[ "$mount_dir" == "" ]];then
                    continue
                fi
                dev_name=`df -h |grep "$mount_dir" |awk '{print $1}'`
                lab=`blkid |grep "$dev_name"|awk '{print $2}'|cut -d \" -f 2`
                if [[ "$dev_name" != "" ]];then
                    if umount "$mount_dir">/dev/null;then
                        #delete from rc.local
                        if sed -i /"$lab"/d /etc/rc.local>/dev/null;then
                            if mkfs.xfs "$dev_name"  -f>/dev/null;then
                                if [[ "$result" && true ]];then
                                    result=true
                                else
                                    result=false
                                fi
                            else
                                result=false
                            fi
                        fi
                    fi
                fi
            done
            if "$result";then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        fi
    else
        isexist=`ls /dev|grep ${2##*/}`
        if [[ "$isexist" == "" ]];then
            echo "the target disk is not exist,please check your input value."
        else
            label=`blkid |grep "LABEL"|awk '{print $2}'|cut -d \" -f 2|grep -oE "[0-9]*"|sort -n|sed -n '$p'`
            if [[ "$label" == "" ]];then
                echo "no disk label found"
            elif [[ "$label" -ge 0 ]];then
                mount_dir=`df -h |grep "$2" |awk '{print $NF}'`
                if [[ "$mount_dir" == "" ]];then
                    echo "$2" "unmounted"
                else
                    dev_name=`df -h |grep "$mount_dir" |awk '{print $1}'`
                    lab=`blkid |grep "$dev_name"|awk '{print $2}'|cut -d \" -f 2`
                    if [[ "$dev_name" != "" ]];then
                        if  umount "$mount_dir">/dev/null;then
                            #delete from rc.local
                            if sed -i /"$lab"/d /etc/rc.local>/dev/null;then
                                if mkfs.xfs "$dev_name" -f>/dev/null;then
                                    echo "SUCCESS"
                                else
                                    echo "Format Failed"
                                fi
                            else
                                echo "$2" "Delete failed"
                            fi
                        else
                            echo "$2" "unmount failed"
                        fi
                    else
                        echo "$2" "not exist"
                    fi
                fi
            fi
        fi
    fi
else
    echo "operation input error,you can input 'add|ADD|Add|ADd|delete|del|DETELE|DEL|Del' as operation type"
fi