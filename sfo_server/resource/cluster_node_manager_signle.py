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
from flask_restful import Resource, abort

from sfo_common.models import SfoClusterNodes
from sfo_datahandler import db
from sfo_server.models import SfoTasksListMethod
from sfo_server.resource.common import timestamp_format
from sfo_utils.apscheduler_utils import scheduler
from sfo_server.decorate import login_required, permission_required


def get_node_info(guid):
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
        nodes = SfoClusterNodes.query.filter(SfoClusterNodes.guid == guid).first()
        if nodes:
            status = 200
            message = 'OK'
            no = SfoClusterNodes
            for node in nodes:
                res = {}
                dic = node.__dict__
                for key in dic.keys():
                    if hasattr(no, key):
                        res[key] = dic[key]
                data.append(res)
        else:
            status = 404
            message = 'No record was found '
    except Exception as ex:
        status = 502
        message = str(ex)
    finally:
        resp.update({"status": status, "data": data, "message": message})
        return resp,status


def update_node_2cluster(nodejson, guid):
    '''
    更新数据库中的节点数据
    :param nodejson:
    :return:
    '''
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    mynode = SfoClusterNodes.query.filter(SfoClusterNodes.guid == guid).first()
    auto_install_srv = nodejson.get('auto_install_srv')
    username = 'root'
    services = mynode.node_host_name
    operation = 'update_node'
    service_type = 'node_manager'
    try:
        if nodejson:
            node = nodejson
            if node:
                for key in node.keys():
                    if hasattr(mynode, key):
                        setattr(mynode, key, node[key])
                db.session.add(mynode)
                sfo_task = SfoTasksListMethod.create_or_update_task(service_type=service_type,
                                                                    operation=operation,
                                                                    hostname=mynode.node_host_name,
                                                                    username=username,
                                                                    service_name=services
                                                                    )
                db.session.add(sfo_task)
                taskid = sfo_task.guid
                if auto_install_srv:
                    node_role = json.loads(mynode.node_role)
                    node_services_set = set(
                        map(lambda x: x.lower().split('-')[0], filter(lambda x: node_role[x] == 'YES', node_role)))
                    for srv in node_services_set:
                        scheduler.add_service(args=(mynode, srv, taskid))
                        if srv == 'proxy':
                            scheduler.add_service(args=(mynode, 'memcached', taskid))
                db.session.commit()
                status = 200
                message = 'SUCCESS'
        else:
            status = 501
            message = 'NULL VALUE %s' % nodejson
    except Exception as ex:
        status = 502
        message = str(ex)
    finally:
        resp.update({"status": status, "message": message})
        return resp, status


def delete_node_from_cluster(guid):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    try:
        if guid:
            mynode = SfoClusterNodes.query.filter(SfoClusterNodes.guid == guid).first()
            if mynode:
                mynode.node_stat = '1'
                mynode.cluster_name = ''
                mynode.node_inet_ip = ''
                mynode.node_replicate_ip = ''
                mynode.node_role = ''
                mynode.add_time = timestamp_format(time.time())
                db.session.commit()
                status = 200
                message = 'SUCCESS'
        else:
            status = 501
            message = 'NULL VALUE %s' % guid
    except Exception as ex:
        status = 502
        message = str(ex)
    finally:
        resp.update({"status": status, "message": message})
        return resp, status


class ClusterNodeManagerSignleApi(Resource):

    resource = (SfoClusterNodes,)

    @login_required
    @permission_required(*resource)
    def get(self, guid):
        try:
            resp, status = get_node_info(guid)
            return resp, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def put(self, guid):
        try:
            if not request.json:
                abort(400)
            datajson = request.json
            resp, status = update_node_2cluster(datajson, guid)
            return resp, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def delete(self, guid):
        try:
            resp, status = delete_node_from_cluster(guid)
            return resp, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status