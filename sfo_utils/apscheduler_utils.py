#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2007 Free Software Foundation, Inc. <https://fsf.org/>
#
# Licensed under the GNU General Public License, version 3 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://jxself.org/translations/gpl-3.zh.shtml
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import re
import os
import json
import sys
import inspect
import time
import datetime
import logging
import requests
from multiprocessing import RLock
from sfo_server import getLogger, access_logger
from sfo_common.config_parser import Config
from sfo_server.build_config_template import create_new_config_file
from sfo_server.models import (SfoServerAccessLog,
                               SfoTasksListMethod,
                               SfoManagerTaskLogMethod,
                               db,
                               SfoClusterNodesMethod,
                               SfoCofigureMethod,
                               SfoHostInfoMethod,
                               )
from sfo_server.resource.common import timestamp_format, weight_con, reverse_unit
from sfo_server.manager_class import DiskOperation, SwiftServiceOperation, RingManager, PolicyManager, FileManager, ClusterManager, ServiceOperation
from apscheduler.schedulers import SchedulerAlreadyRunningError, SchedulerNotRunningError
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

config = Config()
rlock = RLock()

# [apscheduler]
JOBSTORES_SQL_USER = config.mysql_user
JOBSTORES_SQL_PASSWORD = config.mysql_passwd
JOBSTORES_SQL_HOST = config.mysql_host
JOBSTORES_SQL_PORT = config.mysql_port
JOBSTORES_SQL_DBNAME = config.mysql_dbname
THREAD_POOL_EXECUTER_NUM = 1
JOB_COALESCE = False
JOB_MAX_INSTANCE = 100

apsjob_logger = getLogger('apscheduler.executors.default')

jobstores = {
    'default': SQLAlchemyJobStore(url='mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8'% (JOBSTORES_SQL_USER,
                                                                                      JOBSTORES_SQL_PASSWORD,
                                                                                      JOBSTORES_SQL_HOST,
                                                                                      JOBSTORES_SQL_PORT,
                                                                                      JOBSTORES_SQL_DBNAME),
                                  pickle_protocol=0,
                                  engine_options={"pool_recycle": 5})
}


jobstores_gevent = {
    'default': SQLAlchemyJobStore(url='mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8'% (JOBSTORES_SQL_USER,
                                                                                      JOBSTORES_SQL_PASSWORD,
                                                                                      JOBSTORES_SQL_HOST,
                                                                                      JOBSTORES_SQL_PORT,
                                                                                      JOBSTORES_SQL_DBNAME),
                                  tablename='gevent_apscheduler_jobs',
                                  pickle_protocol=0,
                                  engine_options={"pool_recycle": 5})
}


executors = {
    'default': ThreadPoolExecutor(THREAD_POOL_EXECUTER_NUM),
}

gevent_executors = {
    'default': ThreadPoolExecutor(THREAD_POOL_EXECUTER_NUM)
}

job_defaults = {
    'coalesce': JOB_COALESCE,
    'max_instances': JOB_MAX_INSTANCE,
    "misfire_grace_time": 500
}


def take_tasklog_notes(taskid, excute_description, message):
    current_time = time.time()
    manager_log = SfoManagerTaskLogMethod.create_manager_task_log(taskid, message,
                                                                  excute_description,
                                                                  timestamp_format(current_time))
    sfo_task = SfoTasksListMethod.query_tasks_by_guid(taskid)
    if sfo_task:
        ending_flag = int(sfo_task.service_task_ending_flag) if sfo_task.service_task_ending_flag else 0
        ending_flag += 1
        sfo_task.service_task_ending_flag = str(ending_flag)
        sfo_task.task_end_time = timestamp_format(current_time)
        db.session.add(sfo_task)
    db.session.add(manager_log)
    db.session.commit()


def add_disk(host_ip, inet_host_ip, host_name, disk_name='', taskid=None):
    disk_op = DiskOperation(host_ip, inet_host_ip)
    try:
        disk_name = disk_name if disk_name else 'all'
        content = disk_op.add_disk(disk_name)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'mount %s %s disk' % (host_name, disk_name), message)


def delete_disk(host_ip,inet_host_ip, host_name, disk_name='', taskid=None):
    disk_op = DiskOperation(host_ip, inet_host_ip)
    try:
        disk_name = disk_name if disk_name else 'all'
        content = disk_op.delete_disk(disk_name)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'unmount %s %s disk' % (host_name, disk_name), message)


def add_service(host, service, taskid=None):
    swift_op = SwiftServiceOperation(host.node_inet_ip)
    try:
        content = swift_op.install_service(service)
        message = content
    except Exception, error:
        message = str(error)
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'install %s %s' % (host.node_host_name, service), message)


def create_ring(cluster_name, ring_name, part_power, replicas, min_part_hours, policy_num, taskid=None):
    rm = RingManager(cluster_name)
    try:
        if policy_num:
            content = rm.create(part_power=part_power,
                                replicas=replicas,
                                min_part_hours=min_part_hours,
                                policy=True,
                                policy_num=policy_num)

        else:
            ring_name = ring_name.split('.')[0]
            content = rm.create(ring_name=ring_name,
                                part_power=part_power,
                                replicas=replicas,
                                min_part_hours=min_part_hours)

        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid,  'create %s.ring.gz' % ring_name, message)


def add_disk_2_ring(ring_name, region,
                    zone, ip, port, disk_device,
                    weight, replication_ip='', replication_port='', policy_num='', cluster_name='', taskid=None):

    rm = RingManager(cluster_name)
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.add_disk_2_ring(ring_name=ring_name,
                                         region=region,
                                         zone=zone,
                                         ip=ip,
                                         port=port,
                                         disk_device=disk_device,
                                         weight=weight,
                                         replication_ip=replication_ip,
                                         replication_port=replication_port)
        else:
            content = rm.add_disk_2_ring(region=region,
                                         zone=zone,
                                         ip=ip,
                                         port=port,
                                         disk_device=disk_device,
                                         weight=weight,
                                         replication_ip=replication_ip,
                                         replication_port=replication_port,
                                         policy=True,
                                         policy_num=policy_num)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid,   'add %s %s disk to %s.ring.gz' % (ip, disk_device, ring_name), message)


def remove_disk_immediately(ring_name, disk_device, ip, port, policy_num, cluster_name, taskid=None):
    rm = RingManager(cluster_name)
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.remove_disk_immediately(ring_name=ring_name,
                                                 disk_device=disk_device,
                                                 ip=ip,
                                                 port=port)
        else:
            content = rm.remove_disk_immediately(disk_device=disk_device,
                                                 ip=ip,
                                                 port=port,
                                                 policy=True,
                                                 policy_num=policy_num)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'remove %s %s disk from %s.ring.gz immediately' % (ip, disk_device, ring_name), message)


def remove_disk_slowly(ring_name, disk_device, weight, ip, port, policy_num, cluster_name, taskid=None):
    rm = RingManager(cluster_name)
    #需要更改
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.remove_disk_slowly(ring_name=ring_name,
                                            weight=weight,
                                            disk_device=disk_device,
                                            ip=ip,
                                            port=port)
        else:
            content = rm.remove_disk_slowly(weight=weight,
                                            policy=True,
                                            disk_device=disk_device,
                                            ip=ip,
                                            port=port,
                                            policy_num=policy_num)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'remove %s %s disk from %s.ring.gz slowly' % (ip, disk_device, ring_name), message)


def set_weight(ring_name, disk_device, weight, ip, port, policy_num, cluster_name, taskid=None):
    rm = RingManager(cluster_name)
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.set_weight(ring_name=ring_name,
                                    weight=weight,
                                    disk_device=disk_device,
                                    ip=ip,
                                    port=port)
        else:
            content = rm.set_weight(policy_num=policy_num,
                                    weight=weight,
                                    disk_device=disk_device,
                                    ip=ip,
                                    port=port,
                                    policy=True)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'set weight=%s %s.ring.gz' % (weight, ring_name), message)


def rebalance(ring_name, policy_num, cluster_name, taskid=None):
    rm = RingManager(cluster_name)
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.rebalance(ring_name=ring_name)
        else:
            content = rm.rebalance(policy_num=policy_num,
                                   policy=True)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'rebalance %s.ring.gz' % ring_name, message)


def give_away_ring(ring_name, cluster_name, taskid=None):
    rm = RingManager(cluster_name)
    try:
        content = rm.give_away_ring(cluster_name=cluster_name,
                                    ring_file=ring_name)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid,  'give away %s.ring.gz to %s nodes' % (ring_name, cluster_name), message)


def add_policy(cluster_name,
               policy_num,
               policy_name,
               deprecated,
               policy_type,
               taskid=None):

    pm = PolicyManager(cluster_name)
    try:
        content = pm.add(num=policy_num,
                         name=policy_name,
                         deprecated=deprecated,
                         policy_type=policy_type)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid,  'add %s policy' % policy_num, message)


def del_policy(cluster_name, policy_num, taskid=None):
    pm = PolicyManager(cluster_name)
    try:
        content = pm.deprecate(num=policy_num)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'del %s policy' % policy_num, message)


def give_away_file_to_proxy(target_file, cluster_name, taskid=None):
    """
    主要用于分发 passwd文件给proxy节点
    :param target_file:
    :param cluster_name:
    :param taskid:
    :return:
    """
    fm = FileManager()
    try:
        content = fm.give_away_file_to_proxy(cluster_name, target_file)
        message = content
    except Exception, error:
        message = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'give away %s file to %s cluster' % (target_file, cluster_name), message)


def give_away_passwd_to_proxy(target_file, cluster_name, referer, syscode, taskid=None):
    """
    主要用于分发 passwd文件给proxy节点
    :param target_file:
    :param cluster_name:
    :param taskid:
    :return:
    """
    fm = FileManager()
    message_js = {
        "source": referer,
        "syscode": syscode,
    }
    try:
        content = fm.give_away_passwd_to_proxy(cluster_name, target_file)
        results = content.split('/')
        if len(results) > 0:
            message_js['result'] = []
            for result in results:
                host_re_cmp = re.compile(r'Host:(.+) Result:(.+)')
                cmp_result = host_re_cmp.search(result)
                if cmp_result:
                    host, res = cmp_result.groups()
                    message_js["result"].append({"host": host, "result": res})
    except Exception, error:
        message_js["result"] = str(error)
        assert False
    finally:
        if taskid:
            take_tasklog_notes(taskid, 'give away %s file to %s cluster' % (target_file, cluster_name), json.dumps(message_js))
        reload_proxy_srv(cluster_name=cluster_name, taskid=taskid, referer=referer, syscode=syscode)


def reload_proxy_srv(cluster_name, referer, syscode, taskid=None):
    nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    nodes = filter(lambda x: json.loads(x.node_role)['Proxy-Server'] == 'YES', nodes)
    content_list = []
    message_js = {
        "source": referer,
        "syscode": syscode,
    }
    for proxy in nodes:
        try:
            result = requests.get('http://%s:8080/reload/' % proxy.node_inet_ip, timeout=5)
            message = 'Reload Proxy IP:%s  result:%s' % (proxy.node_inet_ip, result.status_code)
            access_logger.info(message)
        except IOError, error:
            message = 'Reload Proxy IP:%s  result:%s' % (proxy.node_inet_ip, error)
            access_logger.error(message)
        finally:
            content_list.append(message)
    messages = '/'.join(content_list)
    results = messages.split('/')
    if len(results) > 0:
        message_js['result'] = []
        for result in results:
            host_re_cmp = re.compile(r'Reload Proxy IP:(.+) result:(.+)')
            cmp_result = host_re_cmp.search(result)
            if cmp_result:
                host, res = cmp_result.groups()
                message_js["result"].append({"host": host, "result": res})
    if taskid:
        take_tasklog_notes(taskid, 'reload %s cluster proxy' % cluster_name, json.dumps(message_js))


def give_away_file_to_host(target_file, host, cp_file_path='/etc/swift', taskid=None):
    fm = FileManager()
    count = 0
    content = ''
    while count < 3:
        try:
            content = fm.give_away_file_to_host(host, target_file, cp_file_path=cp_file_path)
        except Exception, error:
            content = str(error)
            count += 1
        else:
            break
    message = content
    if taskid:
        take_tasklog_notes(taskid, 'give away %s file to %s' % (target_file, host), message)
    if count >= 3:
        assert False


def add_node_2_cluster(taskid, hostip, hostname, cluster_name):
    # init_policys(cluster_name) #策略初始化
    # disks = SfoClusterDisksMethod.query_additional_disks_by_hostname(hostname)
    pass


def standard_system(cluster_name, taskid=None):
    sfo_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    sfo_nodes = filter(lambda x: not (json.loads(x.node_role)['Proxy-Server'] == 'YES'
                                 and json.loads(x.node_role)['Container-Server'] == 'NO'
                                 and json.loads(x.node_role)['Account-Server'] == 'NO'
                                 and json.loads(x.node_role)['Object-Server'] == 'NO'),
                       sfo_nodes)
    cm = ClusterManager()
    if len(sfo_nodes) > 0:
        try:
            for sfo_node in sfo_nodes:
                systemd_zip_path = os.path.join(config.sfo_server_temp_file, 'standard')
                content = give_away_file_to_host(os.path.join(systemd_zip_path, 'openstack-swift-systemd.zip'),sfo_node.node_host_name, '/usr/lib/systemd/system', taskid=taskid)
                content = cm.excute_cmd(message='unzip -o -d /usr/lib/systemd/system/ /usr/lib/systemd/system/openstack-swift-systemd.zip', host=sfo_node.node_inet_ip)
                content = cm.excute_cmd(message='rm -f /usr/lib/systemd/system/openstack-swift-systemd.zip', host=sfo_node.node_inet_ip)
                content = cm.excute_cmd(message='systemctl daemon-reload', host=sfo_node.node_inet_ip)
                message = content
        except Exception, error:
            message = str(error)
            assert False
        finally:
            if taskid:
                take_tasklog_notes(taskid, 'standard %s cluster nodes' % cluster_name, message)


def create_cluster(cluster_name, taskid, ser_ip,
                   account_ring_json,
                   con_ring_json,
                   obj_ring_json,
                   proxy_json,
                   ):
    from sfo_utils.socket_utils import LocalProcessSocketClient
    sfo_nodes = SfoClusterNodesMethod.query_not_used_hosts()
    auth_switch = SfoCofigureMethod.query_value_from_con_key('AUTH_SWITCH')
    admin_user = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_USERNAME')
    admin_password = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_PASSWORD')
    for sfo_node in sfo_nodes:
        enable_cluster = False
        node_role = {"Proxy-Server": "NO", "Container-Server": "NO", "Account-Server": "NO", "Object-Server": "NO"}
        for proxy_node in proxy_json['nodes']:
            if sfo_node.node_host_name == proxy_node['host_name']:
                node_role.update({"Proxy-Server": "YES"})
                sfo_node.node_inet_ip = proxy_node['ip']
                enable_cluster = True
        for account_node in account_ring_json['nodes']:
            if sfo_node.node_host_name == account_node['host_name']:
                node_role.update({"Account-Server": "YES"})
                sfo_node.node_inet_ip = account_node['ip']
                sfo_node.node_replicate_ip = account_node["replication_ip"]
                enable_cluster = True

        for con_node in con_ring_json['nodes']:
            if sfo_node.node_host_name == con_node['host_name']:
                node_role.update({"Container-Server": "YES"})
                sfo_node.node_inet_ip = con_node['ip']
                sfo_node.node_replicate_ip = con_node["replication_ip"]
                enable_cluster = True

        for obj_node in obj_ring_json['nodes']:
            if sfo_node.node_host_name == obj_node['host_name']:
                node_role.update({"Object-Server": "YES"})
                sfo_node.node_inet_ip = obj_node['ip']
                sfo_node.node_replicate_ip = obj_node["replication_ip"]
                enable_cluster = True

        if enable_cluster:
            sfo_node.node_role = json.dumps(node_role, encoding='utf-8')
            sfo_node.cluster_name = cluster_name
    db.session.commit()

    def install_relation_service():
        sfo_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
        if sfo_nodes:
            for idy, sfo_node in enumerate(sfo_nodes):
                if sfo_node.cluster_name == cluster_name:
                    node_role = json.loads(sfo_node.node_role)
                    node_services = map(lambda x: x.split('-')[0].lower(),
                                        filter(lambda x: node_role[x] == 'YES', node_role))
                    for idx, srv in enumerate(node_services):
                        add_service(sfo_node, srv, taskid)
                        if srv == 'proxy':
                            add_service(sfo_node, 'memcached', taskid)

    def standard_ga_template():
        standard_system(cluster_name, taskid)
        sfo_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
        if sfo_nodes:
            sfo_proxy_nodes = filter(lambda x: json.loads(x.node_role)['Proxy-Server'] == 'YES', sfo_nodes)
            sfo_storage_nodes = filter(lambda x: json.loads(x.node_role)['Account-Server'] == 'YES' or
                                                 json.loads(x.node_role)['Container-Server'] == 'YES' or
                                                 json.loads(x.node_role)['Object-Server'] == 'YES', sfo_nodes)
            for node in sfo_proxy_nodes:
                ser_op = ServiceOperation(node.node_inet_ip)
                ser_op.excute_cmd("sed -i 's/\"64\"/\"1024\"/g' /etc/sysconfig/memcached")
                ser_op.excute_cmd(
                    'sed -i \'$c OPTIONS="-l 0.0.0.0 -U 11211 -t 12 >> /var/log/memcached.log 2>&1"\' /etc/sysconfig/memcached')

            for node in sfo_storage_nodes:
                systemd_zip_path = os.path.join(config.sfo_server_temp_file, 'standard')
                give_away_file_to_host(os.path.join(systemd_zip_path, 'SwiftDiskMount.sh'),
                                       node.node_host_name, '/usr/bin', taskid=taskid)
                ser_op = ServiceOperation(node.node_inet_ip)
                ser_op.excute_cmd('chmod +x /usr/bin/SwiftDiskMount.sh')
                ser_op.excute_cmd('systemctl enable openstack-swift-disk-mount.service')

            sfo_memcached_proxy = map(lambda x: x.node_inet_ip + ':11211', sfo_proxy_nodes)
            for idy, sfo_node in enumerate(sfo_nodes):
                base_dir = config.sfo_server_temp_file
                abs_dir = os.path.join(base_dir, sfo_node.node_inet_ip)
                if not os.path.exists(abs_dir):
                    os.mkdir(abs_dir)
                filenames = create_new_config_file(abs_dir, sfo_node,
                                                   **{"private_ip": sfo_node.node_replicate_ip,
                                                      "public_ip": sfo_node.node_inet_ip,
                                                      "ser_ip": ser_ip,
                                                      "account_server_+hostname": "account_server_%s" % sfo_node.node_host_name,
                                                      "object_server_+hostname": "object_server_%s" % sfo_node.node_host_name,
                                                      "container_server_+hostname": "container_server_%s" % sfo_node.node_host_name,
                                                      "proxy_server_+hostname": "proxy_server_%s" % sfo_node.node_host_name,
                                                      "memcachehost1:11211,memcachehost2:11211,memcachehost3:11211": ','.join(
                                                          sfo_memcached_proxy)})

                for idx, filename in enumerate(filenames):
                    target_file = os.path.join(abs_dir, filename)
                    if filename.startswith('account'):
                        cp_file_path = '/etc/swift/account-server'
                    elif filename.startswith('container'):
                        cp_file_path = '/etc/swift/container-server'
                    elif filename.startswith('object'):
                        cp_file_path = '/etc/swift/object-server'
                    elif filename.startswith('rsync'):
                        cp_file_path = '/etc'
                    elif filename == 'openstack-swift.conf':
                        cp_file_path = '/etc/rsyslog.d'
                    else:
                        cp_file_path = '/etc/swift'
                    give_away_file_to_host(target_file, sfo_node.node_host_name, cp_file_path, taskid)

    def mount_all_node_disks():
        sfo_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
        if sfo_nodes:
            sfo_nodes = filter(lambda x: json.loads(x.node_role)['Account-Server'] == 'YES'
                                         or json.loads(x.node_role)['Container-Server'] == 'YES'
                                         or json.loads(x.node_role)['Object-Server'] == 'YES', sfo_nodes)
            for node in sfo_nodes:
                add_disk(node.node_inet_ip, node.node_replicate_ip, node.node_host_name, '', taskid)

    def create_rings():
        rings = ['account', 'container', 'object']
        for idy, i in enumerate(rings):
            if i == 'account':
                create_ring(cluster_name, 'account',
                            account_ring_json['part_power'],
                            account_ring_json['replicas'],
                            account_ring_json['min_part_hours'],
                            '', taskid)
            elif i == 'container':
                create_ring(cluster_name, 'container',
                            con_ring_json['part_power'],
                            con_ring_json['replicas'],
                            con_ring_json['min_part_hours'],
                            '', taskid)
            else:
                create_ring(cluster_name, 'object',
                            obj_ring_json['part_power'],
                            obj_ring_json['replicas'],
                            obj_ring_json['min_part_hours'],
                            '', taskid)

    def add_all_disk_to_rings():
        for host_dict in account_ring_json['nodes']:
            ip = host_dict['ip']
            port = host_dict['port']
            zone = host_dict['zone']
            region = host_dict['region']
            host_name = host_dict['host_name']
            replication_ip = host_dict['replication_ip']
            replication_port = host_dict['replication_port']
            do = DiskOperation(ip, replication_ip)
            _, mount_disks = do.mounted_disks()
            for idx, disk in enumerate(mount_disks):
                _dist_mt_info = disk.strip()
                disk_mt_info_list = _dist_mt_info.split(' ')
                if len(disk_mt_info_list) >= 5:
                    disk_name = disk_mt_info_list[0]
                    label = disk_mt_info_list[4].replace('[', '').replace(']', '')
                    sfo_disk_per = SfoHostInfoMethod.query_host_info_by_host_name(host_name)
                    disk_total = json.loads(sfo_disk_per.disk_useful_size)[disk_name]
                    disk_total_bytes = reverse_unit(disk_total)
                    weight = weight_con(disk_total_bytes)
                    add_disk_2_ring(taskid=taskid,
                                    ring_name='account',
                                    region=region,
                                    zone=zone,
                                    ip=ip,
                                    port=port,
                                    disk_device=label,
                                    weight=weight,
                                    replication_ip=replication_ip,
                                    replication_port=replication_port,
                                    cluster_name=cluster_name)

        for host_dict in con_ring_json['nodes']:
            ip = host_dict['ip']
            port = host_dict['port']
            zone = host_dict['zone']
            region = host_dict['region']
            host_name = host_dict['host_name']
            replication_ip = host_dict['replication_ip']
            replication_port = host_dict['replication_port']
            do = DiskOperation(ip, replication_ip)
            _, mount_disks = do.mounted_disks()
            for idx, disk in enumerate(mount_disks):
                _dist_mt_info = disk.strip()
                disk_mt_info_list = _dist_mt_info.split(' ')
                if len(disk_mt_info_list) >= 5:
                    disk_name = disk_mt_info_list[0]
                    label = disk_mt_info_list[4].replace('[', '').replace(']', '')
                    sfo_disk_per = SfoHostInfoMethod.query_host_info_by_host_name(host_name)
                    disk_total = json.loads(sfo_disk_per.disk_useful_size)[disk_name]
                    disk_total_bytes = reverse_unit(disk_total)
                    weight = weight_con(disk_total_bytes)
                    add_disk_2_ring(taskid=taskid,
                                    ring_name='container',
                                    region=region,
                                    zone=zone,
                                    ip=ip,
                                    port=port,
                                    disk_device=label,
                                    weight=weight,
                                    replication_ip=replication_ip,
                                    replication_port=replication_port,
                                    cluster_name=cluster_name)

        for host_dict in obj_ring_json['nodes']:
            ip = host_dict['ip']
            port = host_dict['port']
            zone = host_dict['zone']
            region = host_dict['region']
            host_name = host_dict['host_name']
            replication_ip = host_dict['replication_ip']
            replication_port = host_dict['replication_port']
            do = DiskOperation(ip, replication_ip)
            _, mount_disks = do.mounted_disks()
            for idx, disk in enumerate(mount_disks):
                _dist_mt_info = disk.strip()
                disk_mt_info_list = _dist_mt_info.split(' ')
                if len(disk_mt_info_list) >= 5:
                    disk_name = disk_mt_info_list[0]
                    label = disk_mt_info_list[4].replace('[', '').replace(']', '')
                    sfo_disk_per = SfoHostInfoMethod.query_host_info_by_host_name(host_name)
                    disk_total = json.loads(sfo_disk_per.disk_useful_size)[disk_name]
                    disk_total_bytes = reverse_unit(disk_total)
                    weight = weight_con(disk_total_bytes)
                    add_disk_2_ring(taskid=taskid,
                                    ring_name='object',
                                    region=region,
                                    zone=zone,
                                    ip=ip,
                                    port=port,
                                    disk_device=label,
                                    weight=weight,
                                    replication_ip=replication_ip,
                                    replication_port=replication_port,
                                    cluster_name=cluster_name)

    def rebalance_ring():
        # # 监听创建环后执行添加磁盘
        # # # 添加磁盘到环
        rebalance('account', '', cluster_name, taskid)
        rebalance('container', '', cluster_name, taskid)
        rebalance('object', '', cluster_name, taskid)

    def ga_ring():
        give_away_ring('account.ring.gz', cluster_name, taskid)
        give_away_ring('container.ring.gz', cluster_name, taskid)
        give_away_ring('object.ring.gz', cluster_name, taskid)

    install_function_list = [install_relation_service, standard_ga_template, mount_all_node_disks, create_rings,
                             add_all_disk_to_rings, rebalance_ring, ga_ring]

    local_soc_client = LocalProcessSocketClient(host='127.0.0.1', port=54444)
    for step, func in enumerate(install_function_list):
        try:
            step += 1
            func()
        except AssertionError:
            local_soc_client.send(
                json.dumps(
                    {"taskid": taskid, "float_percent": round(float(step) / float(len(install_function_list)), 2),
                     "status": 500}))

            break
        else:
            local_soc_client.send(
                json.dumps(
                    {"taskid": taskid, "float_percent": round(float(step) / float(len(install_function_list)), 2),
                     "status": 200}))



def wakeup_aps():
    """
     向任务池中定时添加任务用于唤醒定时任务来处理,应被处理却没有处理的任务
    :return:
    """

class APScheduler(object):

    def __new__(cls, *args, **kwargs):
        with rlock:
            if not hasattr(cls, "instance"):
                cls.instance = super(APScheduler, cls).__new__(cls)
            return cls.instance

    def __init__(self, jobstores=None, executors=None, job_defaults=None):
        self.jobstores = jobstores
        self.executors = executors
        self.job_defaults = job_defaults
        self.sfo_scheduler = BackgroundScheduler(jobstores=self.jobstores,
                                                 executors=self.executors,
                                                 job_defaults=self.job_defaults)

    def wake_up(self):
        self.sfo_scheduler.add_job(wakeup_aps, 'cron', second='*/10', id='wake_up', replace_existing=True)

    def start(self):
        try:
            self.sfo_scheduler.start()
        except SchedulerAlreadyRunningError:
            logging.info('调度器已经启动')

    def shutdown(self):
        try:
            self.sfo_scheduler.shutdown()
        except SchedulerNotRunningError:
            logging.info('调度器还没启动')

    def restart(self):
        try:
            self.shutdown()
            self.start()
        except Exception, error:
            logging.error('重启调度器时发生错误 %s'%str(error))

    def add_disk(self, args, run_time='', id=None, replace_existing=None):
        run_time = datetime.datetime.now() if not run_time else run_time
        _args = inspect.getargspec(add_disk).args
        kwargs = {}
        for idx, arg in enumerate(_args):
            if arg == 'taskid':
                try:
                    val = args[idx]
                    kwargs.update({arg: val})
                except IndexError:
                    kwargs.update({arg: id})
            else:
                try:
                    kwargs.update({arg: args[idx]})
                except IndexError:
                    pass
        self.sfo_scheduler.add_job(add_disk, 'date', run_date=run_time, kwargs=kwargs, id=id, replace_existing=replace_existing)

    def add_service(self, args, run_time='', id=None, replace_existing=None):
        run_time = datetime.datetime.now() if not run_time else run_time
        _args = inspect.getargspec(add_service).args
        kwargs = {}
        for idx, arg in enumerate(_args):
            if arg == 'taskid':
                try:
                    val = args[idx]
                    kwargs.update({arg: val})
                except IndexError:
                    kwargs.update({arg: id})
            else:
                try:
                    kwargs.update({arg: args[idx]})
                except IndexError:
                    pass
        self.sfo_scheduler.add_job(add_service, 'date', run_date=run_time, kwargs=kwargs, id=id, replace_existing=replace_existing)

    def give_away_passwd_to_proxy(self, args, run_time='', id=None, replace_existing=None):
        run_time = datetime.datetime.now() if not run_time else run_time
        _args = inspect.getargspec(give_away_passwd_to_proxy).args
        kwargs = {}
        for idx, arg in enumerate(_args):
            if arg == 'taskid':
                try:
                    val = args[idx]
                    kwargs.update({arg: val})
                except IndexError:
                    kwargs.update({arg: id})
            else:
                try:
                    kwargs.update({arg: args[idx]})
                except IndexError:
                    pass
        self.sfo_scheduler.add_job(give_away_passwd_to_proxy, 'date', run_date=run_time, kwargs=kwargs, id=id, replace_existing=replace_existing)

    def create_cluster(self, args, run_time='', id=None, replace_existing=None):
        run_time = datetime.datetime.now() if not run_time else run_time
        _args = inspect.getargspec(create_cluster).args
        kwargs = {}
        for idx, arg in enumerate(_args):
            if arg == 'taskid':
                try:
                    val = args[idx]
                    kwargs.update({arg: val})
                except IndexError:
                    kwargs.update({arg: id})
            else:
                try:
                    kwargs.update({arg: args[idx]})
                except IndexError:
                    pass
        self.sfo_scheduler.add_job(create_cluster, 'date', run_date=run_time, kwargs=kwargs, id=id, replace_existing=replace_existing)


scheduler = APScheduler(jobstores=jobstores, job_defaults=job_defaults, executors=executors)