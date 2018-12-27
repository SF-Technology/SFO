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

import time
from sfo_server import access_logger
from sfo_server.models import SfoServerRole,db, SfoServerPermission
from flask_restful import Resource, marshal_with, fields,  request,abort
from sfo_server.decorate import access_log_decorate, login_required, permission_required
from sfo_server.resource.common import timestamp_format


role_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "role_name": fields.String,
        "add_time": fields.String,
        "role_desc": fields.String,
        "last_modify_time": fields.String,
        "permissions": fields.List(fields.String(attribute='permission_name'))
    })
}


def get_role_info(role_name):
    status = ''
    message = ''
    data = ''
    resp = {"status": status, "message": message, "data": data}
    sfo_server_role = SfoServerRole.query_role_by_name(role_name)
    if sfo_server_role:
        data = sfo_server_role
        status = 200
        message = 'SUCCESS'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def delete_role(role_name):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_server_role = SfoServerRole.query_role_by_name(role_name)
    if sfo_server_role:
        db.session.delete(sfo_server_role)
        db.session.commit()
        status = 204
        message = 'Delete SUCCESS'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message})
    return resp, status


def update_role(role_json, role_name):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_server_role = SfoServerRole.query_role_by_name(role_name)
    try:
        if role_json and sfo_server_role:
            for key, value in role_json.items():
                if hasattr(sfo_server_role, key):
                    if key == 'permissions':
                        value = SfoServerPermission.query_permissions(value)
                    setattr(sfo_server_role, key, value)
            sfo_server_role.last_modify_time = timestamp_format(time.time())
            db.session.add(sfo_server_role)
            db.session.commit()
            status = 201
            message = 'Update SUCCESS'
        else:
            status = 501
            message = 'NULL VALUE %s' % role_json
    except Exception, ex:
        status = 502
        message = str(ex)
    finally:
        resp.update({"status": status, "message": message})
        return resp, status


class SfoServerRoleAPI(Resource):

    resource = SfoServerRole

    method_decorators = [permission_required(resource), login_required]

    @marshal_with(role_resource_fields)
    def get(self, role_name):
        try:
            resp, status = get_role_info(role_name)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def put(self, role_name):
        try:
            if not request.json:
                abort(400)
            role_json = request.json
            resp, status = update_role(role_json, role_name)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def delete(self, role_name):
        try:
            resp, status = delete_role(role_name)
            return resp,status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status
