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

from flask_restful import Resource, marshal_with, fields

from sfo_common.models import SfoPartitionsInfo
from sfo_server import access_logger
from sfo_server.resource.common import used_time

# 输出字段的映射表
cluster_partition_resource_fields = {

    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "cluster_name": fields.String,
        "use_handoff_partitions": fields.String,
        "health_partitions": fields.String,
        "error_partitions": fields.String,
    })
}


def get_partition_info_logic(cluster_name):
    """
    GET 请求集群隔离区信息
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = ''
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    partition_info = SfoPartitionsInfo.query.filter_by(cluster_name=cluster_name).order_by(SfoPartitionsInfo.update_time.desc()).first()
    if partition_info:
        status = 200
        message = 'OK'
        data = partition_info
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterPartitionAPI(Resource):

    """
    用于获取集群采集数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """


    @used_time
    @marshal_with(cluster_partition_resource_fields)
    def get(self, cluster_name):
        try:
            resp, status = get_partition_info_logic(cluster_name)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterPartitionAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status

