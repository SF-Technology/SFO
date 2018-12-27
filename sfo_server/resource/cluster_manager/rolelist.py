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
import uuid
from sfo_server import access_logger
from sfo_server.models import SfoServerRole,db, SfoServerPermission
from flask_restful import Resource,request,abort,fields,marshal_with
from sfo_server.decorate import access_log_decorate,permission_required, login_required
from sfo_server.resource.common import timestamp_format

rolelist_resource_fields = {
    "status": fields.String,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "role_name": fields.String,
        "add_time": fields.String,
        "last_modify_time": fields.String,
        "role_desc": fields.String
    }))
}


def get_role_list():
    status = ''
    message = ''
    data = []
    resp = {"status": status, "message": message, "data": data}
    sfo_server_rolelist = SfoServerRole.query.all()
    if sfo_server_rolelist:
        data = sfo_server_rolelist
        status = 200
        message = 'SUCCESS'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message, "data":data})
    return resp, status


def add_role_logic(role_json):
    """
    :param role_json:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    new_role = SfoServerRole()
    try:
        if role_json:
            for key, value in role_json.items():
                if hasattr(new_role, key):
                    if key == 'permissions':
                        value = SfoServerPermission.query_permissions(value)
                    setattr(new_role, key, value)
            new_role.guid = str(uuid.uuid4())
            new_role.add_time = new_role.last_modify_time = timestamp_format(time.time())
            db.session.add(new_role)
            db.session.commit()
            status = 200
            message = 'SUCCCESS'
        else:
            status = 501
            message = 'Null Value %s' % role_json
    except Exception, ex:
        status = 502
        message = str(ex)
    resp.update({"status": status, "message": message})
    return resp, status


class SfoServerRoleListAPI(Resource):

    resource = SfoServerRole

    method_decorators = [permission_required(resource), login_required]

    @marshal_with(rolelist_resource_fields)
    def get(self):
        try:
            resp, status = get_role_list()
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def post(self):
        try:
            if not request.json:
                abort(400)
            role_json = request.json
            resp, status = add_role_logic(role_json)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status
