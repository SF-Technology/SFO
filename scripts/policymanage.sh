#!/bin/bash
#sh *.sh [add] [NO.] [name] [deprecated]  [policy_type] [file path]
#sh *.sh [delete] [NO.] [file path]
#sh *.sh [check] [NO.] [file path]
#NO.-policy number.
#name-polixy name,just for human read.
#deprecated-the policy is or not used
#policy_type-replication or erasure_coding
param=$#
lastargs=${!param}
if [ "$1" == "add" -o "$1" == "Add" -o "$1" == "ADD" ];then
    if [[ "$2" -eq 0 ]];then
        echo "can not ceate policy-0,please change your input value."
    elif [[ "$2" -gt 0 ]];then
        if cat "$lastargs" |grep "storage-policy:$2" >/dev/null;then
            echo "the policy NO. is exist,please input another one."
        else
            if echo "[storage-policy:$2]">>"$lastargs";then
                if echo "name = $3">>"$lastargs";then
                    if echo "deprecated = $4">>"$lastargs";then
                        if echo "policy_type = $5">>"$lastargs";then
                            echo "SUCCESS"
                        else
                            echo "create policy failed."
                        fi
                    else
                        echo "create policy failed."
                    fi
                else
                    echo "create policy failed."
                fi
            else
                echo "create policy failed."
            fi
        fi
    else
        echo "you should input a number bigger than 0 "
    fi
#delete the policy by modify the "deprecated = no" to "deprecated = yes"
elif [ "$1" == "del" -o "$1" == "delete" -o "$1" == "Delete"  -o "$1" == "DELETE" ];then
    row=`awk '/policy:'''$2'''/{while(getline)if(($0!~/policy:/) || ($0!~/\$/))  print NR$0;else exit}' "$lastargs"|egrep "deprecated"|grep -o "[0-9]\+"`
    if [[ "$row" > 0 ]];then
        if sed -i ''''$row'''s/no/yes/' "$lastargs" >/dev/null;then
            echo "SUCCESS"
        else
            echo "FAILED"
        fi
    else
        echo "no deprecated policy was found."
    fi
#check the policy by policy-index
elif [ "$1" == "check" -o "$1" == "Check" -o "$1" == "CHECK" ];then
    result=`awk '/policy:'''$2'''/{while(getline)if(($0!~/policy:/) || ($0!~/\$/))  print;else exit}' "$lastargs"`
    echo "$result"
else
    echo "your operation is not supported!"
fi