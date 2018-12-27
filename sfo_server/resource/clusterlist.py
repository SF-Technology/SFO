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
import os
from flask import request, session
from sfo_server import access_logger
from flask_restful import Resource, marshal_with, fields
from sfo_server.models import SfoClusterMethod, SfoCluster, db, SfoTasksListMethod, SfoClusterNodesMethod
from sfo_utils.apscheduler_utils import scheduler
from sfo_server.decorate import access_log_decorate, login_required, permission_required
from sfo_server.resource.common import output_extend_field



# 输出字段的映射表
cluster_list_resource_fields = {

    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "cluster_name": fields.String,
        "alias": fields.String(attribute=lambda x: output_extend_field(x, 'alias')),
        "cluster_stat": fields.String(attribute=lambda x: x.cluster_stat),
        "description": fields.String(attribute=lambda x: output_extend_field(x, 'description'))
    }))
}


def get_cluster_list_logic():
    """
    GET 请求集群信息列表处理逻辑
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = []
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    cluster_set = SfoClusterMethod.query_cluster_list()
    if cluster_set:
        status = 200
        message = 'OK'
        data = cluster_set
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def create_cluster_list_logic(cluster_name, creater, cluster_stat, alias='', description=''):
    status = ''
    message = ''
    resp = {"status": status,  "message": message}
    extend = json.dumps({"alias": alias, "description": description})
    cluster = SfoClusterMethod.create(cluster_name, creater, cluster_stat, extend)
    if cluster:
        db.session.add(cluster)
        db.session.commit()
        status = 200
        message = 'OK'
    else:
        status = 202
        message = 'cluster_name %s is exists'% cluster_name
    resp.update({"status": status, "message": message})
    return resp, status


def update_cluster_config(cluster_name, cluster_json):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_clu = SfoClusterMethod.query_cluster_by_cluster_name(cluster_name)
    if sfo_clu:
        sfo_nodes = SfoClusterNodesMethod.query_not_used_hosts()
        if len(sfo_nodes) > 0:
            username = 'root'
            operation = 'create'
            service_type = 'cluster manager'
            services = 'create %s cluster' % cluster_name
            aco_ring_json = cluster_json.get('account', {})
            ser_ip = cluster_json.get('statsd_host_ip', '')
            con_ring_json = cluster_json.get('container', {})
            obj_ring_json = cluster_json.get('object', {})
            proxy_json = cluster_json.get('proxy', {})
            sfo_task = SfoTasksListMethod.create_or_update_task(service_type=service_type,
                                                                operation=operation,
                                                                username=username,
                                                                service_name=services
                                                                )
            db.session.add(sfo_task)
            db.session.commit()
            scheduler.create_cluster(args=(cluster_name, sfo_task.guid, ser_ip, aco_ring_json, con_ring_json, obj_ring_json, proxy_json))
            status = 201
            message = 'Create OK'
            data = {'data': sfo_task.guid}
            resp.update(data)
        else:
            status = 200
            message = 'There is no enough node'
    else:
        status = 404
        message = "%s cluster doesn't exists" % cluster_name
    resp.update({"status": status, "message": message})
    return resp, status



class ClusterListAPI(Resource):

    """
    用于获取集群采集数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """
    resource = (SfoCluster,)

    @marshal_with(cluster_list_resource_fields)
    def get(self):
        try:
            resp, status = get_cluster_list_logic()
            return resp, status
        except Exception, error:
            access_logger.error('Get ClusterListAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error"
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def post(self):
        try:
            cluster_json = request.json
            cluster_name = cluster_json.get('cluster_name')
            cluster_stat = cluster_json.get('cluster_stat', 'public')
            alias = cluster_json.get('alias', '')
            description = cluster_json.get('desc', '')
            if not cluster_name:
                raise ValueError('cluster name not be null')
            creater = session.get('username')
            resp, status = create_cluster_list_logic(cluster_name, creater, cluster_stat, alias, description)
            return resp, status
        except ValueError, error:
            access_logger.error('Post ClusterListAPI get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('Post ClusterListAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s"%str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def put(self):
        try:
            cluster_json = request.json
            cluster_name = cluster_json.get('cluster_name')
            resp, status = update_cluster_config(cluster_name, cluster_json)
            return resp, status
        except ValueError, error:
            access_logger.error('PUT ClusterListAPI get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('PUT ClusterListAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s"%str(error)
            return {'status': status, "message": message}, status



