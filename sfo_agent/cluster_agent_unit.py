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

from sfo_agent.kafka_producer import ProduceKafkaInfo
from sfo_common.agent import Agent
from sfo_common.import_common import *


class ClusterInfo(object):
    '''
    集群信息采集类
    '''
    def __init__(self):
        pass

    def get_node_perform_info(self, stgip):
        '''
        根据给定的ip地址获取recon的集群运行数据
        数据来源于节点的recon，所以需要节点配置好recon并开启
        :param stgip:
        :return:
        '''
        pci = ProduceKafkaInfo()
        ns = NodeService()
        try:
            clinfo = {}
            roles = ns.get_node_role()
            port = 0
            ports = []
            if not roles:
                return
            if roles['Account-Server'] == 'YES':
                if ns.check_port_by_socket(stgip, config.account_port):
                    port = config.account_port
                    ports.append(config.account_port)
            elif roles['Container-Server'] == 'YES':
                if ns.check_port_by_socket(stgip, config.container_port):
                    port = config.container_port
                    ports.append(config.container_port)
            elif roles['Object-Server'] == 'YES':
                if ns.check_port_by_socket(stgip, config.object_port):
                    port = config.object_port
                    ports.append(config.object_port)
            elif roles['Proxy-Server'] == 'YES':
                pass
            else:
                errport = ','.join(ports)
                logger.info('socket test port is blocked,host ip is {},host port is {}'.format(stgip, str(errport)))
            if port > 0:
                uri = 'http://' + str(stgip).strip() + ':' + str(port)
                clinfo['guid'] = str(uuid.uuid1())
                clinfo['data_model'] = 'SfoNodePerform'
                clinfo['host_name'] = socket.getfqdn()
                clinfo['node_role'] = json.dumps(ns.get_node_role(), encoding="UTF-8", ensure_ascii=True)

                url = uri + r'/recon/version'
                url_response = json.loads(requests.post(url).text, encoding="UTF-8")
                if url_response:
                    clinfo['swift_version'] = url_response['version']

                url = uri + r'/recon/time'
                time_response = requests.post(url).text
                if url_response:
                    clinfo['node_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(time_response)))

                url = uri + r'/recon/async'
                url_response = json.loads(requests.post(url).text, encoding="UTF-8")
                if url_response:
                    clinfo['async_pending'] = url_response['async_pending']

                url = uri + r'/recon/sockstat'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['node_sockstat'] = url_response

                url = uri + r'/recon/diskusage'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['stg_diskusage'] = url_response

                url = uri + r'/recon/driveaudit'
                url_response = json.loads(requests.post(url).text, encoding="UTF-8")
                if url_response:
                    clinfo['drive_audit_errors'] = url_response['drive_audit_errors']

                url = uri + r'/recon/ringmd5'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['node_ringmd5'] = url_response

                url = uri + r'/recon/swiftconfmd5'
                url_response = json.loads(requests.post(url).text, encoding="UTF-8")
                if url_response:
                    clinfo['swiftconfmd5'] = url_response[r'/etc/swift/swift.conf']

                url = uri + r'/recon/quarantined'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['quarantined_count'] = url_response

                url = uri + r'/recon/replication/account'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['account_replication'] = url_response

                url = uri + r'/recon/replication/container'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['container_replication'] = url_response

                url = uri + r'/recon/replication/object'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['object_replication'] = url_response

                url = uri + r'/recon/auditor/account'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['account_auditor'] = url_response

                url = uri + r'/recon/auditor/container'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['container_auditor'] = url_response

                url = uri + r'/recon/auditor/object'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['object_auditor'] = url_response

                url = uri + r'/recon/updater/container'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['container_updater'] = url_response

                url = uri + r'/recon/updater/object'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['object_updater'] = url_response

                url = uri + r'/recon/expirer/object'
                url_response = requests.post(url).text
                if url_response:
                    clinfo['object_expirer'] = url_response

                clinfo['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                data = json.dumps(clinfo, encoding="UTF-8", ensure_ascii=True)
                pci.produce_kafka_info(config.kafka_sys_topic,data)
        except Exception as ex:
            logger.exception("get_node_perform_info function excute exception:" + str(ex))


def get_node_service_stat_schl():
    '''
    起线程定时执行集群中节点服务状态采集
    :return:
    '''
    try:
        host_ip = util.get_ipaddr('HOST')
        ns = NodeService()
        threading.Thread(target=ns.get_node_service_stat,args=[host_ip]).start()
    except Exception as ex:
        logger.exception("get_node_service_stat_schl function excute exception:" + str(ex))


def get_node_perform_schl():
    '''
    起线程定时执行节点运行状态数据采集
    :return:
    '''
    try:
        host_ip = util.get_ipaddr('HOST')
        cli = ClusterInfo()
        threading.Thread(target=cli.get_node_perform_info,args=[host_ip]).start()
    except Exception as ex:
        logger.exception("get_node_perform_schl function excute exception:" + str(ex))


class ClusterUnitAgnet(Agent):
    def __init__(self, pidfile):
        Agent.__init__(self, pidfile)

    def run(self):
        '''
        重写守护进程的run函数，实现集群中节点服务状态和运行状态数据的定时收集
        :return:
        '''
        try:
            sys.stdout.flush()
            hostname = socket.getfqdn()
            hostip = socket.gethostbyname(hostname)
            logger.info("hostname is {}, ip is {}".format(hostname, hostip))
            schedule.every(config.node_refresh).seconds.do(get_node_service_stat_schl)
            schedule.every(config.node_refresh).seconds.do(get_node_perform_schl)
            schedule.run_all(0)
            while True:
                schedule.run_pending()
                time.sleep(0.1)
        except Exception as ex:
            logger.exception("cluster agent run function excute exception:" + str(ex))


class NodeService(object):
    '''
    节点上服务状态采集类
    '''
    def __init__(self):
        pass

    def get_node_service_stat(self, stgip):
        '''
        获取节点上swift服务状态
        根据进程判断服务是否在运行，对于主要服务，同时检测服务端口
        :param stgip:
        :return:数据生成到kafka中
        '''
        pci = ProduceKafkaInfo()
        try:
            nodesrv = {}
            nodesrv['guid'] = str(uuid.uuid1())
            nodesrv['data_model'] = 'SfoNodeService'
            nodesrv['host_name'] = socket.getfqdn()
            nodesrv['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            process_stat = util.excute_command('ps -ef |grep python |grep swift')
            if 'swift-proxy-server' in process_stat:
                if self.check_port_by_socket(stgip, config.proxy_port):
                    nodesrv['srv_proxy'] = 'running'
                else:
                    nodesrv['srv_proxy'] = 'warning'
            else:
                nodesrv['srv_proxy'] = 'stopped'
            if 'swift-account-server' in process_stat:
                if self.check_port_by_socket(stgip, config.account_port):
                    nodesrv['srv_account'] = 'running'
                else:
                    nodesrv['srv_account'] = 'warning'
            else:
                nodesrv['srv_account'] = 'stopped'

            if 'swift-account-auditor' in process_stat:
                nodesrv['srv_account_auditor'] = 'running'
            else:
                nodesrv['srv_account_auditor'] = 'stopped'

            if 'swift-account-reaper' in process_stat:
                nodesrv['srv_account_reaper'] = 'running'
            else:
                nodesrv['srv_account_reaper'] = 'stopped'

            if 'swift-account-replicator' in process_stat:
                nodesrv['srv_account_replicator'] = 'running'
            else:
                nodesrv['srv_account_replicator'] = 'stopped'

            if 'swift-container-server' in process_stat:
                if self.check_port_by_socket(stgip, config.container_port):
                    nodesrv['srv_container'] = 'running'
                else:
                    nodesrv['srv_container'] = 'warning'
            else:
                nodesrv['srv_container'] = 'stopped'

            if 'swift-container-auditor' in process_stat:
                nodesrv['srv_container_auditor'] = 'running'
            else:
                nodesrv['srv_container_auditor'] = 'stopped'

            if 'swift-container-replicator' in process_stat:
                nodesrv['srv_container_replicator'] = 'running'
            else:
                nodesrv['srv_container_replicator'] = 'stopped'

            if 'swift-container-updater' in process_stat:
                nodesrv['srv_container_updater'] = 'running'
            else:
                nodesrv['srv_container_updater'] = 'stopped'

            if 'swift-container-sync' in process_stat:
                nodesrv['srv_container_sync'] = 'running'
            else:
                nodesrv['srv_container_sync'] = 'stopped'

            if 'swift-container-reconciler' in process_stat:
                nodesrv['srv_container_reconciler'] = 'running'
            else:
                nodesrv['srv_container_reconciler'] = 'stopped'

            if 'swift-object-server' in process_stat:
                if self.check_port_by_socket(stgip, config.object_port):
                    nodesrv['srv_object'] = 'running'
                else:
                    nodesrv['srv_object'] = 'warning'
            else:
                nodesrv['srv_object'] = 'stopped'

            if 'swift-object-auditor' in process_stat:
                nodesrv['srv_object_auditor'] = 'running'
            else:
                nodesrv['srv_object_auditor'] = 'stopped'

            if 'swift-object-replicator' in process_stat:
                nodesrv['srv_object_replicator'] = 'running'
            else:
                nodesrv['srv_object_replicator'] = 'stopped'

            if 'swift-object-updater' in process_stat:
                nodesrv['srv_object_updater'] = 'running'
            else:
                nodesrv['srv_object_updater'] = 'stopped'

            if 'swift-object-expirer' in process_stat:
                nodesrv['srv_object_expirer'] = 'running'
            else:
                nodesrv['srv_object_expirer'] = 'stopped'

            if 'swift-object-reconstructor' in process_stat:
                nodesrv['srv_object_reconstructor'] = 'running'
            else:
                nodesrv['srv_object_reconstructor'] = 'stopped'

            data = json.dumps(nodesrv, encoding="UTF-8", ensure_ascii=True)
            pci.produce_kafka_info(config.kafka_sys_topic,data)
        except Exception as ex:
            logger.exception("get_node_service_stat function excute exception:" + str(ex))

    def get_node_role(self):
        '''
        根据主机上运行的进程判断主机的角色
        :return:
        '''
        try:
            role = {}
            process_stat = util.excute_command('ps -ef |grep python |grep swift')
            if process_stat:
                pro_parser = reg_templates.NodeServiceParser(process_stat)
                pro_res = pro_parser.parse()

                if pro_res.has_key('srv_proxy'):
                    role['Proxy-Server'] = 'YES'
                else:
                    role['Proxy-Server'] = 'NO'

                if pro_res.has_key('srv_account'):
                    role['Account-Server'] = 'YES'
                else:
                    role['Account-Server'] = 'NO'

                if pro_res.has_key('srv_container'):
                    role['Container-Server'] = 'YES'
                else:
                    role['Container-Server'] = 'NO'

                if pro_res.has_key('srv_object'):
                    role['Object-Server'] = 'YES'
                else:
                    role['Object-Server'] = 'NO'
            return role
        except Exception as ex:
            logger.exception("get_node_role function excute exception:" + str(ex))

    def check_port_by_socket(self, targetip, targetport):
        '''
        检查节点的端口是否能正常连通
        :param targetip:
        :param targetport:
        :return:
        '''
        stat = False
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sk.settimeout(2)
            sk.connect((targetip, targetport))
            stat = True
        except Exception as ex:
            stat = False
            logger.exception("check_port_by_socket function excute exception:{},targetip is {},target port is {}".format(str(ex),targetip,str(targetport)))
        finally:
            sk.close()
            return stat

