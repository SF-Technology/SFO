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

from flask_restful import Resource
from sfo_server.models import SfoManagerTaskLogMethod
from sfo_server.resource.common import used_time
from flask_restful import  marshal_with, fields
from sfo_server.decorate import login_required, permission_required

manager_log_field = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "guid": fields.String,
        "taskid": fields.String,
        "excute_description": fields.String,
        "excute_message": fields.String,
        "add_time": fields.String,
        "end_time": fields.String
    }))
}


def get_manager_log(taskid):
    """
    日志详情
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_man_log = SfoManagerTaskLogMethod.query_manager_log_by_taskid(taskid)
    if sfo_man_log:
        status = 200
        message = 'OK'
        data = sfo_man_log
    else:
        status = 404
        message = 'Invaild taskid from % or task never start' % taskid
        data = []
    resp.update({"status": status, "message": message, 'data':data})
    return resp, status


class ManagerLogDetailAPI(Resource):

    """
    管理操作日志 相关api
    response :
        { 'status': 200/404 , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]
    resource = (SfoManagerTaskLogMethod, )

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(manager_log_field)
    def get(self, taskid):
        try:
            resp, status = get_manager_log(taskid)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {"status": status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {"status": status, "message": message}, status


