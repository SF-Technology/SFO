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
from sfo_server.models import SfoManagerTaskLogMethod
from flask_restful import Resource
from sfo_server.resource.common import used_time, timestamp_format
from flask_restful import fields, marshal_with
from sfo_server.decorate import login_required, permission_required

service_task_detail_field = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "details_total": fields.Integer,
        "details": fields.List(fields.Nested({
            "guid": fields.String,
            "taskid": fields.String,
            "excute_description": fields.String,
            "excute_message": fields.String,
            "add_time": fields.String,
            "end_time": fields.String,
        })
    )})
}


def get_service_task_detail(taskid=None, start_time=None, end_time=None, page=1, limit=10):
    """
    获取对应服务进程列表
    :return:
    """
    status = ''
    message = ''
    data = {"details": [], "details_total": 0}
    resp = {"status": status, "message": message}
    sfo_task_logs = SfoManagerTaskLogMethod.query_manager_log_by_filter_key(taskid=taskid,
                                                                            start_time=start_time,
                                                                            end_time=end_time,
                                                                            page=page,
                                                                            limit=limit)
    if sfo_task_logs:
        status = 200
        message = 'OK'
        data['details'] = sfo_task_logs.items if hasattr(sfo_task_logs, 'items') else sfo_task_logs
        data['details_total'] = sfo_task_logs.total if hasattr(sfo_task_logs, 'total') else len(sfo_task_logs)
    else:
        if taskid:
            status = 404
            message = 'No Manager Log by %s Task' % taskid
        else:
            status = 404
            message = "There is no operation record in the last"
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


class ServiceTaskDetailAPI(Resource):

    """
    系统操作 相关api
    response :
        { 'status': 200/404 , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]

    resource = (SfoManagerTaskLogMethod, )

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(service_task_detail_field)
    def get(self):
        start_time = request.args.get('starttime', None)
        end_time = request.args.get('endtime', None)
        taskid = request.args.get('taskid', None)
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        try:
            if start_time:
                start_time = timestamp_format(start_time, '%Y-%m-%d %H:%M:%S')
            if end_time:
                end_time = timestamp_format(end_time, '%Y-%m-%d %H:%M:%S')
            if page and isinstance(page, (str, unicode)) and page.isdigit():
                page = int(page)
            if limit and isinstance(limit, (str, unicode)) and limit.isdigit():
                limit = int(limit)
            resp, status = get_service_task_detail(taskid, start_time, end_time, page, limit)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {"status": status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {"status": status, "message": message}, status


