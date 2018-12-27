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
from sfo_server import access_logger
from sfo_server.models import SfoAccountManager, SfoCofigureMethod
from flask_restful import Resource, fields, marshal_with
from sfo_server.resource.common import used_time, capacity_translate
from sfo_server.decorate import login_required, permission_required


accounts_list_field = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "accounts_total": fields.Integer,
        "accounts": fields.List(
            fields.Nested({
                "system_code": fields.String,
                "account_id": fields.String,
                "system_env": fields.String,
                "system_capacity": fields.String(attribute=lambda x: capacity_translate(x.system_capacity) if hasattr(x, 'system_capacity') else '0'),
                "capacity_used_percent": fields.String(attribute=lambda x: capacity_used_percent(x.system_capacity, x.system_used) if hasattr(x, 'system_capacity') and hasattr(x, "system_used") else '0'),
                "account_used": fields.String(attribute=lambda x: account_used(x.system_used) if hasattr(x, "system_used") else '0')
            }))
    })
}


def account_used(used):
    try:
        used = int(json.loads(used).get('account-used', '0'))
    except (TypeError, ValueError):
        used = 0
    return used


def capacity_used_percent(capacity, used):
    try:
        used = int(json.loads(used).get('account-used', '0'))
    except Exception, error:
        used = 0
    if used == 0:
        return '0.0'
    else:
        return '%0.4f' % (round(float(used)/float(capacity), 4)*100)


def cluster_accounts_logic(page, limit):
    """
    集群账户列表信息
    :return:
    """
    status = ''
    message = ''
    data = {"accounts_total": '', "accounts": []}
    resp = {"status": status, "message": message}
    accounts = SfoAccountManager.query.filter_by(account_stat='1').order_by(SfoAccountManager.add_time.desc(), SfoAccountManager.guid)\
        .paginate(int(page), int(limit))
    if len(accounts.items) > 0:
        status = 200
        message = 'OK'
        data['accounts_total'] = accounts.total
        data['accounts'].extend(sorted(accounts.items, key=lambda x: capacity_used_percent(x.system_capacity, x.system_used), reverse=True))
    else:
        status = 404
        message = 'Not Record Found'
    resp.update({"status": status, "message": message, "data": data})
    return resp


def cluster_account_info(apply_account, system_env):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_system_env_con = SfoCofigureMethod.query_value_from_con_key(system_env)
    if not sfo_system_env_con:
        raise ValueError('system_env %s is invalid'%system_env)
    sfo_acc = SfoAccountManager.query.filter_by(system_code=apply_account, system_env=system_env).first()
    if sfo_acc:
        status = 304
        message = '%s Account existed' % apply_account
        data = sfo_acc.system_capacity
        resp.update({"data":{"systemCapacity": capacity_translate(data),
                             "ossSystemAccount":apply_account}})
    else:
        status = 200
        message = '%s Account available ' % apply_account
    resp.update({"status": status, "message": message})
    return resp


class ClusterAccountListAPI(Resource):

    """
    集群注册账号列表API
    response :
        { 'status': 200/404 , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]
    resource = (SfoAccountManager, )

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(accounts_list_field)
    def get(self):
        try:
            page = request.args.get('page', 1)
            limit = request.args.get('limit', 10)
            resp = cluster_accounts_logic(page, limit)
            return resp
        except Exception, error:
            access_logger.error('get ClusterAccountListAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % error
            return {'status': status, "message": message}


class ClusterAccountInfoAPI(Resource):

    resource = (SfoAccountManager, )

    @login_required
    @permission_required(*resource)
    def get(self):
        try:
            apply_account = request.args.get('applyAccount')
            system_env = request.args.get('system_env')
            if not (apply_account and system_env):
                return {"status": 400, "message": "applyAccount or system_env is null"}
            resp = cluster_account_info(apply_account, system_env)
            return resp
        except ValueError,error:
            access_logger.error('get ClusterAccountInfoAPI get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}
        except Exception, error:
            access_logger.error('get ClusterAccountInfoAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % error
            return {'status': status, "message": message}