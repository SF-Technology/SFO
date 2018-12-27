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
from sfo_server.models import (SfoNodePerformMethod,
                               SfoNodePerform5MinMethod,
                               SfoNodePerformDayMethod,
                               SfoNodePerformHourMethod)
from sfo_server.resource.common import used_time, timestamp_format, RecuDictField, is_less_than_nhours
from sfo_server.decorate import login_required, permission_required


cluster_node_perform_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
            "node_role": RecuDictField(),
            "host_name": fields.String,
            "swift_version": fields.String,
            "node_time": fields.String,
            "async_pending": fields.String,
            "node_sockstat": RecuDictField(),
            "stg_diskusage": RecuDictField(),
            "drive_audit_errors": fields.String,
            "quarantined_count": RecuDictField(),
            "account_replication": RecuDictField(),
    }),
}


def get_cluster_nodeperform_detail_logic(host_name, start_time, end_time):
    """
    GET 请求节点执行数据处理逻辑
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = ''
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    if is_less_than_nhours(start_time, end_time, 1):
        node_perform_detail = SfoNodePerformMethod.query_node_per_by_host_name(host_name, start_time, end_time)
    elif is_less_than_nhours(start_time, end_time, 8):
        node_perform_detail = SfoNodePerform5MinMethod.query_node_per_by_host_name(host_name, start_time, end_time)
    elif is_less_than_nhours(start_time, end_time, 24):
        node_perform_detail = SfoNodePerformHourMethod.query_node_per_by_host_name(host_name, start_time, end_time)
    else:
        node_perform_detail = SfoNodePerformDayMethod.query_node_per_by_host_name(host_name, start_time, end_time)
    if node_perform_detail:
        status = 200
        message = 'OK'
        node_perform_detail_ins = node_perform_detail[-1]
        node_perform_detail_ins.list = node_perform_detail
        data = node_perform_detail_ins
    else:
        status = 404
        message = 'Not Found Record Between %s and %s  Cluster NodePerform By %s' % (start_time, end_time, host_name)
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterNodePerformDetailAPI(Resource):

    """
    用于获取最近一小时(默认)节点执行数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]

    resource = (SfoNodePerformMethod,)

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_node_perform_resource_fields)
    def get(self, host_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time) if start_time else timestamp_format(time.time() - 3600)
            end_time = timestamp_format(end_time) if end_time else timestamp_format(time.time())
            resp, status = get_cluster_nodeperform_detail_logic(host_name, start_time=start_time, end_time=end_time)
            return resp, status
        except ValueError, error:
            access_logger.error('access ClusterNodePerformDetailAPI get exception %s' % error)
            status = 400
            message = 'Invalid Parameter'
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('access ClusterNodePerformDetailAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error"
            return {'status': status, "message": message}, status
