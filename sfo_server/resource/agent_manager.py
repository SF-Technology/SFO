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
from flask_restful import Resource, fields, marshal_with, request
from sfo_server.models import BeatHeartInfoMethod, SfoClusterNodesMethod
from sfo_server.decorate import access_log_decorate, login_required, permission_required
from sfo_server.resource.common import used_time
from sfo_server.manager_class import FileManager, ServiceOperation


agent_field_map = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "agents_total": fields.Integer,
        "agents": fields.List(
            fields.Nested({
                "guid": fields.String,
                "hostname": fields.String,
                "add_time": fields.String,
            }))
    })
}


def get_cluster_agent_logic(cluster_name, page, limit):
    """
    GET 请求集群Agent管理
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = {"agents_total": '', "agents": []}
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    sfo_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    agents = BeatHeartInfoMethod.lived_agent_filter_cluster2(sfo_nodes, int(page), int(limit))
    if agents:
        status = 200
        message = 'OK'
        data['agents_total'] = agents.total
        data['agents'].extend(agents.items)
    else:
        status = 404
        message = 'Not Found Record Cluster Agent'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def test_cmd_link(host_name):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    node = SfoClusterNodesMethod.query_host_by_host_name(host_name)
    if node:
        try:
            sop = ServiceOperation(node.node_inet_ip)
            content = sop.excute_cmd('date')
            status = 200
            message = content
        except Exception, error:
            message = str(error)
            raise ValueError(message)
    else:
        status = 404
        message = 'Not Found'
    resp.update({"status": status, "message": message})
    return resp, status


def test_file_link(host_name):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    node = SfoClusterNodesMethod.query_host_by_host_name(host_name)
    if node:
        try:
            fm = FileManager()
            content = fm.give_away_file_to_host(host_name, '/app/sfo/README.md','/tmp')
            status = 200
            message = content
        except Exception, error:
            message = str(error)
            raise ValueError(message)
    else:
        status = 404
        message = 'Not Found'
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterAgentManagerAPI(Resource):

    """
    用于获取最近一次节点服务采集的数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    resource = (BeatHeartInfoMethod, )
    # method_decorators = [access_log_decorate]

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(agent_field_map)
    def get(self, cluster_name):
        try:
            page = request.args.get('page', 1)
            limit = request.args.get('limit', 10)
            resp, status = get_cluster_agent_logic(cluster_name, page, limit)
            return resp, status
        except ValueError, error:
            access_logger.error('GET ClusterAgentManagerAPI get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('GET ClusterAgentManagerAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % error
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def post(self, cluster_name):
        try:
            test_json = request.json
            operation = test_json.get('operation', 'test_cmd_link')
            host_name = test_json.get('host_name')
            if operation == 'test_cmd_link':
                resp, status = test_cmd_link(host_name)
            else:
                resp, status = test_file_link(host_name)
            return resp, status
        except ValueError, error:
            access_logger.error('POST ClusterAgentManagerAPI get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('GET ClusterAgentManagerAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % error
            return {'status': status, "message": message}, status