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
from sfo_server.models import SfoServerUser
from flask_restful import Resource, marshal_with, fields,  request,abort
from sfo_server.decorate import access_log_decorate,permission_required, login_required


user_info_resource_fields = {
    "status": fields.String,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "user_account": fields.String,
        "display_name": fields.String,
        "last_login_time": fields.String,
        "roles": fields.List(fields.String(attribute='role_name')),
        "add_time": fields.String,

    }))
}


def get_user_info():
    status = ''
    message = ''
    data = {}
    resp = {"status": status, "message": message, "data": data}
    sfo_server_userlist = SfoServerUser.query_active_user_list()
    if sfo_server_userlist:
        data = sfo_server_userlist
        status = 200
        message = 'SUCCESS'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


class UserListAPI(Resource):

    resource = SfoServerUser

    method_decorators = [permission_required(resource), login_required]

    @marshal_with(user_info_resource_fields)
    def get(self):
        try:
            resp, status = get_user_info()
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status
