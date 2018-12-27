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
from sfo_server import access_logger
from flask_restful import Resource, fields
from sfo_server.decorate import access_log_decorate, login_required
from sfo_server.resource.common import used_time


user_logout_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.String
}


def user_logout_logic(logout_json):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    login_user = session.get('username', '')
    user_account = logout_json.get('username', '')
    if user_account == login_user:
        status = 200
        message = 'Logout Success'
        session.pop('username')
        session.pop('token')
        session.clear()
    else:
        status = 404
        message = 'Not Found %s' % user_account
    resp.update({"status": status, "message": message})
    return resp, status


class UserLogoutAPI(Resource):

    """
    用户登出, 返回操作结果
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    method_decorators = [login_required]

    @used_time
    def post(self):
        try:
            logout_json = request.json
            if not logout_json:
                raise ValueError("parameters is null")
            resp, status = user_logout_logic(logout_json)
            return resp, status
        except ValueError, error:
            access_logger.error('POST UserLogoutAPI get exception %s' % error)
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('POST UserLogoutAPI get exception %s' % error)
            status = 500
            message = "Internal server error"
            return {'status': status, "message": message}, status


