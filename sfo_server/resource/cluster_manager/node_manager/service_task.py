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

from flask import request, session
from sfo_server.models import SfoTasksListMethod
from flask_restful import Resource
from sfo_server.resource.common import used_time
from flask_restful import fields, marshal_with
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sfo_server.decorate import login_required, permission_required

service_list_field = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "guid": fields.String,
        "node_host_name": fields.String,
        "create_user": fields.String,
        "operation": fields.String,
        "service_type": fields.String,
        "service_name": fields.String,
        "service_task_ending_flag": fields.Integer,
        "task_start_time": fields.String,
        "task_end_time": fields.String,
    }))
}


def get_service_tasks(username, **query_map):
    """
    获取对应服务进程列表
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    if username and username == 'root':
        services = SfoTasksListMethod.query_by_filterkey(**query_map)
    elif username:
        services = SfoTasksListMethod.query_by_filterkey(create_user=username, **query_map)
    else:
        services = []
    if services:
        status = 200
        message = 'OK'
        data = services
    else:
        status = 404
        message = 'No Running Service Tasks'
        data = []
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


class ServiceTaskAPI(Resource):

    """
    系统操作 相关api
    response :
        { 'status': 200/404 , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]

    resource = (SfoTasksListMethod, )

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(service_list_field)
    def get(self):
        try:
            username = session.get('username')
            query_map = {}
            for key, key_type in SfoTasksListMethod.__dict__.items():
                if isinstance(key_type, InstrumentedAttribute):
                    if request.args.get(key):
                        key_val = request.args.get(key)
                        query_map.update({key: key_val})
            resp, status = get_service_tasks(username, **query_map)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {"status": status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {"status": status, "message": message}, status
