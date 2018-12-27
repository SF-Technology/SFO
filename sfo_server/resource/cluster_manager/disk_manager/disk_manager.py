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
from sfo_server.models import SfoClusterNodesMethod
from flask_restful import Resource, marshal_with, fields
from sfo_server.resource.common import timestamp_format, RecuDictField, _pickle_method
from sfo_server.manager_class import DiskOperation, RingManager
from sfo_server import access_logger
from multiprocessing import Pool
from sfo_server.decorate import login_required, permission_required
import copy_reg, types
copy_reg.pickle(types.MethodType, _pickle_method)

disk_list_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "host_name": fields.String,
        "host_ip": fields.String,
        "disk_name": fields.String,
        "system_type": fields.String,
        "is_xfs_format": fields.String,
        "is_used": RecuDictField(),
        "is_abnormal": fields.String,
        "is_mount": fields.String,
        "mount_on": fields.String,
        "mount_params": fields.String,
        "label": fields.String,
    }))
}


class DiskInformation:

    def __init__(self, disk_name, host_name, host_ip, host_re_ip):
        self.disk_name = disk_name
        self.host_name = host_name
        self.host_ip = host_ip
        self.host_re_ip = host_re_ip
        self.is_abnormal = '0'
        self.is_mount = '0'
        self.is_used = []
        self.is_xfs_format = '0'
        self.label = ''
        self.mount_on = ''
        self.mount_params = ''
        self.system_type = ''
        self.message = ''

    def __repr__(self):
        return '<DiskInfomation %s>'%self.disk_name


def async_disk_operation(node):
    data = []
    disk_op = DiskOperation(node.node_inet_ip, node.node_replicate_ip)
    try:
        available_list, disk_stat_map = disk_op.available_disks()
        abnormal_list = disk_stat_map['abnormal']
        xfs_fmt_list = disk_op.xfs_format_disks()
        mount_list, mt_info_list = disk_op.mounted_disks()
        for disk in available_list:
            disk_ = DiskInformation(disk, node.node_host_name, node.node_inet_ip, node.node_replicate_ip)
            data.append(disk_)
        for _disk in data:
            if _disk.host_name != node.node_host_name:
                continue
            if _disk.disk_name in abnormal_list:
                _disk.is_abnormal = '1'
            if _disk.disk_name in xfs_fmt_list:
                _disk.is_xfs_format = '1'
            if _disk.disk_name in mount_list:
                _disk.is_mount = '1'
                for mtinfo in mt_info_list:
                    if _disk.disk_name in mtinfo:
                        disk_mt_info = mtinfo.split(' ')
                        if len(disk_mt_info) == 5:
                            _disk.mount_on = disk_mt_info[1]
                            _disk.system_type = disk_mt_info[2]
                            _disk.mount_params = disk_mt_info[3]
                            _disk.label = disk_mt_info[4].replace('[', '').replace(']', '')
                        else:
                            _disk.mount_on = disk_mt_info[1]
                            _disk.system_type = disk_mt_info[2]
                            _disk.mount_params = disk_mt_info[3]
        return data
    except Exception, error:
        access_logger.error('Collect %s Disk Information Fail, Reason:%s '% (node.node_host_name, str(error)))


def get_disk_list(cluster_name):
    """
    获取节点磁盘列表
    :param cluster_name:
    :return:
    """
    sfo_disks = []
    apply_result_list = []
    status = ''
    message = {}
    resp = {"status": status, "data": sfo_disks, "message": message}
    sfo_node = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name=cluster_name)
    rm = RingManager(cluster_name)
    try:
        ring_host_label_map = rm.used_map(cluster_name)
    except IOError:
        ring_host_label_map = {}
    pool = Pool(25)
    for node in sfo_node:
        apply_result = pool.apply_async(func=async_disk_operation, args=(node,))
        apply_result_list.append(apply_result)
    pool.close()
    pool.join()
    for apply_result in apply_result_list:
        apply_result_data = apply_result.get(timeout=1)
        if apply_result_data:
            for ring_name, ring_info in ring_host_label_map.items():
                for disk_infomation in apply_result_data:
                    for host_labels_dict in ring_info:
                        if (disk_infomation.host_ip == host_labels_dict['host_ip'] or disk_infomation.host_re_ip == host_labels_dict['host_ip']) and disk_infomation.label in host_labels_dict['labels']:
                            disk_infomation.is_used.append(ring_name)
            sfo_disks.extend(apply_result_data)
    if sfo_disks:
        status = 200
        message = 'OK'
        sfo_disks = sorted(sfo_disks, key=lambda x: x.host_name)
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": sfo_disks, "message": message})
    return resp, status


def mount_disk_2node(host_name, disk_name):
    """
    添加磁盘的操作
        1.格式化
        2.挂载
        3. 添加到环   ###未实现
    :param host_name: 主机名
    :param disk_name: 磁盘名
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_node = SfoClusterNodesMethod.query_host_by_host_name(host_name)
    if not sfo_node:
        raise ValueError('Not Found Node Host %s' % host_name)
    disk_op = DiskOperation(sfo_node.node_inet_ip, sfo_node.node_replicate_ip)
    try:
        disk_name = disk_name if disk_name else 'all'
        content = disk_op.add_disk(disk_name)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 200
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


def umount_disk_2node(host_name, disk_name):
    """
    删除磁盘的操作
    :param host_name: 主机名
    :param disk_name: 磁盘名
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_node = SfoClusterNodesMethod.query_host_by_host_name(host_name)
    if not sfo_node:
        raise ValueError('Not Found Node Host %s' % host_name)
    disk_op = DiskOperation(sfo_node.node_inet_ip, sfo_node.node_replicate_ip)
    try:
        disk_name = disk_name if disk_name else 'all'
        content = disk_op.delete_disk(disk_name)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 200
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterDiskManagerApi(Resource):

    resource = (SfoClusterNodesMethod, )

    @login_required
    @permission_required(*resource)
    @marshal_with(disk_list_resource_fields)
    def get(self, cluster_name):
        try:
            resp, status = get_disk_list(cluster_name)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def post(self, cluster_name):
        try:
            datajson = request.json
            host_name = datajson.get('host_name')
            disk_name = datajson.get('disk_name')
            if not host_name:
                raise ValueError('host_name not allow null')
            resp, status = mount_disk_2node(host_name, disk_name)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def delete(self, cluster_name):
        try:
            datajson = request.json
            host_name = datajson.get('host_name')
            disk_name = datajson.get('disk_name')
            if not host_name:
                raise ValueError('host_name not allow null')
            resp, status = umount_disk_2node(host_name, disk_name)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status