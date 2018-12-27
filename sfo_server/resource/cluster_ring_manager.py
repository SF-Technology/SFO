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

from flask import request
from sfo_server import access_logger
from sfo_common.config_parser import Config
from sfo_server.manager_class import RingManager
from sfo_server.models import (SfoClusterNodesMethod)
from flask_restful import Resource,  marshal_with, fields
from sfo_server.decorate import access_log_decorate, login_required, permission_required

config = Config()

ring_fields_map = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "guid": fields.String,
        "cluster_name": fields.String,
        "ring_name": fields.String,
        "part_power": fields.String,
        "replicas": fields.String,
        "min_part_hours": fields.String,
        "add_time": fields.String,
    }))
}


def get_ring_info(cluster_name, ring_name):
    status = ''
    message = ''
    data = ''
    resp = {"status": status, "data": data, "message": message}
    rm = RingManager(cluster_name)
    try:
        content = rm.ring_info(ring_name)
        status = 200
        message = 'OK'
        data = content
    except IOError, error:
        status = 500
        message = str(error)
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def get_ring_list(cluster_name):
    """
    获取环列表
    :param cluster_name:
    :return:
    """
    data = []
    sfo_rings = []
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    rm = RingManager(cluster_name=cluster_name)
    try:
        ring_map = rm.rings()
    except Exception:
        ring_map = {}
    for ring_name in ring_map:
        sfo_rings.append({"cluster_name": cluster_name,
                          "ring_name": ring_name,
                          "replicas": ring_map[ring_name].get('replicas'),
                          "part_power": ring_map[ring_name].get('part_power'),
                          "min_part_hours": ring_map[ring_name].get('min_part_hours'),
                          })
    if sfo_rings:
        status = 200
        message = 'OK'
        data = sfo_rings
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def add_ring_2cluster(cluster_name, ringjson):
    """
    添加环数据到数据库
    :param ringjson:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    policy_num = ''
    replicas = ringjson.get('replicas')
    part_power = ringjson.get('part_power')
    ring_name = ringjson.get('ring_name')
    ring_name = ring_name if ring_name.endswith('.ring.gz') else ring_name + '.ring.gz'
    if 'object-' in ring_name:
        obj_ring, policy_num = ring_name.rstrip('.ring.gz').split('-')
    min_part_hours = ringjson.get('min_part_hours')
    sfo_clu_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    if not sfo_clu_nodes:
        raise ValueError('Not Master Node in %s' % cluster_name)
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
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 201
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


def add_disk_cluster(cluster_name, datajson):
    """
        向环中添加磁盘
        :param ringjson:
        :return:
        """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    policy_num = ''
    ip = datajson.get('ip')
    port = datajson.get('port')
    zone = datajson.get('zone')
    device = datajson.get('device')
    weight = datajson.get('weight')
    region = datajson.get('region')
    ring_name = datajson.get('ring_name')
    ring_name = ring_name if ring_name.endswith('.ring.gz') else ring_name + '.ring.gz'
    if 'object-' in ring_name:
        obj_ring, policy_num = ring_name.rstrip('.ring.gz').split('-')
    replication_ip = datajson.get('replication_ip')
    replication_port = datajson.get('replication_port')
    sfo_clu_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    if not sfo_clu_nodes:
        raise ValueError('Not Master Node in %s' % cluster_name)
    # 建立task 任务
    rm = RingManager(cluster_name)
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.add_disk_2_ring(ring_name=ring_name,
                                         region=region,
                                         zone=zone,
                                         ip=ip,
                                         port=port,
                                         disk_device=device,
                                         weight=weight,
                                         replication_ip=replication_ip,
                                         replication_port=replication_port)
        else:
            content = rm.add_disk_2_ring(region=region,
                                         zone=zone,
                                         ip=ip,
                                         port=port,
                                         disk_device=device,
                                         weight=weight,
                                         replication_ip=replication_ip,
                                         replication_port=replication_port,
                                         policy=True,
                                         policy_num=policy_num)

    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 201
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


def remove_disk_imm(cluster_name, datajson):
    """
    向环中立即删除磁盘
    :param ringjson:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    policy_num = ''
    ip = datajson.get('ip')
    port = datajson.get('port')
    device = datajson.get('device')
    ring_name = datajson.get('ring_name')
    ring_name = ring_name if ring_name.endswith('.ring.gz') else ring_name + '.ring.gz'
    if 'object-' in ring_name:
        obj_ring, policy_num = ring_name.rstrip('.ring.gz').split('-')
    sfo_clu_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    if not sfo_clu_nodes:
        raise ValueError('Not Master Node in %s' % cluster_name)
    # 建立task 任务
    rm = RingManager(cluster_name)
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.remove_disk_immediately(ring_name=ring_name,
                                                 disk_device=device,
                                                 ip=ip,
                                                 port=port)
        else:
            content = rm.remove_disk_immediately(disk_device=device,
                                                 ip=ip,
                                                 port=port,
                                                 policy=True,
                                                 policy_num=policy_num)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 201
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


def remove_disk_grad(cluster_name, datajson):
    """
    向环中逐渐删除磁盘
    :param ringjson:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    policy_num = ''
    ip = datajson.get('ip')
    port = datajson.get('port')
    weight = datajson.get('weight')
    device = datajson.get('device')
    ring_name = datajson.get('ring_name')
    ring_name = ring_name if ring_name.endswith('.ring.gz') else ring_name + '.ring.gz'
    if 'object-' in ring_name:
        obj_ring, policy_num = ring_name.rstrip('.ring.gz').split('-')
    sfo_clu_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    if not sfo_clu_nodes:
        raise ValueError('Not Master Node in %s' % cluster_name)
    # 建立task 任务
    rm = RingManager(cluster_name)
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.remove_disk_slowly(ring_name=ring_name,
                                            weight=weight,
                                            disk_device=device,
                                            ip=ip,
                                            port=port)
        else:
            content = rm.remove_disk_slowly(weight=weight,
                                            policy=True,
                                            disk_device=device,
                                            ip=ip,
                                            port=port,
                                            policy_num=policy_num)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 201
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


def set_weight(cluster_name, datajson):
    """
    更改环的权重
    :param ringjson:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    policy_num = ''
    ip = datajson.get('ip')
    port = datajson.get('port')
    weight = datajson.get('weight')
    device = datajson.get('device')
    ring_name = datajson.get('ring_name')
    ring_name = ring_name if ring_name.endswith('.ring.gz') else ring_name + '.ring.gz'
    if 'object-' in ring_name:
        obj_ring, policy_num = ring_name.rstrip('.ring.gz').split('-')
    sfo_clu_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    if not sfo_clu_nodes:
        raise ValueError('Not Master Node in %s' % cluster_name)
    rm = RingManager(cluster_name)
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.set_weight(ring_name=ring_name,
                                    weight=weight,
                                    disk_device=device,
                                    ip=ip,
                                    port=port)
        else:
            content = rm.set_weight(policy_num=policy_num,
                                    weight=weight,
                                    disk_device=device,
                                    ip=ip,
                                    port=port,
                                    policy=True)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 201
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


def rebalance(cluster_name, datajson):
    """
    平衡环
    :param datajson:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    policy_num = ''
    ring_name = datajson.get('ring_name')
    ring_name = ring_name if ring_name.endswith('.ring.gz') else ring_name + '.ring.gz'
    if 'object-' in ring_name:
        obj_ring, policy_num = ring_name.rstrip('.ring.gz').split('-')
    sfo_clu_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    if not sfo_clu_nodes:
        raise ValueError('Not Master Node in %s' % cluster_name)
    # 建立task 任务
    rm = RingManager(cluster_name)
    try:
        if not policy_num:
            ring_name = ring_name.split('.')[0]
            content = rm.rebalance(ring_name=ring_name)
        else:
            content = rm.rebalance(policy_num=policy_num,
                                   policy=True)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 201
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


def give_away_ring(cluster_name, datajson):
    """
        平衡环
        :param datajson:
        :return:
        """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    ring_name = datajson.get('ring_name')
    ring_name = ring_name if ring_name.endswith('.ring.gz') else ring_name + '.ring.gz'
    sfo_clu_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    if not sfo_clu_nodes:
        raise ValueError('Not Master Node in %s' % cluster_name)
    rm = RingManager(cluster_name)
    try:
        content = rm.give_away_ring(cluster_name=cluster_name,
                                    ring_file=ring_name)
    except Exception, error:
        message = str(error)
        status = 501
    else:
        status = 201
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterRingManagerApi(Resource):

    resource = (SfoClusterNodesMethod, )

    @login_required
    @permission_required(*resource)
    @marshal_with(ring_fields_map)
    def get(self, cluster_name):
        try:
            resp, status = get_ring_list(cluster_name)
            return resp, status
        except ValueError, error:
            access_logger.error('GET ClusterRingManagerApi get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('GET ClusterRingManagerApi get exception %s' % error)
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def post(self, cluster_name):
        try:
            datajson = request.json
            if not datajson.get('ring_name'):
                raise ValueError('ring_name not allow null')
            resp, status = add_ring_2cluster(cluster_name, datajson)
            return resp, status
        except ValueError, error:
            access_logger.error('POST ClusterRingManagerApi get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('POST ClusterRingManagerApi get exception %s' % error)
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def put(self, cluster_name):
        try:
            datajson = request.json
            operation = datajson.get('operation', '')
            if not operation:
                raise ValueError('select opertaion in [add_disk_cluster/remove_disk_imm/remove_disk_grad/rebalance/give_away_ring]')
            if not datajson.get('ring_name'):
                raise ValueError('ring_name not allow null')
            if operation == 'add_disk_cluster':
                if not (datajson.get('region') and datajson.get('zone')
                        and datajson.get('weight') and datajson.get('device')
                        and datajson.get('ip') and datajson.get('port')):
                    raise ValueError('port/ip/region/zone/weight/device not allow null')
                resp, status = add_disk_cluster(cluster_name, datajson)
            elif operation == 'remove_disk_imm':
                if not (datajson.get('device') and datajson.get('ip') and datajson.get('port')):
                    raise ValueError('device/ip/port not allow null')
                resp, status = remove_disk_imm(cluster_name, datajson)
            elif operation == 'remove_disk_grad':
                if not (datajson.get('weight') and datajson.get('device') and datajson.get('ip') and datajson.get('port')):
                    raise ValueError('weight/device/ip/port not allow null')
                resp, status = remove_disk_grad(cluster_name, datajson)
            elif operation == 'set_weight':
                if not (datajson.get('weight') and datajson.get('device') and datajson.get('ip') and datajson.get('port')):
                    raise ValueError('weight/device/ip/port not allow null')
                resp, status = set_weight(cluster_name, datajson)
            elif operation == 'rebalance':
                resp, status = rebalance(cluster_name, datajson)
            elif operation == 'give_away_ring':
                resp, status = give_away_ring(cluster_name, datajson)
            else:
                raise ValueError('select opertaion in [add_disk_cluster/remove_disk_imm/remove_disk_grad/rebalance]')
            return resp, status
        except ValueError, error:
            access_logger.error('PUT ClusterRingManagerApi get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('PUT ClusterRingManagerApi get exception %s' % error)
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status


class ClusterRingManagerDetailApi(Resource):

    resource = (SfoClusterNodesMethod,)

    @login_required
    @permission_required(*resource)
    def get(self, cluster_name):
        try:
            ring_name = request.args.get('ring_name')
            resp, status = get_ring_info(cluster_name, ring_name)
            return resp, status
        except ValueError, error:
            access_logger.error('GET ClusterRingManagerDetailApi get exception %s ' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('GET ClusterRingManagerDetailApi get exception %s' % error)
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

