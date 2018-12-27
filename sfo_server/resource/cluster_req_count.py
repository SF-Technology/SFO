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
from sfo_server.models import (SfoClusterNodesMethod,
                               SfoProxyStatsDMethod,
                               SfoProxyStatsD5MinMethod,
                               SfoProxyStatsDDayMethod,
                               SfoProxyStatsDHourMethod)
from sfo_server.resource.common import (timestamp_format,
                                        RecuDictField,
                                        sum_times_group_by_httpmethod,
                                        proxy_server_stat,
                                        is_less_than_nhours)
from sfo_server.decorate import access_log_decorate,login_required,permission_required


request_stat_fields_map = {
    "status": fields.Integer,
    "message": fields.String,
    "data": RecuDictField()
}


def get_requests_count_logic(cluster_name, start_time, end_time):
    """
    GET 请求集群信息列表处理逻辑
    :param start_time: str  字符串日期格式
    :param end_time: str  字符串日期格式
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = {"request_stats": [], "add_times": []}
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    if is_less_than_nhours(start_time, end_time, 1):
        request_stats = SfoProxyStatsDMethod.query_proxt_stat_st2et(start_time, end_time)
    elif is_less_than_nhours(start_time, end_time, 8):
        request_stats = SfoProxyStatsD5MinMethod.query_proxt_stat_st2et(start_time, end_time)
    elif is_less_than_nhours(start_time, end_time, 24):
        request_stats = SfoProxyStatsDHourMethod.query_proxt_stat_st2et(start_time, end_time)
    else:
        request_stats = SfoProxyStatsDDayMethod.query_proxt_stat_st2et(start_time, end_time)
    sfo_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name=cluster_name)
    for stat in request_stats:
        add_time = stat.add_time
        hostname_httpmethod_map = proxy_server_stat(stat.req_timing)
        for host_name in hostname_httpmethod_map.keys():
            if host_name.upper() not in [node.node_host_name.upper() for node in sfo_nodes]:
                hostname_httpmethod_map.pop(host_name)
        if hostname_httpmethod_map.values():
            data['request_stats'].append(reduce(lambda x, y: sum_times_group_by_httpmethod(x, y),
                                                hostname_httpmethod_map.values()))
            data['add_times'].append(add_time)
    if request_stats:
        status = 200
        message = 'OK'
        if data['request_stats']:
            data['request_stats'] = dict(
                zip(data['request_stats'][0].keys(), zip(*map(lambda x: x.values(), data['request_stats']))))
        else:
            status = 404
            message = 'Not Found Record By %s' % cluster_name
    else:
        status = 404
        message = 'Not Found Record By %s' % cluster_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterRequestCountApi(Resource):

    resource = (SfoProxyStatsDMethod, )

    @login_required
    @permission_required(*resource)
    @marshal_with(request_stat_fields_map)
    def get(self, cluster_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time) if start_time else timestamp_format(time.time() - 3600)
            end_time = timestamp_format(end_time) if end_time else timestamp_format(time.time())
            resp, status = get_requests_count_logic(cluster_name, start_time, end_time)
            return resp, status
        except ValueError, error:
            access_logger.error('GET ClusterRequestCountApi get exception %s' % error)
            status = 400
            message = "Invalid Parameters %s" % str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('GET ClusterRequestCountApi get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status