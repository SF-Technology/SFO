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
from sfo_server import access_logger
from flask_restful import Resource, marshal_with, fields, request
from sfo_server.models import (SfoDiskPerformMethod,
                               SfoDiskPerform5MinMethod,
                               SfoDiskPerformHourMethod,
                               SfoDiskPerformDayMethod,
                               SfoClusterNodesMethod)
from sfo_server.resource.common import used_time, timestamp_format, group_data, is_less_than_nhours
from sfo_server.decorate import login_required, permission_required

cluster_disk_io_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "read_list": fields.List(fields.List(fields.String)),
        "write_list": fields.List(fields.List(fields.String)),
        "read_mbps_list": fields.List(fields.List(fields.String)),
        "write_mbps_list": fields.List(fields.List(fields.String)),
        "await_list": fields.List(fields.List(fields.String)),
    })
    }


def cluster_disk_io(cluster_name, starttime, endtime):
    read_list = []
    write_list = []
    read_mbps_list = []
    write_mbps_list = []
    await_list = []
    nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name=cluster_name)
    if is_less_than_nhours(starttime, endtime, 1):
        region = 60
        data = SfoDiskPerformMethod.query_disk_io(starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 8):
        region = 600
        data = SfoDiskPerform5MinMethod.query_disk_io(starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24):
        region = 7200
        data = SfoDiskPerformHourMethod.query_disk_io(starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24*7):
        region = 86400
        data = SfoDiskPerformHourMethod.query_disk_io(starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24*31):
        region = 86400 * 30
        data = SfoDiskPerformDayMethod.query_disk_io(starttime, endtime)
    else:
        region = 86400 * 365
        data = SfoDiskPerformDayMethod.query_disk_io(starttime, endtime)
    if not nodes:
        raise ValueError('Cluster Not Found nodes')
    data = filter(lambda x: x.host_name in map(lambda x: x.node_host_name, nodes), data)
    if data:
        dot_group_list, region_time_list = group_data(data, region)
        for idx, group in enumerate(dot_group_list):
            clu_disk_read_series_data = []
            clu_disk_write_series_data = []
            clu_disk_read_mbps_series_data = []
            clu_disk_write_mbps_series_data = []
            clu_disk_await_series_data = []
            clu_disk_read, clu_disk_write = group.disk_io_count()
            clu_disk_read_mbps, clu_disk_write_mbps = group.disk_io_used()
            clu_disk_await = group.disk_io_await()
            clu_disk_read_series_data.append(region_time_list[idx])
            clu_disk_read_series_data.append(clu_disk_read//region)
            clu_disk_read_series_data.append(cluster_name)
            clu_disk_write_series_data.append(region_time_list[idx])
            clu_disk_write_series_data.append(clu_disk_write//region)
            clu_disk_write_series_data.append(cluster_name)
            clu_disk_read_mbps_series_data.append(region_time_list[idx])
            clu_disk_read_mbps_series_data.append(clu_disk_read_mbps//region)
            clu_disk_read_mbps_series_data.append(cluster_name)
            clu_disk_write_mbps_series_data.append(region_time_list[idx])
            clu_disk_write_mbps_series_data.append(clu_disk_write_mbps // region)
            clu_disk_write_mbps_series_data.append(cluster_name)
            clu_disk_await_series_data.append(region_time_list[idx])
            clu_disk_await_series_data.append(clu_disk_await)
            clu_disk_await_series_data.append(cluster_name)
            read_list.append(clu_disk_read_series_data)
            write_list.append(clu_disk_write_series_data)
            read_mbps_list.append(clu_disk_read_mbps_series_data)
            write_mbps_list.append(clu_disk_write_mbps_series_data)
            await_list.append(clu_disk_await_series_data)
        return {"read_list": read_list,
                "write_list": write_list,
                "read_mbps_list": read_mbps_list,
                "await_list": await_list,
                "write_mbps_list": write_mbps_list}
    return None


def get_cluster_disk_io_logic(cluster_name, starttime, endtime):
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
    clu_disk_io = cluster_disk_io(cluster_name, starttime, endtime)
    if clu_disk_io:
        status = 200
        message = 'OK'
        data = clu_disk_io
    else:
        status = 404
        message = 'Not Found Record Cluster Infomation By %s' % cluster_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterDiskIOAPI(Resource):

    """
    用于获取最近的集群整体信息数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """
    resource = (SfoDiskPerformMethod,)

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_disk_io_resource_fields)
    def get(self, cluster_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time, '%Y-%m-%d %H:%M:00') if start_time else timestamp_format(
                time.time() - 1800, '%Y-%m-%d %H:%M:00')
            end_time = timestamp_format(end_time, '%Y-%m-%d %H:%M:00') if end_time else timestamp_format(time.time(),
                                                                                                         '%Y-%m-%d %H:%M:00')
            resp, status = get_cluster_disk_io_logic(cluster_name, start_time, end_time)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterDiskIOAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status
