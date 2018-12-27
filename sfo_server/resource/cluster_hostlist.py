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
from copy import deepcopy
from sfo_server import access_logger
from flask_restful import Resource, marshal_with, fields, request
from sfo_server.models import SfoClusterNodesMethod, SfoHostInfoMethod, db, SfoClusterNodes
from sfo_server.decorate import access_log_decorate, login_required, permission_required
from sfo_server.resource.common import used_time, RecuDictField


def filter_ip_address(obj):
    net_ip_address = []
    if obj and hasattr(obj, 'net_ip_address'):
        _net_ip_address = obj.net_ip_address
        try:
            _net_ip_address = json.loads(_net_ip_address)
            if isinstance(_net_ip_address, dict):
                net_ip_address = map(lambda x: _net_ip_address[x], filter(lambda x: _net_ip_address[x] != 'N/A', _net_ip_address))
                return net_ip_address
            else:
                return net_ip_address
        except (TypeError, ValueError):
            return net_ip_address
    return net_ip_address


cluster_host_list_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "node_inet_ip": fields.String,
        "node_replicate_ip": fields.String,
        "node_role": fields.String,
        "node_host_name": fields.String,
        "add_time": fields.String,
        "host_info": fields.Nested({
            "mem_total": fields.String,
            "mem_number": fields.String,
            "mem_single_size": fields.String,
            "net_number": fields.String,
            "net_ip_address": fields.String(attribute=lambda x: filter_ip_address(x)),
            "disk_capacity": fields.String,
            "disk_useful_size": fields.String,
        })
    }))
}


def get_cluster_host_list_logic(cluster_name, is_host_info=''):
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
    if cluster_name == 'default':
        sfo_collect_hosts = SfoHostInfoMethod.query_last_host_info_list()
        used_hosts = db.session.query(SfoClusterNodes).filter(SfoClusterNodes.cluster_name != '').all()
        if used_hosts:
            used_hosts = map(lambda x: x.node_host_name.lower(), used_hosts)
        if sfo_collect_hosts:
            disused_hosts = filter(lambda x: x.host_name.lower() not in used_hosts, sfo_collect_hosts)
        else:
            disused_hosts = []
        will_used_hosts = []
        if disused_hosts:
            for host in disused_hosts:
                sfo_host = SfoClusterNodesMethod.create_or_update(host.host_name, '', '', '', '')
                if sfo_host:
                    db.session.add(sfo_host)
                    will_used_hosts.append(sfo_host)
            db.session.commit()
        last_host_info_set = will_used_hosts
        if is_host_info:
            for host in last_host_info_set:
                sfo_host = SfoHostInfoMethod.query_host_info_by_host_name(host.node_host_name)
                sfo_host_deepcopy = deepcopy(sfo_host)
                host.host_info = sfo_host_deepcopy
    else:
        last_host_info_set = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
        if last_host_info_set:
            last_host_info_set = filter(lambda x: x.node_stat == '1', last_host_info_set)
            if is_host_info:
                for host in last_host_info_set:
                    sfo_host = SfoHostInfoMethod.query_host_info_by_host_name(host.node_host_name)
                    sfo_host_deepcopy = deepcopy(sfo_host)
                    host.host_info = sfo_host_deepcopy
    if last_host_info_set:
        status = 200
        message = 'OK'
        data = last_host_info_set
    else:
        status = 404
        message = 'Not Found Record HostList By %s'%cluster_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterHostListAPI(Resource):

    """
    用于获取最近一次集群采集的主机数据，用于监控
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]

    resource = (SfoClusterNodes, )

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_host_list_resource_fields)
    def get(self, cluster_name):
        try:
            is_host_info = request.args.get('host_info', '')
            resp, status = get_cluster_host_list_logic(cluster_name, is_host_info)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterHostListAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status
