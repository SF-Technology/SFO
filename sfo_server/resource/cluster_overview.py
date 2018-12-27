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


import time
import json
from sfo_server import access_logger
from flask_restful import Resource, marshal_with, fields,  request
from sfo_server.models import (SfoClusterInfoMethod,
                               SfoClusterNodesMethod,
                               SfoDiskPerformMethod,
                               SfoNodeStatMethod,
                               SfoNodeStat5MinMethod,
                               SfoNodeStatDayMethod,
                               SfoNodeStatHourMethod,
                               SfoNodePerformMethod)
from sfo_server.decorate import access_log_decorate, login_required, permission_required
from sfo_server.resource.common import used_time, RecuDictField, timestamp_format, group_data, is_less_than_nhours

cluster_overview_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "capacity_total": RecuDictField,
    })
}

cluster_mem_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({"cluster_mem_total_rate_avg": RecuDictField})
}

cluster_cpu_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({"cpu_frequency_val": RecuDictField})
}

cluster_storage_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({"storage": RecuDictField})
}

cluster_proxy_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({"proxy": RecuDictField})
}

cluster_band_width_fileds = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "band_used": fields.List(fields.String),
        "band_rep_used": fields.List(fields.String),
        "add_time": fields.List(fields.String)
    })
}

cluster_disk_performance_fileds = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "host_name": fields.String(attribute='host_name'),
        "disk_name": fields.String(attribute='disk_name'),
        "disk_total": fields.String(attribute='disk_total'),
        "disk_used": fields.String(attribute='disk_used'),
        "disk_percent": fields.String(attribute='disk_percent'),
        "add_time": fields.String(attribute='add_time'),
    })),
    "disk_num_total": fields.String
}

cluster_node_performance_fileds = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "host_name": fields.String,
        "account_replication": RecuDictField,
        "container_replication": RecuDictField,
        "object_replication": RecuDictField,
        "object_updater": RecuDictField
    }))
}


def server_net_used(node_list, starttime, endtime):
    send_bytes = []
    recv_bytes = []
    if is_less_than_nhours(starttime, endtime, 1):
        region = 60
        data, host_name_list = SfoNodeStatMethod.query_net_used_by_cluster_name(node_list, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 8):
        region = 600
        data, host_name_list = SfoNodeStat5MinMethod.query_net_used_by_cluster_name(node_list, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24):
        region = 7200
        data, host_name_list = SfoNodeStatHourMethod.query_net_used_by_cluster_name(node_list, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24*7):
        region = 86400
        data, host_name_list = SfoNodeStatHourMethod.query_net_used_by_cluster_name(node_list, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24*31):
        region = 86400*30
        data, host_name_list = SfoNodeStatDayMethod.query_net_used_by_cluster_name(node_list, starttime, endtime)
    else:
        region = 86400*365
        data, host_name_list = SfoNodeStatDayMethod.query_net_used_by_cluster_name(node_list, starttime, endtime)
    dot_group_list, region_time_list = group_data(data, region)
    for i in dot_group_list:
        try:
            cluster_net_total_send, cluster_net_total_recv = i.server_net_used()
            cluster_net_total_send = round(cluster_net_total_send/region, 2)
            cluster_net_total_recv = round(cluster_net_total_recv/region, 2)
        except Exception:
            send_bytes.append('N/A')
            recv_bytes.append('N/A')
        else:
            send_bytes.append(cluster_net_total_send)
            recv_bytes.append(cluster_net_total_recv)
    return send_bytes, recv_bytes, region_time_list


def get_proxy_net_used_logic(cluster_name, starttime, endtime):
    data = {}
    proxy = {}
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    proxy_node_list, storage_node_list = SfoClusterNodesMethod.category_node_list(cluster_name)  # 获取proxy、storage节点主机列表
    if proxy_node_list:
        try:
            send_bytes, recv_bytes, add_time = server_net_used(proxy_node_list, starttime, endtime)
            if add_time:
                status = 200
                message = 'OK'
                proxy.update({'send_bytes': send_bytes, "recv_bytes": recv_bytes, "add_time": add_time})
            else:
                status = 404
                message = 'Proxy Node Not Found Record'
        except Exception, error:
            status = 501
            message = 'get exception %s from proxy net used'%str(error)
    else:
        status = 404
        message = 'Null Proxy Node Found'
    data.update({"proxy": proxy})
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def get_storage_net_used_logic(cluster_name, starttime, endtime):
    data = {}
    status = ''
    message = ''
    storage = {}
    resp = {"status": status, "data": data, "message": message}
    proxy_node_list, storage_node_list = SfoClusterNodesMethod.category_node_list(cluster_name)  # 获取proxy、storage节点主机列表
    if storage_node_list:
        try:
            send_bytes, recv_bytes, add_time = server_net_used(storage_node_list, starttime, endtime)
            if add_time:
                status = 200
                message = 'OK'
                storage.update({'send_bytes': send_bytes, "recv_bytes": recv_bytes, "add_time": add_time})
            else:
                status = 404
                message = 'Storage Node Not Found Record'
        except Exception, error:
            status = 501
            message = 'get exception %s from storage net used' % str(error)
    else:
        status = 404
        message = 'Null Storage Node Found'
    data.update({"storage": storage})
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def get_avg_mem_used_rate_logic(cluster_name, starttime, endtime):
    _data = {}
    status = ''
    message = ''
    cluster_mem_total_rate_avg = {}
    resp = {"status": status, "data": _data, "message": message}
    if is_less_than_nhours(starttime, endtime, 1):
        region = 60
        data, host_name_list = SfoNodeStatMethod.query_node_mem_info(cluster_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 8):
        region = 600
        data, host_name_list = SfoNodeStat5MinMethod.query_node_mem_info(cluster_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24):
        region = 7200
        data, host_name_list = SfoNodeStatHourMethod.query_node_mem_info(cluster_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24*7):
        region = 86400
        data, host_name_list = SfoNodeStatHourMethod.query_node_mem_info(cluster_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24*31):
        region = 86400*30
        data, host_name_list = SfoNodeStatDayMethod.query_node_mem_info(cluster_name, starttime, endtime)
    else:
        region = 86400*365
        data, host_name_list = SfoNodeStatDayMethod.query_node_mem_info(cluster_name, starttime, endtime)
    if data and host_name_list:
        try:
            dot_list = []
            dot_group_list, region_time_list = group_data(data, region)
            for group in dot_group_list:
                try:
                    mem_avg = group.avg_mem_used()
                except Exception:
                    dot_list.append('N/A')
                else:
                    dot_list.append(round(mem_avg, 2))
            cluster_mem_total_rate_avg.update({"avg_mem": dot_list, "add_time": region_time_list})
            status = 200
            message = 'OK'
        except Exception,error:
            status = 501
            message = 'get exception %s from avg mem used' % str(error)
    else:
        status = 404
        message = 'Null Mem Data Found'
    _data.update({"cluster_mem_total_rate_avg": cluster_mem_total_rate_avg})
    resp.update({"status": status, "data": _data, "message": message})
    return resp, status


def get_cluster_cpu_frequency_logic(cluster_name, starttime, endtime):
    _data = {}
    status = ''
    message = ''
    cpu_frequency_val = {}
    resp = {"status": status, "data": _data, "message": message}
    if is_less_than_nhours(starttime, endtime, 1):
        region = 60
        data = SfoNodeStatMethod.query_cpu_frequency_region(cluster_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 8):
        region = 600
        data = SfoNodeStat5MinMethod.query_cpu_frequency_region(cluster_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24):
        region = 7200
        data = SfoNodeStatHourMethod.query_cpu_frequency_region(cluster_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24*7):
        region = 86400
        data = SfoNodeStatHourMethod.query_cpu_frequency_region(cluster_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24*31):
        region = 86400*30
        data = SfoNodeStatDayMethod.query_cpu_frequency_region(cluster_name, starttime, endtime)
    else:
        region = 86400*365
        data = SfoNodeStatDayMethod.query_cpu_frequency_region(cluster_name, starttime, endtime)
    if data:
        try:
            dot_list = []
            dot_group_list, region_time_list = group_data(data, region)
            for host_group in dot_group_list:
                cluster_core_used_sum = 0
                group_list = host_group.group_by_host_name()
                try:
                    for _host_list in group_list.values():
                        cpu_us_map = map(lambda x: float(x.cpu_us), _host_list)  # 不存在的数据默认0.0
                        sum_host = sum(cpu_us_map) // len(_host_list)
                        cluster_core_used_sum += sum_host
                except Exception:
                    dot_list.append('N/A')
                else:
                    _cpu_frequency_val = cluster_core_used_sum / len(group_list.keys()) if len(
                        group_list.keys()) else 1
                    _cpu_frequency_val = '%0.2f' % _cpu_frequency_val
                    dot_list.append(_cpu_frequency_val)
            cpu_frequency_val.update({"cpu_frq": dot_list, "add_time": region_time_list})
            status = 200
            message = 'OK'
        except Exception, error:
            status = 501
            message = 'get exception %s from cpu frequency' % str(error)
    else:
        status = 404
        message = 'Null Cpu Frequency Data Found'
    _data.update({"cpu_frequency_val": cpu_frequency_val})
    resp.update({"status": status, "data": _data, "message": message})
    return resp, status


def get_cluster_overview_logic(cluster_name):
    """
    GET 请求集群信息处理逻辑
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = ''
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    sfo_cluster = SfoClusterInfoMethod.query_last_cluster_overview(cluster_name)    # 获取总容量
    if sfo_cluster:
        status = 200
        message = 'OK'
        data = sfo_cluster
    else:
        status = 404
        message = 'Not Found Record Cluster Infomation By %s'% cluster_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def get_band_width_logic(cluster_name, starttime, endtime):

    data = {}
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    sfo_cluster = SfoClusterInfoMethod.query_start2end_region_list_info(cluster_name, starttime, endtime)  # 获取总容量
    if sfo_cluster:
        status = 200
        message = 'OK'
        band_used_list = map(lambda x: json.loads(x.band_width)['band_used'], sfo_cluster)
        band_rep_used_list = map(lambda x: json.loads(x.band_width)['band_rep_used'], sfo_cluster)
        add_time_list = map(lambda x: x.add_time, sfo_cluster)
        data.update({"band_used": band_used_list, "band_rep_used":band_rep_used_list, "add_time":add_time_list})
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def get_node_performance_logic(cluster_name):
    data = ''
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    node_perform = SfoNodePerformMethod.query_node_per_by_cluster_name(cluster_name)
    if node_perform:
        status = 200
        message = 'OK'
        data = node_perform
    else:
        status = 404
        message = 'Not Found Record Cluster Node Infomation By %s'% cluster_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def get_disk_performance_logic(cluster_name):
    data = ''
    status = ''
    message = ''
    disk_num_total = 0
    resp = {"status": status, "data": data, "message": message, "disk_num_total": disk_num_total}
    nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name=cluster_name)
    order_list = []
    for node in nodes:
        sfo_disk_per = []
        _sfo_disk_per = SfoDiskPerformMethod.query_last_diskinfo_by_hostname(node.node_host_name)
        for disk in _sfo_disk_per:
            if disk.disk_name not in map(lambda x: x.disk_name, sfo_disk_per):
                mx_disk = max(filter(lambda x: x.disk_name == disk.disk_name, _sfo_disk_per), key=lambda x: x.add_time)
                sfo_disk_per.append(mx_disk)
                order_list.append(mx_disk)
    if not nodes:
        raise ValueError('Cluster Not Found nodes')
    order_list = sorted(order_list, key=lambda x: float(x.disk_percent), reverse=True)
    if order_list:
        status = 200
        message = 'OK'
        data = order_list
        disk_num_total = len(order_list)
    else:
        status = 404
        message = 'Not Found Record Cluster Disk Infomation By %s' % cluster_name
    resp.update({"status": status, "data": data, "message": message, 'disk_num_total': disk_num_total})
    return resp, status


class ClusterOverViewAPI(Resource):

    """
    用于获取最近的集群整体信息数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]

    resource = (SfoClusterInfoMethod,)

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_overview_resource_fields)
    def get(self, cluster_name):
        try:
            resp, status = get_cluster_overview_logic(cluster_name)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterOverViewAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status


class ClusterCpuFrequencyAPI(Resource):

    """
        用于获取最近的集群整体信息数据
        request: GET
        response :
            { 'status': 200/404 ,"data":data , "message": message}
        content-type : application/json
        """

    resource = (SfoNodeStatMethod,)

    # method_decorators = [access_log_decorate]

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_cpu_resource_fields)
    def get(self, cluster_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time, '%Y-%m-%d %H:%M:00') if start_time else timestamp_format(
                time.time() - 3600, '%Y-%m-%d %H:%M:00')
            end_time = timestamp_format(end_time, '%Y-%m-%d %H:%M:00') if end_time else timestamp_format(time.time(),
                                                                                                         '%Y-%m-%d %H:%M:00')
            resp, status = get_cluster_cpu_frequency_logic(cluster_name, start_time, end_time)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterCpuFrequencyAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status


class ClusterMemoryAPI(Resource):
    """
        用于获取最近的集群整体信息数据
        request: GET
        response :
            { 'status': 200/404 ,"data":data , "message": message}
        content-type : application/json
        """

    # method_decorators = [access_log_decorate]
    resource = (SfoNodeStatMethod,)

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_mem_resource_fields)
    def get(self, cluster_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time, '%Y-%m-%d %H:%M:00') if start_time else timestamp_format(
                time.time() - 3600, '%Y-%m-%d %H:%M:00')
            end_time = timestamp_format(end_time, '%Y-%m-%d %H:%M:00') if end_time else timestamp_format(time.time(),
                                                                                                         '%Y-%m-%d %H:%M:00')
            resp, status = get_avg_mem_used_rate_logic(cluster_name, start_time, end_time)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterMemoryAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s"%str(error)
            return {'status': status, "message": message}, status


class ClusterStorNetUsedAPI(Resource):

    # method_decorators = [access_log_decorate]
    resource = (SfoNodeStatMethod,)

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_storage_resource_fields)
    def get(self, cluster_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time, '%Y-%m-%d %H:%M:00') if start_time else timestamp_format(
                time.time() - 3600, '%Y-%m-%d %H:%M:00')
            end_time = timestamp_format(end_time, '%Y-%m-%d %H:%M:00') if end_time else timestamp_format(time.time(),
                                                                                                         '%Y-%m-%d %H:%M:00')
            resp, status = get_storage_net_used_logic(cluster_name, start_time, end_time)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterStorNetUsedAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status


class ClusterProNetUsedAPI(Resource):

    resource = (SfoNodeStatMethod,)

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_proxy_resource_fields)
    def get(self, cluster_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time, '%Y-%m-%d %H:%M:00') if start_time else timestamp_format(
                time.time() - 3600, '%Y-%m-%d %H:%M:00')
            end_time = timestamp_format(end_time, '%Y-%m-%d %H:%M:00') if end_time else timestamp_format(time.time(),
                                                                                                         '%Y-%m-%d %H:%M:00')
            resp, status = get_proxy_net_used_logic(cluster_name, start_time, end_time)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterProNetUsedAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s"% str(error)
            return {'status': status, "message": message}, status


class ClusterBandWidthAPI(Resource):

    resource = (SfoNodeStatMethod,)

    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_band_width_fileds)
    def get(self, cluster_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time, '%Y-%m-%d %H:%M:00') if start_time else timestamp_format(
                time.time() - 3600, '%Y-%m-%d %H:%M:00')
            end_time = timestamp_format(end_time, '%Y-%m-%d %H:%M:00') if end_time else timestamp_format(time.time(),
                                                                                                         '%Y-%m-%d %H:%M:00')
            resp, status = get_band_width_logic(cluster_name, start_time, end_time)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterBandWidthAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s"% str(error)
            return {'status': status, "message": message}, status


class ClusterDiskPerformAPI(Resource):

    resource = (SfoDiskPerformMethod,)

    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_disk_performance_fileds)
    def get(self, cluster_name):
        try:
            resp, status = get_disk_performance_logic(cluster_name)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterDiskPerformAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s"% str(error)
            return {'status': status, "message": message}, status


class ClusterNodePerformAPI(Resource):

    resource = (SfoNodeStatMethod,)

    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_node_performance_fileds)
    def get(self, cluster_name):
        try:
            resp, status = get_node_performance_logic(cluster_name)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterNodePerformAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s"% str(error)
            return {'status': status, "message": message}, status


