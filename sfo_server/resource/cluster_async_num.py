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
from sfo_server.resource.common import timestamp_format, RecuDictField, is_less_than_nhours
from flask_restful import Resource, marshal_with, fields
from sfo_server.models import SfoCluster, SfoClusterInfoMethod, SfoClusterInfoHourMethod, SfoClusterInfoDayMethod
from sfo_server.decorate import login_required, permission_required



# 输出字段的映射表
cluster_info_resource_fields = {

    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "sync_num_list": fields.List(fields.String(attribute='sync_num')),
        "add_time_list": fields.List(fields.String(attribute='add_time')),
        "cluster_condition": fields.Nested({
            "auditor_queue": RecuDictField,
            "update_num": RecuDictField,
            "replicate_num": RecuDictField
        }),
        "cluster_virtual": fields.Nested({
            "object_num": fields.String,
            "account_num": fields.String,
            "container_num": fields.String,
        })
    })
}


def get_cluster_async_pending_logic(cluster_name, starttime, endtime):
    """
    GET 请求集群信息列表处理逻辑
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = {'sync_num_list': [], "add_time_list": [], 'cluster_condition': '', "cluster_virtual": ''}
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    if is_less_than_nhours(starttime, endtime, 1):
        cluster_set = SfoClusterInfoMethod.query_start2end_region_list_info(cluster_name=cluster_name,
                                                                            start_time=starttime,
                                                                            end_time=endtime)
    elif is_less_than_nhours(starttime, endtime, 24):
        cluster_set = SfoClusterInfoHourMethod.query_start2end_region_list_info(cluster_name=cluster_name,
                                                                                start_time=starttime,
                                                                                end_time=endtime)
    else:
        cluster_set = SfoClusterInfoDayMethod.query_start2end_region_list_info(cluster_name=cluster_name,
                                                                               start_time=starttime,
                                                                               end_time=endtime)
    instance = SfoClusterInfoMethod.query_by_cluster_name(cluster_name=cluster_name)
    if cluster_set:
        status = 200
        message = 'OK'
        data['sync_num_list'] = cluster_set
        data['add_time_list'] = cluster_set
        if instance:
            data['cluster_condition'] = instance
            data['cluster_virtual'] = instance
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterAysncPendingAPI(Resource):

    """
    用于获取集群采集数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """
    resource = (SfoCluster,)

    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_info_resource_fields)
    def get(self, cluster_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time) if start_time else timestamp_format(time.time() - 3600)
            end_time = timestamp_format(end_time) if end_time else timestamp_format(time.time())
            resp, status = get_cluster_async_pending_logic(cluster_name, start_time ,end_time)
            return resp, status
        except Exception, error:
            access_logger.error('Get ClusterAysncPendingAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error"
            return {'status': status, "message": message}, status




