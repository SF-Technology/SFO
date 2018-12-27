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
from flask import request
from sfo_server import access_logger
from flask_restful import Resource, marshal_with, fields
from sfo_server.models import SfoDiskPerformMethod, SfoDiskPerform5MinMethod,SfoDiskPerformHourMethod,SfoDiskPerformDayMethod, SfoDiskPerform, SfoDiskPerformHistory
from sfo_server.decorate import access_log_decorate, login_required, permission_required
from sfo_server.resource.common import used_time, RecuDictField, timestamp_format, strft_2_timestamp, is_less_than_nhours
from sfo_common.import_common import Config

config = Config()

cluster_disk_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "disk": RecuDictField
    })),
}


def get_cluster_disk_logic(host_name, starttime, endtime):
    """
    GET 请求集群节点信息处理逻辑
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = []
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    if is_less_than_nhours(starttime, endtime, 1):
        last_disk_perform_set = SfoDiskPerformMethod.query_disk_list_by_hostname(host_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 8):
        last_disk_perform_set = SfoDiskPerform5MinMethod.query_disk_list_by_hostname(host_name, starttime, endtime)
    elif is_less_than_nhours(starttime, endtime, 24):
        last_disk_perform_set = SfoDiskPerformHourMethod.query_disk_list_by_hostname(host_name, starttime, endtime)
    else:
        last_disk_perform_set = SfoDiskPerformDayMethod.query_disk_list_by_hostname(host_name, starttime, endtime)
    disk_dict = {}
    add_time_list = []
    add_time_set = map(lambda x: str(x.add_time), last_disk_perform_set)
    for disk in last_disk_perform_set:
        disk_name = str(disk.disk_name)
        if not disk_dict.get(disk_name, ''):
            disk_dict.setdefault(disk_name, [disk])
        else:
            disk_dict[disk_name].append(disk)
    for add_time in add_time_set:
        if not add_time_list:
            add_time_list.append(add_time)
            continue
        if add_time not in add_time_list:
            time_diff = int(strft_2_timestamp(add_time)) - int(strft_2_timestamp(add_time_list[-1]))
            if time_diff <= config.disk_refresh - 3:
                pass
            else:
                add_time_list.append(add_time)
    for disk_name, disk_list in disk_dict.items():
        obj = {'disk': {}}
        read_bytes_list = []
        read_count_list = []
        write_count_list = []
        write_bytes_list = []
        await_list = []
        for idx, disk_obj in enumerate(disk_list):
            read_bytes_series_data = []
            write_bytes_series_data = []
            read_count_series_data = []
            write_count_series_data = []
            await_list_series_data = []
            if idx == len(disk_list)-1:
                filter_key = filter(lambda x: not x.startswith('_'), disk_obj.__dict__)
                for key in filter_key:
                    obj['disk'].update({key: disk_obj.__dict__[key]})
                continue
            read_bytes = round(disk_obj.read_bytes_diff(disk_list[idx+1]), 2)
            write_bytes = round(disk_obj.write_bytes_diff(disk_list[idx+1]), 2)
            read_counts = round(disk_obj.read_count_diff(disk_list[idx+1]))
            write_counts = round(disk_obj.write_count_diff(disk_list[idx+1]))
            await_time = round(disk_obj.await_diff(disk_list[idx+1]), 2)
            read_bytes_series_data.append(add_time_list[idx])
            read_bytes_series_data.append(read_bytes)
            read_bytes_series_data.append('%s %s' % (host_name, disk_name))
            write_bytes_series_data.append(add_time_list[idx])
            write_bytes_series_data.append(write_bytes)
            write_bytes_series_data.append('%s %s' % (host_name, disk_name))
            read_count_series_data.append(add_time_list[idx])
            read_count_series_data.append(read_counts)
            read_count_series_data.append('%s %s' % (host_name, disk_name))
            write_count_series_data.append(add_time_list[idx])
            write_count_series_data.append(write_counts)
            write_count_series_data.append('%s %s' % (host_name, disk_name))
            await_list_series_data.append(add_time_list[idx])
            await_list_series_data.append(await_time)
            await_list_series_data.append('%s %s' % (host_name, disk_name))
            read_bytes_list.append(read_bytes_series_data)
            write_bytes_list.append(write_bytes_series_data)
            read_count_list.append(read_count_series_data)
            write_count_list.append(write_count_series_data)
            await_list.append(await_list_series_data)  #响应时间
        obj['disk'].update({'read': read_bytes_list,
                            "write": write_bytes_list,
                            "read_count": read_count_list,
                            "write_count": write_count_list,
                            "await": await_list})
        data.append(obj)
    if last_disk_perform_set:
        data = data
        status = 200
        message = 'OK'
    else:
        status = 404
        message = 'Not Found Record Cluster Disk By %s' % host_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterDiskAPI(Resource):

    """
    用于获取主机下的磁盘信息
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """
    resource = (SfoDiskPerform, )

    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_disk_resource_fields)
    def get(self, host_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time) if start_time else timestamp_format(time.time() - 1800)
            end_time = timestamp_format(end_time) if end_time else timestamp_format(time.time())
            resp, status = get_cluster_disk_logic(host_name, start_time, end_time)
            return resp, status
        except ValueError, error:
            access_logger.error('GET ClusterDiskAPI get exception %s' % error)
            status = 400
            message = "Invaild Parameter %s" % str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('GET ClusterDiskAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status
