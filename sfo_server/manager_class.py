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
import asyncore
import copy
import json
import logging
import sys
from multiprocessing import RLock

import os
import re
from swift.common.exceptions import SwiftException
from swift.common.ring import RingBuilder

from sfo_agent.cluster_server_client import ClusterClient
from sfo_common.agent import Config
from sfo_server import SCRIPT_PATH, PROXY_HOST_IP
from sfo_server import access_logger
from sfo_server.build_config_template import create_new_config_specify_file
from sfo_server.models import SfoClusterNodesMethod, SfoCofigureMethod, SfoHostRingMethod, db
from sfo_utils.utils import Util

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

util = Util()
lock = RLock()
config = Config()


def compare_remote_host_md5(file, host):
    target_file = os.path.join(config.temp_file, os.path.basename(file))
    local_file_md5 = util.excute_command('md5sum %s' % file)
    socket_client = ClusterClient(host, config.sock_cmd_port)
    socket_client.message = '%s' % ('md5sum %s' % target_file)
    asyncore.loop()
    target_file_md5 = socket_client.buffer
    _local_md5 = local_file_md5.split(' ')
    if len(_local_md5) > 0:
        _local_md5 = _local_md5[0]
    _tar_md5 = target_file_md5.split(' ')
    if len(_tar_md5) > 0:
        _tar_md5 = _tar_md5[0]
    return not cmp(_local_md5, _tar_md5)


class NodeConfigBasic:
    """
    节点配置基类
    """

    default_config_path = ''

    def __init__(self, node_host):
        self.host = node_host
        self.cmd_port = 7201
        self.file_port = 7202

    def change_config(self, content, config_file, host=None):
        """
        更改配置文件
        :param content: 修改前的配置内容(全部内容)
        :return: 修改后的配置内容(生成一个新的配置文件)
        """
        base_dir = config.sfo_server_temp_file
        new_host_dir = os.path.join(base_dir, host if host else self.host)
        new_path = '%s' % (os.path.join(base_dir, os.path.join(host if host else self.host, config_file)))
        back_path = '%s_backup' % (os.path.join(base_dir, os.path.join(host if host else self.host, config_file)))
        try:
            with lock:
                if not os.path.isdir(new_host_dir):
                    os.mkdir(new_host_dir)
                if os.path.exists(new_path):
                    os.rename(new_path, back_path)
                with open(new_path, 'wb') as f:
                    f.write(content)
        except Exception, error:
            logging.error("create %s fail get %s" % (config_file, error))
            if os.path.exists(new_path):
                os.remove(new_path)
                if os.path.exists(back_path):
                    os.rename(back_path, new_path)
                    logging.info('rollback %s file' % back_path)
        else:
            if os.path.exists(back_path):
                os.remove(back_path)

    def excute_cmd_file(self, message, config_path, config_file, host=None):
        socket_client = ClusterClient(host if host else self.host, self.cmd_port)
        config_path = config_path if config_path else self.default_config_path
        if not config_path:
            raise NotImplementedError('config_path or default config path must alertnative')
        socket_client.message = '%s %s/%s' % (message, config_path, config_file)
        asyncore.loop(map=socket_client._map)
        if socket_client.buffer:
            if socket_client.buffer == '__wait__':
                content = 'Connection Error'
            elif socket_client.buffer == 'SUCCESS':
                content = 'Excute Cmd Success'
            elif socket_client.buffer == 'Operation failed':
                content = 'Excute Cmd Fail'
            else:
                content = copy.deepcopy(socket_client.buffer)
        else:
            content = 'Excute Cmd Fail'
        del socket_client
        return content

    def excute_cmd_dir(self, message, config_path, host):
        socket_client = ClusterClient(host if host else self.host, self.cmd_port)
        config_path = config_path if config_path else self.default_config_path
        if not config_path:
            raise NotImplementedError('config_path or default config path must alertnative')
        socket_client.message = '%s %s' % (message, config_path)
        asyncore.loop(map=socket_client._map)
        if socket_client.buffer:
            if socket_client.buffer == '__wait__':
                content = 'Connection Error'
            elif socket_client.buffer == 'SUCCESS':
                content = 'Excute Cmd Success'
            elif socket_client.buffer == 'Operation failed':
                content = 'Excute Cmd Fail'
            else:
                content = copy.deepcopy(socket_client.buffer)
        else:
            content = 'Excute Cmd Fail'
        del socket_client
        return content

    def list_dir(self, message='ls', config_path=default_config_path, host=None):
        """
        查看配置列表页
        :param message:
        :param config_path:
        :return:
        """
        content = self.excute_cmd_dir(message, config_path, host if host else self.host)
        if content == 'Excute Cmd Fail':
            content = 'No such directory %s' % config_path
            raise IOError(content)
        elif content == 'Connection Error':
            raise IOError('Error %s from ls %s ' % (content, config_path))
        return content

    def read_config(self, config_file, config_path=default_config_path, host=None):
        """
        读取配置文件
        :param config_path:
        :return:
        """
        content = self.excute_cmd_file('cat', config_path, config_file, host if host else self.host)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            raise IOError('Error %s from cat %s/%s ' %(content, config_path, config_file))
        return content

    def write_config(self, config_file, host=None):
        """
        向对象地址写入配置文件
        :return:
        """
        base_dir = config.sfo_server_temp_file
        new_file_path = '%s' % (os.path.join(base_dir, os.path.join(self.host, config_file)))
        if os.path.exists(new_file_path):
            file_socket_client = ClusterClient(host if host else self.host, self.file_port, filepath=new_file_path)
            asyncore.loop(map=file_socket_client._map)
            try:
                if file_socket_client.buffer:
                    content = json.loads(file_socket_client.buffer)
                    if content == '__wait__':
                        content = 'Connection Error'
                    elif content['result'] == "File receive compeled":
                        content = 'Send File Success'
                    else:
                        content = 'Send File Fail'
                else:
                    content = 'Send File Fail'
            except Exception:
                content = 'Send File Fail'
            result = copy.deepcopy(content)
            del file_socket_client
            return result

    def restart_service(self, config_file):
        """
        修改软件配置后,需要重启服务的配置实例
        :return:
        """
        pass

    def config_file_md5sum(self, config_file, config_path=default_config_path, host=None):
        """
        获取文件对象Md5值
        :param config_file: 文件对象名
        :param config_path:  文件路径
        :return:
        """
        content = self.excute_cmd_file('md5sum', config_path, config_file, host if host else self.host)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            raise IOError('Error %s from get %s md5sum ' %(content, config_file))
        return content

    def chmod(self, permission, config_file, config_path, host=None):
        content = self.excute_cmd_file('chmod %d'% permission, config_path, config_file, host if host else self.host)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            raise IOError('Error %s from change %s mode' %(content, config_file))
        return content

    def copy(self, old_path, config_path, config_file, host=None):
        content = self.excute_cmd_file('cp {old_path}/{config_file} '.format(old_path=old_path,
                                                                             config_file=config_file)
                                       , config_path, config_file, host if host else self.host)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            raise IOError('Error %s from copy %s %s' %(content, old_path, config_path))
        return content


class SwiftConfig(NodeConfigBasic):

    default_config_path = '/etc/swift'

    def restart_service(self, config_file):
        """
        重启对应的服务
        :param config_file:
        :return:
        """
        if config_file.endswith('.conf'):
            filename, ext = config_file.split('.')
            con_filename = filename.strip('-server')
            socket_client = ClusterClient(self.host, self.cmd_port)
            socket_client.message = 'systemctl restart openstack-swift-%s.service' % con_filename
            asyncore.loop(map=socket_client._map)
            if socket_client.buffer:
                content = copy.deepcopy(socket_client.buffer)
            else:
                content = 'Restart Service Fail'
            del socket_client
            return content


class OperationSystemConfig(NodeConfigBasic):
    pass


class ServiceOperation:

    def __init__(self, host):
        self.host = host
        self.cmd_port = 7201

    def excute_cmd(self, message, host=None):
        socket_client = ClusterClient(host if host else self.host, self.cmd_port)
        socket_client.message = '%s' % message
        asyncore.loop()
        if socket_client.buffer:
            if socket_client.buffer == '__wait__':
                content = 'Connection Error'
            elif 'SUCCESS' in socket_client.buffer:
                content = 'Excute Cmd Success'
            elif socket_client.buffer == 'Operation failed':
                content = 'Excute Cmd Fail'
            else:
                content = copy.deepcopy(socket_client.buffer)
        else:
            content = 'Excute Cmd Fail'
        del socket_client
        return content

    def stop(self, service):
        cmd = str('sh %s/serviceoperation.sh stop %s' % (SCRIPT_PATH, service))
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('stop %s host:%s cmd:%s result:%s' % (service, self.host, cmd, content))
            raise IOError('stop %s host:%s cmd:%s result:%s' % (service, self.host, cmd, content))
        return content

    def start(self, service):
        cmd = str('sh %s/serviceoperation.sh start %s' % (SCRIPT_PATH, service))
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from start %s service ' % (content, service))
            raise IOError('Error %s from start %s service ' % (content, service))
        return content

    def status(self, service):
        cmd = str('sh %s/serviceoperation.sh status %s' % (SCRIPT_PATH, service))
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from restart %s service' % (content, service))
            raise IOError('Error %s from restart %s service' % (content, service))
        return content

    def restart(self, service):
        cmd = str('sh %s/serviceoperation.sh restart %s' % (SCRIPT_PATH, service))
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from restart %s service' % (content, service))
            raise IOError('Error %s from restart %s service' % (content, service))
        return content

    def install_service(self, services=''):
        services = services if services else 'all'
        cmd = str('sh %s/softmanage.sh install %s' % (SCRIPT_PATH, services))
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from install %s service' % (content, services))
            raise IOError('Error %s from install %s service' % (content, services))
        return content

    def uninstall_service(self, services=''):
        services = services if services else 'all'
        cmd = str('sh %s/softmanage.sh uninstall %s' % (SCRIPT_PATH, services))
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from uninstall %s service'%(content, services))
            raise IOError('Error %s from uninstall %s service'%(content, services))
        return content

    def srvs(self, softwares_grep):
        """
        'openstack-swift-account*|openstack-swift-object*|rsyncd?'
        :param softwares:
        :return:
        """
        srvs_list = []
        cmd = "ls /usr/lib/systemd/system/ |grep -E '%s' |grep -v '@' |grep service" % softwares_grep
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from list service status' % content)
            raise IOError('Error %s from list service status' % content)
        else:
            _srvs = content.split('\n')
            for srv in _srvs:
                if not bool(srv.strip()):
                    continue
                srv_info_dict = {"stat": '', "message": '', "service": ''}
                srv_info_dict['service'] = srv
                try:
                    status_content = self.status(srv)
                    access_logger.info('get %s status host:%s result:%s' % (srv, self.host, status_content))
                    active_status_cmp = re.compile('Active: .+\((.+)\)')
                    active_status_cmp_result = active_status_cmp.search(status_content)
                    if active_status_cmp_result:
                        stat = active_status_cmp_result.groups()[0]
                        if stat == 'dead':
                            stat_code = 0
                        elif stat == 'running':
                            stat_code = 1
                        else:
                            stat_code = 2
                        srv_info_dict['stat'] = stat_code
                        srvs_list.append(srv_info_dict)
                    else:
                        access_logger.info('Can not compile service from %s status content' % self.host)
                except IOError, error:
                    srv_info_dict['message'] = str(error)
                    srvs_list.append(srv_info_dict)
        return srvs_list


class SwiftServiceOperation(ServiceOperation):
    pass


class NodeManager:
    """
    节点管理
    """
    def __init__(self, host):
        """
        被管理的host的ip地址
        :param host:
        """
        self.host = host
        self.swift_service = SwiftServiceOperation(self.host)
        self.swift_config = SwiftConfig(self.host)
        self.os_service = ServiceOperation(self.host)
        self.os_config = OperationSystemConfig(self.host)


class ClusterManager:

    def __init__(self):
        self.cmd_port = 7201

    def excute_cmd(self, message, host):
        socket_client = ClusterClient(host, self.cmd_port)
        socket_client.message = '%s' % message
        asyncore.loop()
        if socket_client.buffer:
            if socket_client.buffer == '__wait__':
                content = 'Connection Error'
            elif socket_client.buffer == 'SUCCESS':
                content = 'Excute Cmd Success'
            elif socket_client.buffer == 'Operation failed':
                content = 'Excute Cmd Fail'
            else:
                content = copy.deepcopy(socket_client.buffer)
        else:
            content = 'Excute Cmd Fail'
        del socket_client
        return content


class RingManager:

    """
    环管理只在代理主机上执行
    """

    def __init__(self, cluster_name):
        self.host = PROXY_HOST_IP
        self.cmd_port = 7201
        self.swift_path = os.path.join(config.sfo_server_temp_file, 'etc')
        self.cluster_name = cluster_name
        if not os.path.exists('%s/%s/swift' % (self.swift_path, self.cluster_name)):
            os.makedirs('%s/%s/swift' % (self.swift_path, self.cluster_name), mode=644)
        else:
            if not os.path.exists('%s/%s/swift/swift.conf' % (self.swift_path, self.cluster_name)):
                result = create_new_config_specify_file('swift.conf',
                                                        '%s/%s/swift/' % (self.swift_path, self.cluster_name))
                if not result:
                    raise StandardError('Can not build swift.conf template ....')

    def excute_cmd(self, message, host=None):
        socket_client = ClusterClient(host if host else self.host, self.cmd_port)
        socket_client.message = '%s' % message
        asyncore.loop(map=socket_client._map)
        if socket_client.buffer:
            if socket_client.buffer == '__wait__':
                content = 'Connection Error'
            elif socket_client.buffer == 'SUCCESS':
                content = 'Excute Cmd Success'
            elif socket_client.buffer == 'Operation failed' or socket_client.buffer == 'FAILED':
                content = 'Excute Cmd Fail'
            else:
                content = copy.deepcopy(socket_client.buffer)
        else:
            content = 'Excute Cmd Fail'
        del socket_client
        return content

    def create(self, part_power, replicas, min_part_hours, policy=False, policy_num='', ring_name=''):
        """
        创建环
        :param ring_name: account / container/ object
        :param part_power:  分区数
        :param replicas:    副本数
        :param min_part_hours:   移动分区最小间隔时间
        :param policy:   是否属于策略环
        :return:
        """
        if not policy:
            content = self.excute_cmd(str('sh %s/ringmanage.sh %s create %s %s %s %s' % (SCRIPT_PATH,
                                      ring_name,
                                      part_power,
                                      replicas,
                                      min_part_hours,
                                      '%s/%s/swift/%s.builder' % (self.swift_path, self.cluster_name, ring_name))))
        else:
            content = self.excute_cmd(str('sh %s/ringmanage.sh policy %s create %s %s %s %s %s' % (SCRIPT_PATH,
                                     policy_num,
                                     part_power,
                                     replicas,
                                     min_part_hours,
                                     '%s/%s/swift/swift.conf' % (self.swift_path, self.cluster_name),
                                     '%s/%s/swift/%s.builder' % (self.swift_path, self.cluster_name, 'object-%s'%policy_num))))

        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from create %s ring ' % (content, ring_name if not policy else 'Object-%s' % policy_num))
            raise IOError(
                'Error %s from create %s ring ' % (content, ring_name if not policy else 'Object-%s' % policy_num))
        return content

    def add_disk_2_ring(self, region, zone, ip, port, disk_device, weight, replication_ip='', replication_port='', policy=False, policy_num='', ring_name=''):
        disk_device = disk_device if disk_device else 'all'
        if not policy:
            content = self.excute_cmd(str(
                'sh {script_path}/ringmanage.sh {ring_name} add {region} {zone} {ip} {port} {replication_ip} {replication_port} {device} {weight} {builder_path}'
                    .format(**{'ring_name': ring_name,
                               'region': region,
                               'zone': zone,
                               'ip': ip,
                               'port': port,
                               'device': disk_device,
                               'weight': weight,
                               'replication_ip': replication_ip,
                               'replication_port': replication_port,
                               "script_path": SCRIPT_PATH,
                               "builder_path": '%s/%s/swift/%s.builder' % (self.swift_path, self.cluster_name, ring_name)})))
        else:
            content = self.excute_cmd(str(
                'sh {script_path}/ringmanage.sh policy {policy_num} add {region} {zone} {ip} {port} {replication_ip} {replication_port} {device} {weight} {swift_conf_path} {builder_path}'
                .format(**{'policy_num': policy_num,
                           'region': region,
                           'zone': zone,
                           'ip': ip,
                           'port': port,
                           'device': disk_device,
                           'weight': weight,
                           'replication_ip': replication_ip,
                           'replication_port': replication_port,
                           "script_path": SCRIPT_PATH,
                           "swift_conf_path": '%s/%s/swift/swift.conf' % (self.swift_path, self.cluster_name),
                           "builder_path": '%s/%s/swift/%s.builder' % (self.swift_path, self.cluster_name, 'object-%s'%policy_num)})))

        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from add disk to %s ring ip:%s device:%s '%(content,
                                                                                ring_name if not policy else 'Object-%s' % policy_num,
                                                                                ip,
                                                                                disk_device,))
            raise IOError('Error %s from add disk to %s ring ip:%s device:%s '%(content,
                                                                                ring_name if not policy else 'Object-%s' % policy_num,
                                                                                ip,
                                                                                disk_device,))
        return content

    def remove_disk_immediately(self, disk_device, ip, port, policy=False, ring_name='', policy_num=''):
        if not policy:
            content = self.excute_cmd(str('sh {script_path}/ringmanage.sh {ring_name} remove {ip}:{port}/{device} {builder_path}'
                                          .format(**{'ring_name': ring_name,
                                                     'device': disk_device,
                                                     "ip": ip,
                                                     "port": port,
                                                     "script_path": SCRIPT_PATH,
                                                     "builder_path": '%s/%s/swift/%s.builder' % (self.swift_path, self.cluster_name, ring_name)})))
        else:
            content = self.excute_cmd(
                str('sh {script_path}/ringmanage.sh policy {policy_num} remove {ip}:{port}/{device} {swift_conf_path} {builder_path}'
                    .format(**{'policy_num': policy_num,
                               'device': disk_device,
                               "ip": ip,
                               "port": port,
                               "script_path": SCRIPT_PATH,
                               "swift_conf_path": '%s/%s/swift/swift.conf' % (self.swift_path, self.cluster_name),
                               "builder_path": '%s/%s/swift/%s.builder' % (self.swift_path, self.cluster_name, 'object-%s'%policy_num)})))

        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from remove disk immediately ip:%s device:%s ring:%s' % (content,
                                                                                             ip,
                                                                                             disk_device,
                                                                                             ring_name if not policy else 'Object-%s' % policy_num))
            raise IOError('Error %s from remove disk immediately ip:%s device:%s ring:%s' % (content,
                                                                                             ip,
                                                                                             disk_device,
                                                                                             ring_name if not policy else 'Object-%s' % policy_num))
        return content

    def remove_disk_slowly(self, weight, disk_device, ip, port, policy=False, ring_name='', policy_num=''):
        if not policy:
            content = self.excute_cmd(
                str('sh {script_path}/ringmanage.sh {ring_name} setweight {ip}:{port}/{device} {weight} {builder_path}'
                    .format(**{'ring_name': ring_name,
                               'device': disk_device,
                               'weight': weight,
                               "ip": ip,
                               "port": port,
                               "script_path": SCRIPT_PATH,
                               "builder_path": '%s/%s/swift/%s.builder' % (self.swift_path, self.cluster_name, ring_name)})))
        else:
            content = self.excute_cmd(
                str('sh {script_path}/ringmanage.sh policy {policy_num} setweight {ip}:{port}/{device} {weight} {swift_conf_path} {builder_path}'
                    .format(**{'policy_num': policy_num,
                               'device': disk_device,
                               'weight': weight,
                               "ip": ip,
                               "port": port,
                               "script_path": SCRIPT_PATH,
                               "swift_conf_path": '%s/%s/swift/swift.conf' % (self.swift_path, self.cluster_name),
                               "builder_path": '%s/%s/swift/%s.builder' % (self.swift_path, self.cluster_name, 'object-%s'%policy_num)})))
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from remove disk slowly ip:%s device:%s ring:%s' % (content,
                                                                                        ip,
                                                                                        disk_device,
                                                                                        ring_name if not policy else 'Object-%s'%policy_num))
            raise IOError('Error %s from remove disk slowly ip:%s device:%s ring:%s' % (content,
                                                                                        ip,
                                                                                        disk_device,
                                                                                        ring_name if not policy else 'Object-%s'%policy_num))
        return content

    def rebalance(self, policy=False, ring_name='', policy_num=''):
        if not policy:
            content = self.excute_cmd(str('sh {script_path}/ringmanage.sh {ring_name} rebalance {builder_path}'
                                          .format(**{'ring_name': ring_name,
                                                     "script_path": SCRIPT_PATH,
                                                     "builder_path": '%s/%s/swift/%s.builder' % (
                                                            self.swift_path, self.cluster_name, ring_name)})))
        else:
            content = self.excute_cmd(str('sh {script_path}/ringmanage.sh policy {policy_num} rebalance {swift_conf_path} {builder_path}'
                                          .format(**{'policy_num': policy_num,
                                                     "script_path": SCRIPT_PATH,
                                                     "swift_conf_path": '%s/%s/swift/swift.conf' % (
                                                                    self.swift_path, self.cluster_name),
                                                     "builder_path": '%s/%s/swift/%s.builder' % (
                                                                    self.swift_path, self.cluster_name, 'object-%s' % policy_num)
                                                     })))
        access_logger.info('Rebalance %s Ring %s' % (ring_name, content))
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from rebalance ring:%s' % (content, ring_name if not policy else 'Object-%s' % policy_num))
            raise IOError('Error %s from rebalance ring:%s' % (content, ring_name if not policy else 'Object-%s' % policy_num))

        return content

    def set_weight(self, weight, disk_device, ip, port, policy=False, ring_name='', policy_num=''):
        if not policy:
            content = self.excute_cmd(str('sh {script_path}/ringmanage.sh {ring_name} setweight {ip}:{port}/{device} {weight} {builder_path}'
                                          .format(**{'ring_name': ring_name,
                                                     'device': disk_device,
                                                     'weight': weight,
                                                     "ip": ip,
                                                     "port": port,
                                                     "script_path": SCRIPT_PATH,
                                                     "builder_path": '%s/%s/swift/%s.builder' % (
                                                         self.swift_path, self.cluster_name, ring_name)
                                                     })))
        else:
            content = self.excute_cmd(
                str('sh {script_path}/ringmanage.sh policy {policy_num} setweight {ip}:{port}/{device} {weight} {swift_conf_path} {builder_path}'
                    .format(**{'policy_num': policy_num,
                               'device': disk_device,
                               'weight': weight,
                               "ip": ip,
                               "port": port,
                               "script_path": SCRIPT_PATH,
                               "swift_conf_path": '%s/%s/swift/swift.conf' % (
                                   self.swift_path, self.cluster_name),
                               "builder_path": '%s/%s/swift/%s.builder' % (
                                   self.swift_path, self.cluster_name, 'object-%s' % policy_num)
                               })))
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.info('Error %s from set weight=%s ip:%s device:%s ring:%s'%(content, weight, ip, disk_device, ring_name if not policy else 'Object-%s'%policy_num))
            raise IOError('Error %s from set weight=%s ip:%s device:%s ring:%s'%(content, weight, ip, disk_device, ring_name if not policy else 'Object-%s'%policy_num))
        return content

    def give_away_ring_to_host(self, host, ring_file, cp_file_path='/etc/swift'):
        node = SfoClusterNodesMethod.query_host_by_host_name(host)
        if node:
            client = ClusterClient(node.node_inet_ip, 7202, filepath='%s/%s/swift/%s'%(self.swift_path, self.cluster_name, ring_file))
            asyncore.loop(map=client._map)
            try:
                if client.buffer:
                    content = json.loads(client.buffer)
                    if content == '__wait__':
                        content = 'Connection Error'
                    elif content['result'] == "File receive compeled":
                        content = 'Send File Success'
                    else:
                        content = 'Send File Fail'
                else:
                    content = 'Send File Fail'
            except (ValueError, TypeError):
                content = 'Send File Fail'
            del client
            if content == 'Send File Fail' or content == 'Connection Error':
                access_logger.info('%s send file %s' % (host, content))
                raise IOError('%s send file %s' % (host, content))
            else:
                if not compare_remote_host_md5(file='%s/%s/swift/%s' % (self.swift_path, self.cluster_name, ring_file),
                                               host=node.node_inet_ip):
                    raise IOError('Inconsistent document comparison')
            sw_con = SwiftConfig(PROXY_HOST_IP)
            content = sw_con.chmod(644, ring_file, config.temp_file, host=node.node_inet_ip)
            if content == 'Excute Cmd Fail' or content == 'Connection Error':
                access_logger.info('%s change mode %s' % (host, content))
                raise IOError('%s change mode %s' % (host, content))
            content = sw_con.copy(config.temp_file, cp_file_path, ring_file, host=node.node_inet_ip)
            if content == 'Excute Cmd Fail' or content == 'Connection Error':
                access_logger.error('%s copy file %s' % (host, content))
                raise IOError('%s copy file %s' % (host, content))
            return content
        else:
            content = 'Not Found Host %s '%host
            return content

    def give_away_ring(self, cluster_name, ring_file):
        nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
        content_list = []
        for node in nodes:
            count = 0
            while count < 3:
                try:
                    content = self.give_away_ring_to_host(node.node_host_name, ring_file)
                    _ring_builder = ring_file.split('.')[0]
                    ring_builder = _ring_builder + '.builder'
                    content = self.give_away_ring_to_host(node.node_host_name, ring_builder)
                except Exception, error:
                    content = str(error)
                    count += 1
                else:
                    if content == 'Excute Cmd Success':
                        content = 'Success'
                        count += 3
                    else:
                        content = 'Unkown Error'
                        count += 1
            else:
                content_list.append('Host:%s  Result:%s' % (node.node_inet_ip, content))
        else:
            file_path = '%s/%s/swift/%s'%(self.swift_path, self.cluster_name, ring_file)
            SfoCofigureMethod.update_ring_md5(file_path, self.cluster_name)
        return '/'.join(content_list)

    def ring_info(self, ring_name):
        ring_name = ring_name.split('.')[0]
        content = self.excute_cmd(str('swift-ring-builder %s/%s/swift/%s.builder|awk "NR!=1&&NR!=4&&NR!=5{print}"'%(self.swift_path, self.cluster_name, ring_name )))
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.error('Error %s from get %s ring_info' % (content, ring_name))
            raise IOError('Error %s from get %s ring_info' % (content, ring_name))
        return content

    def rings(self):
        ring_map = {}
        cmd = "ls %s/%s/swift |grep 'builder'" % (self.swift_path, self.cluster_name)
        builders = self.excute_cmd(cmd, host=PROXY_HOST_IP)
        if builders == 'Excute Cmd Fail' or builders == 'Excute Cmd Success' or builders == 'Connection Error':
            access_logger.error('Exception %s from get builders' % builders)
            raise IOError('Exception %s from get builders' % builders)
        builders = builders.split('\n')
        for builder in builders:
            try:
                _builder = RingBuilder.load('%s/%s/swift/%s' % (self.swift_path, self.cluster_name, builder))
                if _builder:
                    ring_name = builder.replace('.builder', '.ring.gz')
                    ring_map.update({ring_name: {"replicas": _builder.replicas,
                                                 "part_power": pow(2, int(_builder.part_power)),
                                                 "min_part_hours": _builder.min_part_hours}})
            except SwiftException, error:
                access_logger.error(str(error))
        return ring_map

    def used_map(self, cluster_name):
        """
        获取已在集群中的磁盘列表
        :return:
        """
        builder_map = {}
        swift_config_dir = os.path.join(config.sfo_server_temp_file, 'etc')
        cmd = "ls %s/%s/swift |grep 'builder'"%(swift_config_dir, cluster_name)
        builders = self.excute_cmd(cmd, host=PROXY_HOST_IP)
        if builders == 'Excute Cmd Fail' or builders == 'Excute Cmd Success' or builders == 'Connection Error':
            access_logger.error('Exception %s from get builders' % builders)
            raise IOError('Exception %s from get builders' % builders)
        builders = builders.split('\n')
        for builder in builders:
            try:
                _builder = RingBuilder.load('%s/%s/swift/%s'% (swift_config_dir, cluster_name,builder))
                used_disk_label_lists = []
                if _builder.devs:
                    hosts = _builder.devs
                    for host_label in hosts:
                        label = host_label['device']
                        host_ip = host_label['ip']
                        if host_ip in map(lambda x: x['host_ip'], used_disk_label_lists):
                            for idx, _host_ip in enumerate(map(lambda x: x['host_ip'], used_disk_label_lists)):
                                if host_ip == _host_ip:
                                    used_disk_label_lists[idx]['labels'].append(label)
                        else:
                            used_host_label_map = {"host_ip": host_ip, "labels": [label]}
                            used_disk_label_lists.append(used_host_label_map)
                    if used_disk_label_lists:
                        builder_map.update({builder.replace('builder', 'ring.gz'): used_disk_label_lists})
            except SwiftException, error:
                access_logger.error(str(error))
        return builder_map


class DiskOperation:

    disk_prefix = '/dev/sd'

    def __init__(self, host, inet_host):
        self.host = host
        self.inet_host = inet_host
        self.cmd_port = 7201

    def excute_cmd(self, message, host=None):
        socket_client = ClusterClient(host if host else self.host, self.cmd_port)
        socket_client.message = '%s' % message
        asyncore.loop(map=socket_client._map)
        if socket_client.buffer:
            if socket_client.buffer == '__wait__':
                content = 'Connection Error'
            elif socket_client.buffer == 'SUCCESS':
                content = 'Excute Cmd Success'
            elif socket_client.buffer == 'Operation failed':
                content = 'Excute Cmd Fail'
            elif socket_client.buffer == 'FAILED':
                content = 'Excute Cmd Fail'
            else:
                content = copy.deepcopy(socket_client.buffer)
        else:
            content = 'Excute Cmd Fail'
        del socket_client
        return content

    def available_disks(self):
        """
        获取可用的磁盘列表
        :return:
        """
        avail_disk = []
        sys_disk_set = set()
        disk_stat_map = {"available": [], "abnormal": []}
        cmd = "df -l|grep /boot|awk '{print $1}'"
        system_disks = self.excute_cmd(cmd)
        if system_disks == 'Excute Cmd Fail' or system_disks == 'Excute Cmd Success' or system_disks == 'Connection Error':
            access_logger.error('Exception %s from system disks' % system_disks)
            raise IOError('Exception %s from system disks' % system_disks)
        else:
            sys_disks = system_disks.split('\n')
            for disk in sys_disks:
                sys_disk_re = re.compile('\D+')
                sys_result = sys_disk_re.search(disk)
                if sys_result:
                    sys_disk_set.add(sys_result.group())
        cmd = "cat /proc/partitions |grep sd |awk -v OFS='/' '{print \"/dev\",$4}'"
        disks = self.excute_cmd(cmd)
        if disks == 'Excute Cmd Fail' or disks == 'Excute Cmd Success' or disks == 'Connection Error':
            access_logger.error('Exception %s from available disks' % disks)
            raise IOError('Exception %s from available disks' % disks)
        else:
            disks = disks.split('\n')
            for disk in disks:
                is_system_disk = False
                for sysdisk in sys_disk_set:
                    cmp_disk_p = re.compile('^%s$|^%s\d+$' % (sysdisk, sysdisk))
                    cmp_result = cmp_disk_p.search(disk)
                    if cmp_result:
                        is_system_disk = True
                if is_system_disk:
                    continue
                else:
                    avail_disk.append(disk)
                cmd = "fdisk -l %s |grep 'Disk' |awk '{print $2}'|tr ':\n' ' '" % disk
                content = self.excute_cmd(cmd)
                if content == 'Excute Cmd Success' or not content:
                    disk_stat_map['abnormal'].append(disk)
                else:
                    disk_stat_map['available'].append(disk)
        return avail_disk, disk_stat_map

    def mounted_disks(self):
        """
        获取已挂载的磁盘列表
        :return:
        """
        mount_disk_list = []
        sys_disk_set = set()
        cmd = "df -l|grep /boot|awk '{print $1}'"
        system_disks = self.excute_cmd(cmd)
        if system_disks == 'Excute Cmd Fail' or system_disks == 'Excute Cmd Success' or system_disks == 'Connection Error':
            access_logger.error('Exception %s from system disks' % system_disks)
            raise IOError('Exception %s from system disks' % system_disks)
        else:
            sys_disks = system_disks.split('\n')
            for disk in sys_disks:
                sys_disk_re = re.compile('\D+')
                sys_result = sys_disk_re.search(disk)
                if sys_result:
                    sys_disk_set.add(sys_result.group())
        cmd = "mount -l |grep '/dev/sd'|awk -v OFS=' ' '{print $1,$3,$5,$6,$7}'"
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Excute Cmd Success' or content == 'Connection Error':
            access_logger.error('Exception %s from mounted disks' % content)
            raise IOError('Exception %s from mounted disks' % content)
        mounted_list = content.split('\n')
        mt_list = []
        for mt_disk in mounted_list:
            is_system_disk = False
            mount_info_list = mt_disk.split(' ')
            for sysdisk in sys_disk_set:
                cmp_disk_p = re.compile('^%s$|^%s\d+$' % (sysdisk, sysdisk))
                cmp_result = cmp_disk_p.search(mt_disk)
                if cmp_result:
                    is_system_disk = True
            if is_system_disk:
                continue
            else:
                mt_list.append(mt_disk)
            if len(mount_info_list) == 5:
                disk_name, mount_on, filesys, params, label = mount_info_list
            elif len(mount_info_list) == 4:
                disk_name, mount_on, filesys, params = mount_info_list
            else:
                disk_name = ''
            if disk_name:
                mount_disk_list.append(disk_name)
        return mount_disk_list, mt_list

    def xfs_format_disks(self):
        """
        获取已格式化的磁盘列表
        可用的磁盘列表中没有mount的disks就是没有格式化的
        cmd = file -s /dev/sd* |awk -F '[: ]+' -v OFS=' '  '{print $1,$3}'
        :return:
        """
        sys_disk_set = set()
        cmd = "df -l|grep /boot|awk '{print $1}'"
        system_disks = self.excute_cmd(cmd)
        if system_disks == 'Excute Cmd Fail' or system_disks == 'Excute Cmd Success' or system_disks == 'Connection Error':
            access_logger.error('Exception %s from system disks' % system_disks)
            raise IOError('Exception %s from system disks' % system_disks)
        else:
            sys_disks = system_disks.split('\n')
            for disk in sys_disks:
                sys_disk_re = re.compile('\D+')
                sys_result = sys_disk_re.search(disk)
                if sys_result:
                    sys_disk_set.add(sys_result.group())
        cmd = "file -s /dev/sd* |awk -F '[: ]+' -v OFS=' '  '{print $1,$3}'"
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Excute Cmd Success' or content == 'Connection Error':
            access_logger.error('Exception %s from get xfs format disks' % content)
            raise IOError('Exception %s from get xfs format disks' % content)
        format_lists = content.split('\n')
        fmt_list = []
        for fmt_disk in format_lists:
            is_system_disk = False
            for sysdisk in sys_disk_set:
                cmp_disk_p = re.compile('^%s$|^%s\d+$' % (sysdisk, sysdisk))
                _fmt_disk = fmt_disk.split(' ')[0]
                cmp_result = cmp_disk_p.search(_fmt_disk)
                if cmp_result:
                    is_system_disk = True
            if is_system_disk:
                continue
            else:
                fmt_list.append(fmt_disk)
        fmt_list = map(lambda x: x.split(' ')[0], filter(lambda x: 'XFS' in x, fmt_list))
        return fmt_list

    def add_disk(self, disk_name=''):
        disk = 'all' if not disk_name else disk_name
        cmd = str('sh %s/diskmanage.sh add %s' % (SCRIPT_PATH, disk))
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Connection Error' \
                or content == 'target disk device is null' \
                or content == 'there is no disk available on this server,please check it manual'\
                or content == 'the target disk is not exist,please check your input value.' \
                or content == 'Failed':
            access_logger.error('Exception %s from add disk' % content)
            raise IOError('Exception %s from add disk' % content)
        return content

    def delete_disk(self, disk_name=''):
        disk = 'all' if not disk_name else disk_name
        cmd = str('sh %s/diskmanage.sh delete %s' % (SCRIPT_PATH, disk))
        content = self.excute_cmd(cmd)
        if content == 'Excute Cmd Fail' or content == 'Connection Error' \
                or content == 'target disk device is null' \
                or content == 'no disk label found' \
                or content == 'the target disk is not exist,please check your input value.' \
                or content == disk_name + ' ' + 'Delete failed' \
                or content == disk_name + ' ' + 'unmount failed' \
                or content == disk_name + ' ' + 'not exist' \
                or content == disk_name + ' ' + 'unmounted':
            access_logger.error('Exception %s from delete disk' % content)
            raise IOError('Exception %s from delete disk' % content)
        return content


class PolicyManager:

    """
    策略管理只在代理主机上执行
    """
    def __init__(self, cluster_name):
        self.host = PROXY_HOST_IP
        self.cmd_port = 7201
        self.swift_path = os.path.join(config.sfo_server_temp_file, 'etc')
        self.cluster_name = cluster_name
        if not os.path.exists('%s/%s/swift' % (self.swift_path, self.cluster_name)):
            os.makedirs('%s/%s/swift' % (self.swift_path, self.cluster_name), mode=644)
        else:
            if not os.path.exists('%s/%s/swift/swift.conf' % (self.swift_path, self.cluster_name)):
                result = create_new_config_specify_file('swift.conf', '%s/%s/swift/' % (self.swift_path, self.cluster_name))
                if not result:
                    raise StandardError('Can not build swift.conf template ....')

    def excute_cmd(self, message, host=None):
        socket_client = ClusterClient(host if host else self.host, self.cmd_port)
        socket_client.message = '%s' % message
        asyncore.loop(map=socket_client._map)
        if socket_client.buffer:
            if socket_client.buffer == '__wait__':
                content = 'Connection Error'
            elif socket_client.buffer == 'SUCCESS':
                content = 'Excute Cmd Success'
            elif socket_client.buffer == 'Operation failed':
                content = 'Excute Cmd Fail'
            else:
                content = copy.deepcopy(socket_client.buffer)
        else:
            content = 'Excute Cmd Fail'
        del socket_client
        return content

    def add(self, num, name, deprecated='no', policy_type='replication'):

        content = self.excute_cmd(str('sh {script_path}/policymanage.sh add {num} {name} {deprecated} {policy_type} {swift_conf_path}'
                                      .format(**{'num': num,
                                                 'name': name,
                                                 "deprecated": deprecated,
                                                 "policy_type": policy_type,
                                                 "script_path": SCRIPT_PATH,
                                                 "swift_conf_path": '%s/%s/swift/swift.conf' % (self.swift_path, self.cluster_name)})))

        if content == 'Excute Cmd Fail' or content == 'Connection Error'\
                or content == 'can not ceate policy-0,please change your input value.'\
                or content == 'the policy NO. is exist,please input another one.' \
                or content == 'create policy failed.' \
                or content == 'you should input a number bigger than 0 ':
            access_logger.error('Parameters: clusterName:%s swift_path:%s Num:%s script_path:%s Name:%s deprecated:%s policy_type:%s' % (self.cluster_name, self.swift_path, num, SCRIPT_PATH, name, deprecated, policy_type))
            raise IOError('PolicyManager add method excute policymanage.sh add fail, result:%s'%content)
        else:
            self.give_away_swiftconf()
        return content

    def deprecate(self, num):

        content = self.excute_cmd(
            str('sh {script_path}/policymanage.sh del {num} {swift_conf_path}'
                .format(**{'num': num,
                           "script_path": SCRIPT_PATH,
                           "swift_conf_path": '%s/%s/swift/swift.conf' % (self.swift_path, self.cluster_name)})))

        if content == 'Excute Cmd Fail' or content == 'Connection Error' or content == 'no deprecated policy was found.':
            access_logger.error('Parameters: clusterName:%s swift_path:%s Num:%s script_path:%s' % (self.cluster_name, self.swift_path, num, SCRIPT_PATH))
            raise IOError('PolicyManager deprecate method excute policymanage.sh del fail, result:%s'%content)
        else:
            self.give_away_swiftconf()
        return content

    def check(self, num):

        content = self.excute_cmd(
            str('sh {script_path}/policymanage.sh check {num} {swift_conf_path}'
                .format(**{'num': num,
                           "script_path": SCRIPT_PATH,
                           "swift_conf_path": '%s/%s/swift/swift.conf' % (self.swift_path, self.cluster_name)})))

        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.error('Parameters: clusterName:%s swift_path:%s Num:%s script_path:%s' % (self.cluster_name, self.swift_path, num, SCRIPT_PATH))
            raise IOError('PolicyManager check method excute policymanage.sh check fail, result:%s'%content)
        return content

    def policys(self):
        policy_map = {}

        content = self.excute_cmd(
            str('cat %s/%s/swift/swift.conf | grep -e "storage-policy:"' % (self.swift_path, self.cluster_name)))
        if content == 'Excute Cmd Fail' or content == 'Connection Error':
            access_logger.error('Get Policys %s' % content)
            raise IOError('Get Policys %s' % content)
        _policys = content.split('\n')
        for policy in _policys:
            policy_cmp = re.compile('storage-policy:(\d+)')
            re_result = policy_cmp.search(policy)
            policy_num = re_result.groups()[0]
            content = self.check(policy_num)
            keyword_attrs = content.split('\n')
            policy_map.setdefault(policy_num, {})
            for attr in keyword_attrs:
                key, value = attr.split('=')
                policy_map[policy_num].update({key.strip(): value.strip()})
        return policy_map


    def give_away_file_to_host(self, host_name, filename, cp_file_path='/etc/swift'):
        node = SfoClusterNodesMethod.query_host_by_host_name(host_name)
        if node:
            client = ClusterClient(node.node_inet_ip, 7202,
                                   filepath='%s/%s/swift/%s' % (self.swift_path, self.cluster_name, filename))
            asyncore.loop(map=client._map)
            try:
                if client.buffer:
                    content = json.loads(client.buffer)
                    if content == '__wait__':
                        content = 'Connection Error'
                    elif content['result'] == "File receive compeled":
                        content = 'Send File Success'
                    else:
                        content = 'Send File Fail'
                else:
                    content = 'Send File Fail'
            except (TypeError, ValueError):
                content = 'Send File Fail'
            del client
            if content == 'Send File Fail' or content == 'Connection Error':
                access_logger.error('%s send file %s' % (host_name, content))
                raise IOError('%s send file %s' % (host_name, content))
            else:
                if not compare_remote_host_md5(file='%s/%s/swift/%s' % (self.swift_path, self.cluster_name, filename), host=node.node_inet_ip):
                    raise IOError('Inconsistent document comparison')
            sw_con = SwiftConfig(PROXY_HOST_IP)
            content = sw_con.chmod(644, filename, config.temp_file, host=node.node_inet_ip)
            if content == 'Excute Cmd Fail' or content == 'Connection Error':
                access_logger.error('%s change mode %s' % (host_name, content))
                raise IOError('%s change mode %s' % (host_name, content))
            content = sw_con.copy(config.temp_file, cp_file_path, filename, host=node.node_inet_ip)
            if content == 'Excute Cmd Fail' or content == 'Connection Error':
                access_logger.error('%s copy file %s' % (host_name, content))
                raise IOError('%s copy file %s' % (host_name, content))
            return content
        else:
            content = 'Not Found Host %s ' % host_name
            return content


    def give_away_swiftconf(self):
        nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(self.cluster_name)
        content_list = []
        for node in nodes:
            count = 0
            while count < 3:
                try:
                    content = self.give_away_file_to_host(node.node_host_name, 'swift.conf', '/etc/swift')
                except Exception, error:
                    content = str(error)
                    count += 1
                else:
                    if content == 'Excute Cmd Success':
                        content = 'Success'
                        count += 3
                    else:
                        content = 'Unkown Error'
                        count += 1
            else:
                content_list.append('Host:%s  Result:%s' % (node.node_inet_ip, content))
        else:
            file_path = '%s/%s/swift/%s' % (self.swift_path, self.cluster_name, 'swift.conf')
            SfoCofigureMethod.update_swiftconf_md5(file_path, self.cluster_name)
        return '/'.join(content_list)


class FileManager:

    def excute_cmd(self, message, host):
        socket_client = ClusterClient(host, 7201)
        socket_client.message = '%s' % (message)
        asyncore.loop(map=socket_client._map)
        if socket_client.buffer:
            if socket_client.buffer == '__wait__':
                content = 'Connection Error'
            elif socket_client.buffer == 'SUCCESS':
                content = 'Excute Cmd Success'
            elif socket_client.buffer == 'Operation failed':
                content = 'Excute Cmd Fail'
            else:
                content = copy.deepcopy(socket_client.buffer)
        else:
            content = 'Excute Cmd Fail'
        del socket_client
        return content

    def write_config(self, file, host):
        """
        向对象地址写入配置文件
        :return:
        """
        if os.path.exists(file):
            file_socket_client = ClusterClient(host, 7202, filepath=file)
            asyncore.loop(map=file_socket_client._map)
            try:
                if file_socket_client.buffer:
                    content = json.loads(file_socket_client.buffer)
                    if content == '__wait__':
                        content = 'Connection Error'
                    elif content['result'] == "File receive compeled":
                        content = 'Send File Success'
                    else:
                        content = 'Send File Fail'
                else:
                    content = 'Send File Fail'
            except Exception:
                content = 'Send File Fail'
            result = copy.deepcopy(content)
            del file_socket_client
            return result
        else:
            content = 'File Path %s Not Exists' % file
            return content

    def give_away_file_to_host(self, host, file, cp_file_path):
        node = SfoClusterNodesMethod.query_host_by_host_name(host)
        if node:
            content = self.write_config(file, node.node_inet_ip)
            if content == 'Send File Fail' or content == 'Connection Error':
                access_logger.error('%s send file %s' % (host, content))
                raise IOError('%s send file %s' % (host, content))
            else:
                if not compare_remote_host_md5(file=file, host=node.node_inet_ip):
                    raise IOError('Inconsistent document comparison')
            content = self.excute_cmd('cp %s/%s %s/%s' % (config.temp_file, os.path.basename(file), cp_file_path, os.path.basename(file)), node.node_inet_ip)
            if content == 'Excute Cmd Fail' or content == 'Connection Error':
                access_logger.error('%s copy file %s' % (host, content))
                raise IOError('%s copy file %s' % (host, content))
            return content
        else:
            content = 'Not Found Host %s ' % host
            return content

    def give_away_file_to_proxy(self, cluster_name, file):
        nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
        nodes = filter(lambda x: json.loads(x.node_role)['Proxy-Server'] == 'YES', nodes)
        content_list = []
        for node in nodes:
            count = 0
            while count < 3:
                try:
                    content = self.give_away_file_to_host(node.node_host_name, file, cp_file_path='/etc/swift')
                    access_logger.info('Connect to %s Send File %s, result:%s ' % (node.node_inet_ip, file, content))
                except Exception, error:
                    content = str(error)
                    count += 1
                    access_logger.warning('Try Connect to %s Send File %s again ,count:%s ' % (node.node_inet_ip, file, count))
                else:
                    if content == 'Excute Cmd Success':
                        content = 'Success'
                        count += 3
                    else:
                        count += 1
                        content = 'Unkown Error'
            else:
                content_list.append('Host:%s Result:%s' % (node.node_inet_ip, content))
        return '/'.join(content_list)


    def give_away_passwd_to_proxy(self, cluster_name, file):
        nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
        nodes = filter(lambda x: json.loads(x.node_role)['Proxy-Server'] == 'YES', nodes)
        content_list = []
        for node in nodes:
            count = 0
            while count < 3:
                try:
                    content = self.give_away_file_to_host(node.node_host_name, file, cp_file_path='/etc/swift')
                    access_logger.info('Connect to %s Send File %s, result:%s ' % (node.node_inet_ip, file, content))
                except Exception, error:
                    content = str(error)
                    count += 1
                    access_logger.warning('Try Connect to %s Send File %s again ,count:%s ' % (node.node_inet_ip, file, count))
                else:
                    if content == 'Excute Cmd Success':
                        content = 'Success'
                        count += 3
                    else:
                        count += 1
                        content = 'Unkown Error'
            else:
                content_list.append('Host:%s Result:%s' % (node.node_inet_ip, content))
        else:
            SfoCofigureMethod.update_passwd_md5(file, cluster_name)
            for proxy in nodes:
                try:
                    collection_info = SfoHostRingMethod.query_last_collection_info(proxy.node_host_name)
                    if collection_info:
                        extend_passwd = json.loads(collection_info.extend)
                        cmdstr = 'md5sum /etc/swift/passwd'
                        content = self.excute_cmd(cmdstr, host=proxy.node_inet_ip)
                        if content == 'Excute Cmd Success' or content == 'Excute Cmd Fail' \
                                or content == 'Connection Error':
                            raise IOError('Can\'t update %s passwd md5' % proxy.node_inet_ip)
                        else:
                            _passwd_md5 = str(content).split(' ')
                            passwd_md5 = _passwd_md5[0]
                            if extend_passwd.get('passwdmd5'):
                                extend_passwd['passwdmd5'] = passwd_md5
                                collection_info.extend = json.dumps(extend_passwd)
                                db.session.add(collection_info)
                except IOError, error:
                    access_logger.error(error)
            db.session.commit()
        return '/'.join(content_list)


if __name__ == '__main__':
    pass
