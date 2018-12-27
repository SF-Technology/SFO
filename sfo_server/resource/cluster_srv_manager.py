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
import re
import types
import copy_reg
from flask import request
from sfo_server import access_logger
from sfo_server.models import (SfoClusterNodesMethod,
                               SfoClusterSrvs,
                               SfoCofigureMethod)
from flask_restful import Resource, abort, marshal_with, fields
from sfo_server.decorate import login_required, permission_required
from sfo_server.resource.common import _pickle_method
from sfo_server.manager_class import ServiceOperation, SwiftServiceOperation
from multiprocessing import Pool

copy_reg.pickle(types.MethodType, _pickle_method)

srv_fields_map = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "node_host_name": fields.String,
        "service_name": fields.String,
        "srv_stat": fields.String,
    })),
    "software_packages": fields.List(fields.String(attribute='config_value'))
}


class HostSrv(object):

    def __init__(self, service_name, host_name, host_ip, stat=0, error_message=''):
        self.service_name = service_name
        self.node_host_name = host_name
        self.host_ip = host_ip
        self.srv_stat = stat
        self.error_message = error_message


def get_srv_list(cluster_name, **keyword):
    """
    获取服务列表
    :param cluster_name:
    :return:
    """
    data = []
    sfo_srvs = []
    apply_result_list = []
    status = ''
    message = ''
    software_packs = SfoCofigureMethod.query_value_from_con_group('software_package')
    resp = {"status": status, "data": data, "message": message, "software_packages": software_packs}
    software_packages_map = map(lambda x: 'openstack-swift-%s*' % x.config_value if x.config_value in ['account', 'container', 'object', 'proxy'] else '%sd?' % x.config_value, software_packs)
    software_reg = '|'.join(software_packages_map)
    sfo_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    if not sfo_nodes:
        raise ValueError('Nodes is null')
    pool = Pool(25)
    for node in sfo_nodes:
        so = ServiceOperation(node.node_inet_ip)
        apply_result = pool.apply_async(func=so.srvs, args=(software_reg,))
        apply_dict = {"host_name": node.node_host_name, "ip": node.node_inet_ip, "apply_result": apply_result}
        apply_result_list.append(apply_dict)
    pool.close()
    pool.join()
    for apply_dict in apply_result_list:
        ip = apply_dict['ip']
        host_name = apply_dict['host_name']
        apply_result = apply_dict['apply_result']
        apply_result_data = apply_result.get(timeout=1)
        if apply_result_data:
            for srv in apply_result_data:
                for node in sfo_nodes:
                    if host_name == node.node_host_name:
                        node_role = node.node_role
                        try:
                            node_role_js = json.loads(node_role)
                            if isinstance(node_role_js, dict):
                                roles = filter(lambda x: node_role_js[x] == 'YES', node_role_js.keys())
                                for role in roles:
                                    role, _ = role.split('-')
                                    role = role.lower()
                                    role_com = re.compile(role)
                                    search_result = role_com.search(srv['service'])
                                    if search_result:
                                        hostsrv = HostSrv(srv['service'], host_name, ip, srv['stat'], srv['message'])
                                        sfo_srvs.append(hostsrv)
                        except ValueError:
                            continue

    if sfo_srvs:
        if not keyword:
            for srv in sfo_srvs:
                if srv.service_name not in map(lambda x: x.service_name, data):
                    data.append(srv)
            status = 200
            message = 'OK'
        else:
            for query_key, keyword_val in keyword.items():
                for srv in sfo_srvs:
                    if hasattr(srv, query_key):
                        if getattr(srv, query_key) == keyword_val:
                            data.append(srv)
                        status = 200
                        message = 'OK'
                    else:
                        raise AttributeError('%s has no %s attribute ' % (srv, query_key))
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def add_srv_2cluster(cluster_name, srvjson):
    """
    添加服务到数据库
    :param cluster_name:
    :param srvjson:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    host_name = srvjson.get('host_name')
    service_name = srvjson.get('service_name')
    sfo_clu_node = SfoClusterNodesMethod.query_host_by_host_name(host_name)
    if not sfo_clu_node:
        raise ValueError('Not Found Node Host %s' % host_name)
    swift_op = SwiftServiceOperation(sfo_clu_node.node_inet_ip)
    try:
        content = swift_op.install_service(service_name)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 200
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterSrvManagerApi(Resource):

    resource = (SfoClusterSrvs,)

    @login_required
    @permission_required(*resource)
    @marshal_with(srv_fields_map)
    def get(self, cluster_name):
        try:
            query_map = {}
            query_keyword = request.args.get('query')
            if query_keyword:
                keyword = request.args.get(query_keyword)
                if not keyword:
                    raise ValueError("""You need to set up %s,
                      when you set up the query parameter,
                      example: ?query=%s&%s=your_query_kw""" % (str(query_keyword),
                                                                str(query_keyword),
                                                                str(query_keyword)))
                else:
                    query_map.update({query_keyword: keyword})
                    resp, status = get_srv_list(cluster_name, **query_map)
            else:
                resp, status = get_srv_list(cluster_name)
            return resp, status
        except ValueError, error:
            access_logger.error('GET ClusterSrvManagerApi get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('GET ClusterSrvManagerApi get exception %s' % error)
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def post(self, cluster_name):
        try:
            if not request.json:
                abort(400)
            datajson = request.json
            if not datajson.get('host_name'):
                raise ValueError('host_name not allow null')
            if not datajson.get('service_name'):
                raise ValueError('service_name not allow null')
            resp, status = add_srv_2cluster(cluster_name, datajson)
            return resp, status
        except ValueError, error:
            access_logger.error('POST ClusterSrvManagerApi get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('POST ClusterSrvManagerApi get exception %s' % error)
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status
