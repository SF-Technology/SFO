#!/bin/bash
#sh *.sh [account|container|object] [create|add|rebalance]  ... [file path]
param=$#
lastargs=${!param}
result=true
if [ "$1" == "account.builder" -o "$1" == "account" -o "$1" == "Account" -o "$1" == "ACCOUNT" ];then
    #create ring
    if [ "$2" == "create" -o "$2" == "Create" -o "$2" == "CREATE" ];then
        if [ "$3" -gt 0 -a "$4" -gt 0 -a "$5" -gt 0 ];then
            if swift-ring-builder "$lastargs" create  "$3"  "$4"  "$5" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        else
            echo "please input number for param3 param4 param5"
        fi
    #add disk to ring
    elif [ "$2" == "add" -o "$2" == "Add" -o "$2" == "ADD" ];then
        if [[ "$#" -eq 9 ]];then
            if swift-ring-builder "$lastargs" add --region "$3" --zone "$4" --ip "$5" --port "$6" --device "$7" --weight "$8" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        elif [[ "$#" -eq 11 ]];then
            if swift-ring-builder "$lastargs" add --region "$3" --zone "$4" --ip "$5" --port "$6"  --replication-ip "$7" --replication-port "$8" --device "$9" --weight "${10}" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        else
            echo "the number of params is not supported"
        fi
    #remove disk from ring immediately
    elif [ "$2" == "remove" -o "$2" == "Remove" -o "$2" == "REMOVE" ];then
        if [[ "$3" == "" ]];then
            echo "please input the disk label you want to remove"
        elif [[ "$#" != 4 ]];then
            echo "for this operation,the number of params is not supported"
        else
            if swift-ring-builder "$lastargs" remove "$3" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        fi
    #remove disk from ring slowly
    elif [ "$2" == "set_weight" -o "$2" == "setweight" -o "$2" == "SetWeight" -o "$2" == "Set_Weight" ];then
        if [[ "$#" != 5 ]];then
            echo "for this operation,the number of  params is not supported"
        elif [[ "$3" == "" ]];then
            echo "please input the disk label you want to set weight."
        else
            if swift-ring-builder "$lastargs" set_weight "$3" "$4" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        fi
    elif [ "$2" == "rebalance" -o "$2" == "Rebalance" -o "$2" == "REBALANCE" ];then
        if swift-ring-builder "$lastargs" rebalance >/dev/null;then
            echo "SUCCESS"
        else
            echo "FAILED"
        fi
    else
        echo "the operation $2 is not supported"
    fi
elif [ "$1" == "container.builder" -o "$1" == "container" -o "$1" == "Container" -o "$1" == "CONTAINER" ];then
    #create ring
    if [ "$2" == "create" -o "$2" == "Create" -o "$2" == "CREATE" ];then
        if [ "$3" -gt 0 -a "$4" -gt 0 -a "$5" -gt 0 ];then
            if swift-ring-builder "$lastargs" create  "$3"  "$4"  "$5" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        else
            echo "please input number for param3 param4 param5"
        fi
    #add disk to ring
    elif [ "$2" == "add" -o "$2" == "Add" -o "$2" == "ADD" ];then
        if [[ "$#" -eq 9 ]];then
            if swift-ring-builder "$lastargs" add --region "$3" --zone "$4" --ip "$5" --port "$6" --device "$7" --weight "$8" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        elif [[ "$#" -eq 11 ]];then
            if swift-ring-builder "$lastargs" add --region "$3" --zone "$4" --ip "$5" --port "$6"  --replication-ip "$7" --replication-port "$8" --device "$9" --weight "${10}" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        else
            echo "the number of params is not supported"
        fi
    #remove disk from ring immediately
    elif [ "$2" == "remove" -o "$2" == "Remove" -o "$2" == "REMOVE" ];then
        if [[ "$3" == "" ]];then
            echo "please input the disk label you want to remove"
        elif [[ "$#" != 4 ]];then
            echo "for this operation,the number of params is not supported"
        else
            if swift-ring-builder "$lastargs" remove "$3" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        fi
    #remove disk from ring slowly
    elif [ "$2" == "set_weight" -o "$2" == "setweight" -o "$2" == "SetWeight" -o "$2" == "Set_Weight" ];then
        if [[ "$#" != 5 ]];then
            echo "for this operation,the number of  params is not supported"
        elif [[ "$3" == "" ]];then
            echo "please input the disk label you want to set weight."
        else
            if swift-ring-builder "$lastargs" set_weight "$3" "$4" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        fi
    elif [ "$2" == "rebalance" -o "$2" == "Rebalance" -o "$2" == "REBALANCE" ];then
        if swift-ring-builder "$lastargs" rebalance >/dev/null;then
            echo "SUCCESS"
        else
            echo "FAILED"
        fi
    else
        echo "the operation $2 is not supported"
    fi
elif [ "$1" == "object.builder" -o "$1" == "object" -o "$1" == "Object" -o "$1" == "OBJECT" ];then
    #create ring
    if [ "$2" == "create" -o "$2" == "Create" -o "$2" == "CREATE" ];then
        if [ "$3" -gt 0 -a "$4" -gt 0 -a "$5" -gt 0 ];then
            if swift-ring-builder "$lastargs" create  "$3"  "$4"  "$5" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        else
            echo "please input number for param3 param4 param5"
        fi
    #add disk to ring
    elif [ "$2" == "add" -o "$2" == "Add" -o "$2" == "ADD" ];then
        if [[ "$#" -eq 9 ]];then
            if swift-ring-builder "$lastargs" add --region "$3" --zone "$4" --ip "$5" --port "$6" --device "$7" --weight "$8" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        elif [[ "$#" -eq 11 ]];then
            if swift-ring-builder "$lastargs" add --region "$3" --zone "$4" --ip "$5" --port "$6"  --replication-ip "$7" --replication-port "$8" --device "$9" --weight "${10}" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        else
            echo "the number of params is not supported"
        fi
    #remove disk from ring immediately
    elif [ "$2" == "remove" -o "$2" == "Remove" -o "$2" == "REMOVE" ];then
        if [[ "$3" == "" ]];then
            echo "please input the disk label you want to remove"
        elif [[ "$#" != 4 ]];then
            echo "for this operation,the number of params is not supported"
        else
            if swift-ring-builder "$lastargs" remove "$3" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        fi
    #remove disk from ring slowly
    elif [ "$2" == "set_weight" -o "$2" == "setweight" -o "$2" == "SetWeight" -o "$2" == "Set_Weight" ];then
        if [[ "$#" != 5 ]];then
            echo "for this operation,the number of  params is not supported"
        elif [[ "$3" == "" ]];then
            echo "please input the disk label you want to set weight."
        else
            if swift-ring-builder "$lastargs" set_weight "$hostip\/$3" "$4" >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        fi
    elif [ "$2" == "rebalance" -o "$2" == "Rebalance" -o "$2" == "REBALANCE" ];then
        if swift-ring-builder "$lastargs" rebalance >/dev/null;then
            echo "SUCCESS"
        else
            echo "FAILED"
        fi
    else
        echo "the operation $2 is not supported!"
    fi
#sh *.sh [policy] [policy-id] [create|add|rebalance...] [file path1] [file path2]

elif [ "$1" == "policy" -o "$1" == "Policy" -o "$1" == "POLICY" ];then
    if [ "$2" == "" -o "$2" < 1 ];then
        echo "the input policy-id is not supported."
    elif cat "${@:$#-1:1}" |grep "storage-policy:$2" >/dev/null;then
        #create ring
        if [ "$3" == "create" -o "$3" == "Create" -o "$3" == "CREATE" ];then
            if [ "$4" -gt 0 -a "$5" -gt 0 -a "$6" -gt 0 ];then
                if swift-ring-builder "$lastargs" create  "$4"  "$5"  "$6" >/dev/null;then
                    echo "SUCCESS"
                else
                    echo "FAILED"
                fi
            else
                echo "please input number for param4 param5 param6"
            fi
        elif [ "$3" == "add" -o "$3" == "Add" -o "$3" == "ADD" ];then
            if [[ "$#" -eq 11 ]];then
                if swift-ring-builder "$lastargs" add --region "$4" --zone "$5" --ip "$6" --port "$7" --device "$8" --weight "$9" >/dev/null;then
                    echo "SUCCESS"
                else
                    echo "FAILED"
                fi
            elif [[ "$#" -eq 13 ]];then
                if swift-ring-builder "$lastargs" add --region "$4" --zone "$5" --ip "$6" --port "$7"  --replication-ip "$8" --replication-port "$9" --device "${10}" --weight "${11}" >/dev/null;then
                    echo "SUCCESS"
                else
                    echo "FAILED"
                fi
            else
                echo "the number of params is not supported"
            fi
        elif [ "$3" == "remove" -o "$3" == "Remove" -o "$3" == "REMOVE" ];then
            if [[ "$4" == "" ]];then
                echo "please input the disk label you want to remove"
            elif [[ "$#" != 6 ]];then
                echo "for this operation,the number of params is not supported"
            else
                if swift-ring-builder "$lastargs" remove "$3" >/dev/null;then
                    echo "SUCCESS"
                else
                    echo "FAILED"
                fi
            fi
        elif [ "$3" == "set_weight" -o "$3" == "Set_Weight" -o "$3" == "SET_WEIGHT" ];then
            if [[ "$#" != 7 ]];then
                echo "for this operation,the number of  params is not supported"
            elif [[ "$4" == "" ]];then
                echo "please input the disk label you want to set weight."
            else
                if swift-ring-builder "$lastargs" set_weight "$3" "$4" >/dev/null;then
                    echo "SUCCESS"
                else
                    echo "FAILED"
                fi
            fi
        elif [ "$3" == "rebalance" -o "$3" == "Rebalance" -o "$3" == "REBALANCE" ];then
            if swift-ring-builder "$lastargs" rebalance >/dev/null;then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        else
            echo "the operation is not supported."
        fi
    else
        echo "the input policy is not in the swift.conf,please check your input value."
    fi
else
    echo "the operate target $1 is not supported!"
fi