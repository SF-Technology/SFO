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

from flask import request
from flask_restful import Resource, abort, marshal_with, fields

from sfo_common.models import SfoClusterNodes
from sfo_datahandler import db
from sfo_server.models import SfoClusterNodesMethod, SfoTasksListMethod, SfoHostInfoMethod
from sfo_utils.apscheduler_utils import scheduler
from sfo_server.decorate import login_required, permission_required

cluster_node_fields_map = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "guid": fields.String,
        "cluster_name": fields.String,
        "node_host_name": fields.String,
        "node_inet_ip": fields.String,
        "node_replicate_ip": fields.String,
        "node_role": fields.String,
        "node_stat": fields.String,
        "add_time": fields.String,
    }))
}


def get_node_list(cluster_name):
    """
    通过集群名获取当前集群中的节点列表
    :param cluster_name:
    :return:
    """
    data = []
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    try:
        if cluster_name:
            nodes = SfoClusterNodes.query.filter(SfoClusterNodes.cluster_name == cluster_name).all()
            if nodes:
                nodes = filter(lambda x: not x.node_stat != '1', nodes)
                if nodes:
                    data = nodes
                    status = 200
                    message = 'OK'
                else:
                    status = 404
                    message = 'No available node was found by %s cluster' % cluster_name
            else:
                status = 404
                message = 'No record was found by %s cluster'%cluster_name
        else:
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
                data = will_used_hosts
                status = 200
                message = 'OK'
            else:
                status = 404
                message = 'There is no enough node'
    except Exception as ex:
        status = 502
        message = str(ex)
    finally:
        resp.update({"status": status, "data": data, "message": message})
        return resp,status


def add_node_2cluster(nodejson):
    """
    添加节点到数据库
    :param nodejson:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    node_role = nodejson.get('node_role')
    host_ip = nodejson.get('node_inet_ip')
    cluster_name = nodejson.get('cluster_name', 'default')
    replication_ip = nodejson.get('node_replicate_ip')
    host_name = nodejson.get('node_host_name')
    auto_install_srv = nodejson.get('auto_install_srv')
    username = 'root'
    services = host_name
    operation = 'add_node'
    service_type = 'node_manager'
    try:
        if nodejson:
            sfo_cluster_node = SfoClusterNodesMethod.create_or_update(node_host_name=host_name,
                                                                      node_inet_ip=host_ip,
                                                                      node_role=node_role,
                                                                      node_replicate_ip=replication_ip,
                                                                      cluster_name=cluster_name)
            if sfo_cluster_node:
                db.session.add(sfo_cluster_node)
                sfo_task = SfoTasksListMethod.create_or_update_task(service_type=service_type,
                                                                    operation=operation,
                                                                    hostname=host_name,
                                                                    username=username,
                                                                    service_name=services
                                                                    )
                db.session.add(sfo_task)
                taskid = sfo_task.guid
                if auto_install_srv:
                    node_role = json.loads(node_role)
                    node_services_set = set(
                        map(lambda x: x.lower().split('-')[0], filter(lambda x: node_role[x] == 'YES', node_role)))
                    for srv in node_services_set:
                        scheduler.add_service(args=(sfo_cluster_node, srv, taskid))
                        if srv == 'proxy':
                            scheduler.add_service(args=(sfo_cluster_node, 'memcached', taskid))
                status = 200
                message = 'OK'
            else:
                status = 202
                message = 'OK'
        else:
            status = 501
            message = 'NULL VALUE %s'%nodejson
    except Exception as ex:
        status = 502
        message = str(ex)
    finally:
        db.session.commit()
        resp.update({"status": status, "message": message})
        return resp,status


class ClusterNodeManagerApi(Resource):

    resource = (SfoClusterNodesMethod,)

    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_node_fields_map)
    def get(self):
        try:
            cluster_name = request.args.get('cluster', '')
            resp, status = get_node_list(cluster_name)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def post(self):
        try:
            if not request.json:
                abort(400)
            datajson = request.json
            resp, status = add_node_2cluster(datajson)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status