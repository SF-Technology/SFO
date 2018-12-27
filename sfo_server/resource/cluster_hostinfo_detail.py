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

from sfo_server import access_logger
from flask_restful import Resource, marshal_with, fields
from sfo_server.models import SfoHostInfoMethod
from sfo_server.decorate import access_log_decorate, login_required, permission_required
from sfo_server.resource.common import (used_time,
                                        EnvelopeField,
                                        RecuDictField)


cluster_host_info_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": EnvelopeField({
            'mf': {
                "host_name": fields.String,
                "mf_name": fields.String,
                "mf_model": fields.String,
                "mf_bios_version": fields.String,
                "mf_bios_date": fields.String,
                "mf_serial_number": fields.String,
                "os_version": fields.String,
                "os_kernel_version": fields.String,
            },
            "cpu": {
                "cpu_model": fields.String,
                "cpu_sockets": fields.String,
                "cpu_cores": fields.String,
                "cpu_processors": fields.String,
                "cpu_frequency": fields.String,
            },
            "mem": {
                "mem_total": fields.String,
                "mem_number": fields.String,
                "mem_single_size": fields.String,
                "mem_frequency": fields.String,
            },
            "net": {
                "net_model": RecuDictField(),
                "net_number": fields.String,
                "net_speed": RecuDictField(),
                "net_mac_address": RecuDictField(),
                "net_ip_address": RecuDictField(),
            },
            "disk": {
                "disk_type": RecuDictField(),
                "disk_number": RecuDictField(),
                "disk_rpm_speed": fields.String,
                "disk_capacity": RecuDictField(),
                "disk_useful_size": RecuDictField(),
                "disk_rw_rate": RecuDictField(),
            }
        }),
}


def get_cluster_hostinfo_detail_logic(host_name):
    """
    GET 请求集群主机信息处理逻辑
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = ''
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    host_info_detail = SfoHostInfoMethod.query_host_info_by_host_name(host_name)
    if host_info_detail:
        status = 200
        message = 'OK'
        data = host_info_detail
    else:
        status = 404
        message = 'Not Found Record Cluster HostInfo By %s'%host_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterHostInfoDetailAPI(Resource):

    """
    用于获取最近一次集群节点采集的数据，用于监控
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]

    resource = (SfoHostInfoMethod,)

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_host_info_resource_fields)
    def get(self, host_name):
        try:
            resp, status = get_cluster_hostinfo_detail_logic(host_name)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterHostInfoDetailAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status
