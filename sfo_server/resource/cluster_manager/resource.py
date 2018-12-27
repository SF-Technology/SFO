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
from sfo_server.models import SfoServerResource, db
from flask_restful import Resource, marshal_with, fields,  request, abort
from sfo_server.decorate import access_log_decorate,permission_required


def get_resource_info(id):
    status = ''
    message = ''
    data = {}
    resp = {"status": status, "message": message, "data": data}
    sfo_server_resource = SfoServerResource.query_resource(id)
    if sfo_server_resource:
        user_class = sfo_server_resource.__class__
        for key, value in user_class.__dict__.keys():
            if hasattr(sfo_server_resource, key):
                value = getattr(sfo_server_resource, key)
                data.update({key: value})
        status = 200
        message = 'SUCCESS'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def delete_resource(id):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_server_resource = SfoServerResource.query_resource(id)
    if sfo_server_resource:
        db.session.delete(sfo_server_resource)
        db.session.commit()
        status = 204
        message = 'Clear'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message})
    return resp, status


def update_resource(resource_json, id):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_server_resource = SfoServerResource.query_resource(id)
    try:
        if resource_json and sfo_server_resource:
            for key, value in resource_json.items():
                if hasattr(sfo_server_resource, key):
                    setattr(sfo_server_resource, key, value)
            db.session.add(sfo_server_resource)
            db.session.commit()
            status = 201
            message = 'Update Success'
        else:
            status = 501
            message = 'NULL VALUE %s' % resource_json
    except Exception, ex:
        status = '502'
        message = str(ex)
    finally:
        resp.update({"status": status, "message": message})
        return resp, status


class SfoServerResourceAPI(Resource):

    resource = SfoServerResource
    method_decorators = [permission_required(resource)]

    def get(self, id):
        try:
            resp, status = get_resource_info(id)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def put(self, id):
        try:
            if not request.json:
                abort(400)
            resource_json = request.json
            resp, status = update_resource(resource_json, id)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def delete(self, id):
        try:
            resp, status = delete_resource(id)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status






