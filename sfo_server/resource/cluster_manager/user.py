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

from sfo_server.models import SfoServerUser,db,SfoServerRole
from flask_restful import Resource, marshal_with, fields,  request,abort
from sfo_server.decorate import access_log_decorate, permission_required,login_required

user_resource_fields = {
    "status": fields.String,
    "message": fields.String,
    "data": fields.Nested({
        "user_account": fields.String,
        "display_name": fields.String,
        "last_login_time": fields.String,
        "roles": fields.List(fields.String(attribute='role_name')),
        "add_time": fields.String,
    }),
}



def get_user_info(user_account):
    status = ''
    message = ''
    data = ''
    resp = {"status": status, "message": message, "data": data}
    sfo_server_user = SfoServerUser.query_user_by_account(user_account)
    if sfo_server_user:
        data = sfo_server_user
        status = 200
        message = 'OK'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def delete_user(user_account):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_server_user = SfoServerUser.query_user_by_account(user_account)
    if sfo_server_user:
        sfo_server_user.active_status = 0
        db.session.add(sfo_server_user)
        db.session.commit()
        status = 204
        message = 'DELETE SUCCESS'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message})
    return resp, status


def update_user(user_json, user_account):
    """
    :param user_json:
    :param user_account:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_server_user = SfoServerUser.query_user_by_account(user_account)
    try:
        if user_json and sfo_server_user:
            for key, value in user_json.items():
                if hasattr(sfo_server_user, key):
                    if key == 'roles':
                        value = SfoServerRole.query_roles(value)
                    if key == "is_clusteradmin" or key == 'active_status':
                        value = value if sfo_server_user.is_clusteradmin else 0
                    setattr(sfo_server_user, key, value)
            db.session.add(sfo_server_user)
            db.session.commit()
            status = 200
            message = 'OK'
        else:
            status = 501
            message = 'NULL VALUE %s' % user_json
    except Exception, ex:
        status = '502'
        message = str(ex)
    finally:
        resp.update({"status": status, "message": message})
        return resp, status


class UserAPI(Resource):

    resource = SfoServerUser

    method_decorators = [permission_required(resource), login_required]

    @marshal_with(user_resource_fields)
    def get(self, user_account):
        try:
            resp, status = get_user_info(user_account)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def put(self, user_account):
        try:
            if not request.json:
                abort(400)
            user_json = request.json
            resp, status = update_user(user_json, user_account)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def delete(self, user_account):
        try:
            resp, status = delete_user(user_account)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status
