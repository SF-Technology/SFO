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

from flask import request
from flask_restful import Resource, marshal_with, fields
from sfo_server.manager_class import PolicyManager, RingManager
from sfo_server.models import SfoCluster
from sfo_server.decorate import login_required, permission_required

policy_fields_map = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "policy_num": fields.String,
        "policy_name": fields.String,
        "deprecated": fields.String,
        "policy_type": fields.String,
    }))
}


def get_policy_list(cluster_name):
    """
    获取存储策略列表
    :param cluster_name:
    :return:
    """
    data = []
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    pm = PolicyManager(cluster_name)
    try:
        sfo_policys = pm.policys()
        for policy in sfo_policys:
            policy_dict = {
                "policy_num": policy,
                "policy_name": sfo_policys[policy].get('name'),
                "deprecated": sfo_policys[policy].get('deprecated', 'no'),
                "policy_type": sfo_policys[policy].get('policy_type','replication')
            }
            data.append(policy_dict)
    except Exception, error:
        raise ValueError(str(error))
    if data:
        status = 200
        message = 'OK'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def add_policy_2cluster(cluster_name, policyjson):
    """
    添加策略到数据库,并创建任务执行添加存储策略的脚本
    :param cluster_name:
    :param policyjson:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    policy_num = policyjson.get('policy_num')
    policy_name = policyjson.get('policy_name')
    deprecated = policyjson.get('deprecated', 'no')
    policy_type = policyjson.get('policy_type', 'replication')
    sync_policy_ring = policyjson.get('sync_policy_ring', '')
    replicas = policyjson.get('replicas', '')
    part_power = policyjson.get('part_power', '')
    min_part_hours = policyjson.get('min_part_hours', '')
    pm = PolicyManager(cluster_name)
    try:
        content = pm.add(num=policy_num,
                         name=policy_name,
                         deprecated=deprecated,
                         policy_type=policy_type)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 201
        message = content
        if sync_policy_ring:
            try:
                rm = RingManager(cluster_name)
                content = rm.create(part_power=part_power,
                                    replicas=replicas,
                                    min_part_hours=min_part_hours,
                                    policy=True,
                                    policy_num=policy_num)
            except Exception, error:
                status = 501
                message = str(error)
            else:
                status = 201
                message = content
    resp.update({"status": status, "message": message})
    return resp, status


def del_policy_2cluster(cluster_name, policyjson):
    """
    弃用集群中的存储策略
    :param cluster_name:
    :param policyjson:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    policy_num = policyjson.get('policy_num')
    pm = PolicyManager(cluster_name)
    try:
        content = pm.deprecate(num=policy_num)
    except Exception, error:
        status = 501
        message = str(error)
    else:
        status = 200
        message = content
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterPolicyManagerApi(Resource):

    resource = (SfoCluster,)

    @login_required
    @permission_required(*resource)
    @marshal_with(policy_fields_map)
    def get(self, cluster_name):
        try:
            resp, status = get_policy_list(cluster_name)
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
    def post(self, cluster_name):
        try:
            policyjson = request.json
            resp, status = add_policy_2cluster(cluster_name, policyjson)
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
    def delete(self, cluster_name):
        try:
            policyjson = request.json
            resp, status = del_policy_2cluster(cluster_name, policyjson)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status