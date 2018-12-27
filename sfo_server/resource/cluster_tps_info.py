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

import json
import time
from flask import request
from sfo_server import access_logger
from sfo_server.resource.common import timestamp_format
from flask_restful import Resource, marshal_with, fields
from sfo_server.models import SfoClusterTpsMethod
from sfo_server.decorate import login_required, permission_required




# 输出字段的映射表
cluster_tps_info_resource_fields = {

    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "avg_time_list": fields.List(fields.String(attribute='avg_time')),
        "head_time_list": fields.List(fields.String(attribute='head_time')),
        "get_time_list": fields.List(fields.String(attribute='get_time')),
        "put_time_list": fields.List(fields.String(attribute='put_time')),
        "delete_time_list": fields.List(fields.String(attribute='delete_time')),
        "post_time_list": fields.List(fields.String(attribute='post_time')),
        "add_time_list": fields.List(fields.String(attribute='add_time')),
    })
}


def get_cluster_tps_info_logic(cluster_name, starttime, endtime):
    """
    GET 请求集群信息列表处理逻辑
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = {'avg_time_list': [],
            "head_time_list": [],
            "get_time_list": [],
            "put_time_list": [],
            "delete_time_list": [],
            "post_time_list": [],
            "add_time_list": []}
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    cluster_tps_set = SfoClusterTpsMethod.query_start2end_region_list_info(cluster_name=cluster_name,
                                                                           start_time=starttime,
                                                                           end_time=endtime)
    if cluster_tps_set:
        status = 200
        message = 'OK'
        data['avg_time_list'] = data['get_time_list'] = data['head_time_list'] = data['put_time_list']\
            = data['delete_time_list'] = data['post_time_list'] = data['add_time_list'] = cluster_tps_set
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterTPSInfoAPI(Resource):

    """
    用于获取集群采集数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """
    resource = (SfoClusterTpsMethod,)

    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_tps_info_resource_fields)
    def get(self, cluster_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time) if start_time else timestamp_format(time.time() - 3600)
            end_time = timestamp_format(end_time) if end_time else timestamp_format(time.time())
            resp, status = get_cluster_tps_info_logic(cluster_name, start_time, end_time)
            return resp, status
        except Exception, error:
            access_logger.error('Get ClusterTPSInfoAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s"%(str(error))
            return {'status': status, "message": message}, status




