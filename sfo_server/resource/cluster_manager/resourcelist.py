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
import json
from sfo_server import access_logger
from sfo_server.models import SfoServerResource, db, SfoServerPermission
from flask_restful import Resource, marshal_with, fields,  request,abort
from sfo_server.decorate import access_log_decorate,permission_required, login_required
from sfo_server.resource.common import timestamp_format


def get_resource_list():
    status = ''
    message = ''
    data = {}
    resp = {"status": status, "message": message, "data": data}
    sfo_server_rescourcelist = SfoServerResource.query.all()
    if sfo_server_rescourcelist:
        data = sfo_server_rescourcelist
        status = 200
        message = 'SUCCESS'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message, "data":data})
    return resp, status


def add_resource_logic(resource_json):
    """
    添加需要控制的资源,默认添加三种资源控制权限
    :param resource_json:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    new_resource = SfoServerResource()
    try:
        if resource_json:
            resource_name = resource_json['resource_name']
            for key, value in resource_json.items():
                if hasattr(new_resource, key):
                    setattr(new_resource, key, value)
            defalut_permission_list = SfoServerPermission.create_default_permission(resource_name)
            new_resource.guid = str(uuid.uuid4())
            new_resource.add_time = timestamp_format(time.time())
            new_resource.permissions = defalut_permission_list
            db.session.add(new_resource)
            db.session.commit()
            status = 200
            message = 'SUCCCESS'
        else:
            status = 501
            message = 'Null Value %s' % resource_json
    except Exception, ex:
        status = 502
        message = str(ex)
    resp.update({"status": status, "message": message})
    return resp, status


class SfoServerResourceListAPI(Resource):

    resource = SfoServerResource

    method_decorators = [permission_required(resource), login_required]

    def get(self):
        try:
            resp, status = get_resource_list()
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def post(self):
        try:
            if not request.json:
                abort(400)
            resource_json = request.json
            resp, status = add_resource_logic(resource_json)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status
