#!/bin/bash
#install software packages
result=true
if [ "$1" == "install" -o "$1" == "Install" -o "$1" == "INSTALL" ];then
    if [ "$2" == "all" -o "$2" == "All" -o "$2" == "ALL" ];then
        #install xfsprogs
        if rpm -qa|grep xfsprogs || yum -y install xfsprogs >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "install xfsprogs failed"
            result=false
        fi

        #install rsync
        if rpm -qa|grep rsync || yum -y install rsync >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "install rsync failed"
            result=false
        fi

        #install account server
        if rpm -qa|grep openstack-swift-account || yum install -y openstack-swift-account >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "install account server failed"
            result=false
        fi
        if mkdir -p /etc/swift/account-server >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "directory create failed"
            result=false
        fi
        if ls /etc/swift/ |grep account-server.conf >/dev/null;then
            if mv /etc/swift/account-server.conf  /etc/swift/account-server >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "move file failed"
                result=false
            fi
        fi
        touch /etc/swift/account-server/account-rep-server.conf
        echo "#please add your account replication config to this file">>/etc/swift/account-server/account-rep-server.conf

        #install container server
        if rpm -qa|grep openstack-swift-container || yum -y install openstack-swift-container >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "install container server failed"
            result=false
        fi
        if mkdir -p /etc/swift/container-server >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "directory create failed"
            result=false
        fi
        if ls /etc/swift/ |grep container-server.conf >/dev/null;then
            if mv /etc/swift/container-server.conf  /etc/swift/container-server >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "move file failed"
                result=false
            fi
        fi
        touch /etc/swift/container-server/container-rep-server.conf
        echo "#please add your container replication config to this file">>/etc/swift/container-server/container-rep-server.conf

        #install object server
        if rpm -qa|grep openstack-swift-object || yum -y install openstack-swift-object >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "install object server failed"
            result=false
        fi
        if mkdir -p /etc/swift/object-server >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "directory create failed"
            result=false
        fi
        if ls /etc/swift/ |grep object-server.conf >/dev/null;then
            if mv /etc/swift/object-server.conf /etc/swift/object-server >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "move file failed"
                result=false
            fi
        fi
        touch /etc/swift/object-server/object-rep-server.conf
        echo "#please add your object replication config to this file">>/etc/swift/object-server/object-rep-server.conf

        #install proxy server
        if rpm -qa|grep openstack-swift-proxy || yum -y install openstack-swift-proxy >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "install proxy server failed"
            result=false
        fi
        mkdir -p /srv/node >/dev/null
        #Directory authorization
        if chown -R swift:swift /srv/node >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            result=false
        fi
        if mkdir -p /var/cache/swift >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            echo "directory create failed"
            result=false
        fi
        if chown -R root:swift /var/cache/swift >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            result=false
        fi
        if chmod -R 775 /var/cache/swift >/dev/null;then
            if "$result" && true;then
                result=true
            else
                result=false
            fi
        else
            result=false
        fi

    else
        if [ "$2" == "account" -o "$2" == "Account" -o "$2" == "ACCOUNT" ];then
            #install xfsprogs
            if rpm -qa|grep xfsprogs || yum -y install xfsprogs >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install xfsprogs failed"
                result=false
            fi

            #install rsync
            if rpm -qa|grep rsync || yum -y install rsync >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install rsync failed"
                result=false
            fi

            if rpm -qa|grep openstack-swift-account || yum install -y openstack-swift-account >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install account server failed"
                result=false
            fi
            if mkdir -p /etc/swift/account-server >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if ls /etc/swift/ |grep account-server.conf >/dev/null;then
                if mv /etc/swift/account-server.conf  /etc/swift/account-server >/dev/null;then
                    if "$result" && true;then
                        result=true
                    else
                        result=false
                    fi
                else
                    result=false
                fi
            fi
            touch /etc/swift/account-server/account-rep-server.conf
            echo "#please add your account replication config to this file">>/etc/swift/account-server/account-rep-server.conf
            mkdir -p /srv/node >/dev/null
            #Directory authorization
            if chown -R swift:swift /srv/node >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if mkdir -p /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if chown -R root:swift /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if chmod -R 775 /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
        elif [ "$2" == "container" -o "$2" == "Container" -o "$2" == "CONTAINER" ];then
            #install xfsprogs
            if rpm -qa|grep xfsprogs || yum -y install xfsprogs >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install xfsprogs failed"
                result=false
            fi

            #install rsync
            if rpm -qa|grep rsync || yum -y install rsync >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install rsync failed"
                result=false
            fi

            if rpm -qa|grep openstack-swift-container || yum -y install openstack-swift-container >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install container server failed"
                result=false
            fi
            if mkdir -p /etc/swift/container-server >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if ls /etc/swift/ |grep container-server.conf >/dev/null;then
                if mv /etc/swift/container-server.conf  /etc/swift/container-server >/dev/null;then
                    if "$result" && true;then
                        result=true
                    else
                        result=false
                    fi
                else
                    result=false
                fi
            fi
            touch /etc/swift/container-server/container-rep-server.conf
            echo "#please add your container replication config to this file">>/etc/swift/container-server/container-rep-server.conf
            mkdir -p /srv/node >/dev/null
            #Directory authorization
            if chown -R swift:swift /srv/node >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if mkdir -p /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if chown -R root:swift /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if chmod -R 775 /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
        elif [ "$2" == "object" -o "$2" == "Object" -o "$2" == "OBJECT" ];then
            #install xfsprogs
            if rpm -qa|grep xfsprogs || yum -y install xfsprogs >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install xfsprogs failed"
                result=false
            fi

            #install rsync
            if rpm -qa|grep rsync || yum -y install rsync >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install rsync failed"
                result=false
            fi

            if rpm -qa|grep openstack-swift-object || yum -y install openstack-swift-object >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install object server failed"
                result=false
            fi
            if mkdir -p /etc/swift/object-server >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if ls /etc/swift/ |grep object-server.conf >/dev/null;then
                if mv /etc/swift/object-server.conf /etc/swift/object-server >/dev/null;then
                    if "$result" && true;then
                        result=true
                    else
                        result=false
                    fi
                else
                    result=false
                fi
            fi
            touch /etc/swift/object-server/object-rep-server.conf
            echo "#please add your object replication config to this file">>/etc/swift/object-server/object-rep-server.conf
            mkdir -p /srv/node >/dev/null
            #Directory authorization
            if chown -R swift:swift /srv/node >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if mkdir -p /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if chown -R root:swift /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if chmod -R 775 /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
        elif [ "$2" == "proxy" -o "$2" == "Proxy" -o "$2" == "PROXY" ];then
            #install proxy server
            if rpm -qa|grep openstack-swift-proxy || yum -y install openstack-swift-proxy >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install proxy server failed"
                result=false
            fi
            mkdir -p /srv/node >/dev/null
            #Directory authorization
            if chown -R swift:swift /srv/node >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if mkdir -p /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if chown -R root:swift /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
            if chmod -R 775 /var/cache/swift >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                result=false
            fi
        else
            if rpm -qa|grep "$2" || yum -y install "$2" >/dev/null;then
                if "$result" && true;then
                    result=true
                else
                    result=false
                fi
            else
                echo "install $2 failed"
                result=false
            fi
        fi
    fi
elif [ "$1" == "uninstall" -o "$1" == "Uninstall" -o "$1" == "UNINSTALL" ];then
    result=false
    echo "No support for software unload"
else
    result=false
    echo "please use this script like sh [path]softmanage.sh [install|uninstall] [all|proxy|account|container|object|softwarename]"
fi
if "$result";then
    echo "SUCCESS"
else
    echo "FAILED"
fi