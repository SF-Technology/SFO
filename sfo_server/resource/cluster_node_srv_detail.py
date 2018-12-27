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

import asyncore
import re
import json
import time
from sfo_server import access_logger
from sfo_agent.cluster_server_client import ClusterClient
from flask import request, session
from flask_restful import Resource, marshal_with, fields
from sfo_utils.apscheduler_utils import scheduler
from sfo_server.models import SfoNodeServiceMethod, SfoClusterNodesMethod, db, SfoTasksListMethod, SfoClusterSrvsMethod
from sfo_server.decorate import access_log_decorate, login_required, permission_required
from sfo_server.resource.common import used_time,EnvelopeField, timestamp_format
from sfo_server.manager_class import NodeManager

action_status_map = {"start": "running",
                     "stop": "stopped",
                     "restart": "running"}

action_code_map = {"0x01": "start",
                   "0x02": "stop",
                   "0x03": "restart"}

cluster_node_srv_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": EnvelopeField({
            "proxy": {
                "srv_proxy": fields.String
            },
            "account": {
                "srv_account": fields.String,
                "srv_account_auditor": fields.String,
                "srv_account_reaper": fields.String,
                "srv_account_replicator": fields.String,
            },
            "container": {
                "srv_container": fields.String,
                "srv_container_auditor": fields.String,
                "srv_container_replicator": fields.String,
                "srv_container_updater": fields.String,
                "srv_container_sync": fields.String,
                "srv_container_reconciler": fields.String,
            },
            "object": {
                "srv_object": fields.String,
                "srv_object_auditor": fields.String,
                "srv_object_replicator": fields.String,
                "srv_object_updater": fields.String,
                "srv_object_expirer": fields.String,
                "srv_object_reconstructor": fields.String,
            },
        }),
}


def node_role_services_map(node_roles, hostname):
    node_roles = map(lambda x: x.lower(), filter(lambda x: node_roles[x] == 'YES', node_roles))
    node_services = SfoClusterSrvsMethod.query_srvlist_by_host_name(hostname)
    services = map(lambda x: x.service_name, node_services)
    services_total = []
    for role in node_roles:
        role = role.split('-server')[0]
        role_services = filter(lambda x: role in x, services)
        services_total.extend(role_services)
    return services_total


def get_cluster_nodesrv_detail_logic(host_name):
    """
    GET 请求集群节点信息处理逻辑
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = ''
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    node_srv_detail = SfoNodeServiceMethod.query_node_srv_by_host_name(host_name)
    if node_srv_detail:
        status = 200
        message = 'OK'
        data = node_srv_detail
    else:
        status = 404
        message = 'Not Found Record Cluster NodeService By %s'%host_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def change_cluster_nodesrv_logic(host_name, param):
    status, message = '', ''
    resp = {"status": status, "message": message}
    sfo_clu_node = SfoClusterNodesMethod.query_host_by_host_name(host_name)
    if sfo_clu_node:
        ip = sfo_clu_node.node_inet_ip
        action = param['action']
        service = param['service']
        client = ClusterClient(host=ip,
                               port=7201,
                               message="systemctl %s openstack-swift-%s.service" % (action, service.replace('_', '-')))
        asyncore.loop()
        if client.buffer == 'SUCCESS':
            sfo_server = SfoNodeServiceMethod.query_node_srv_by_host_name(host_name)
            setattr(sfo_server, 'srv_'+ param['service'], action_status_map[action])
            db.session.add(sfo_server)
            db.session.commit()
            status = 200
            message = 'OK'
        else:
            status = 400
            message = 'Operation Fail'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message})
    return resp, status


def create_cluster_nodesrv_detail_logic(host_name, param):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    host = SfoClusterNodesMethod.query_host_by_host_name(host_name)
    if not host:
        raise ValueError('No Record by %s' % host_name)
    operation = param.get('operation')
    services = param.get('service')
    try:
        nodeman = NodeManager(host.node_inet_ip)
        if hasattr(nodeman.swift_service, operation):
            oper_fun = getattr(nodeman.swift_service, operation)
            content = oper_fun(services)
        else:
            raise AttributeError('%s not found' % operation)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        active_status_cmp = re.compile('Active: .+\((.+)\)')
        active_status_cmp_result = active_status_cmp.search(content)
        if active_status_cmp_result:
            stat = active_status_cmp_result.groups()[0]
            if operation == 'stop' and stat == 'dead':
                status = 200
                message = content
            elif (operation == 'start' or operation == 'restart') and stat == 'running':
                status = 200
                message = content
            else:
                status = 501
                message = content + ' but service failed to perform the expected operation.'
        else:
            raise ValueError('can not complie stat')
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterNodeSrvDetailAPI(Resource):

    """
    用于获取最近一次节点服务采集的数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]
    resource = (SfoNodeServiceMethod, )

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_node_srv_resource_fields)
    def get(self, host_name):
        try:
            resp, status = get_cluster_nodesrv_detail_logic(host_name)
            return resp, status
        except Exception, error:
            access_logger.error('GET ClusterNodeSrvDetailAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % error
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def post(self, host_name):
        try:
            param = request.json
            if not param.get('service'):
                raise ValueError('service not null')
            if not param.get('operation'):
                raise ValueError('operation not Null')
            resp, status = create_cluster_nodesrv_detail_logic(host_name, param)
            return resp, status
        except ValueError, error:
            access_logger.error('POST ClusterNodeSrvDetailAPI get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('POST ClusterNodeSrvDetailAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % error
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def put(self, host_name):
        try:
            param = request.json
            if not param.get('action', ''):
                raise ValueError('action is not null')
            if not param.get('service', ''):
                raise ValueError('service is not null')
            resp, status = change_cluster_nodesrv_logic(host_name, param)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('PUT ClusterNodeSrvDetailAPI get exception %s' % error)
            status = 500
            message = 'Internal Server Error %s '% error
            return {'status': status, "message": message}, status
