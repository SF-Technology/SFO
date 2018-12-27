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

from flask import request, abort
from flask_restful import Resource, fields, marshal_with

from sfo_common.models import SfoCofigure
from sfo_server.decorate import permission_required, login_required
from sfo_server.models import db, SfoCofigureMethod
from sfo_server.resource.common import timestamp_format

config_field = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "config_total": fields.Integer,
        "configs": fields.List(fields.Nested({
            "guid": fields.String,
            "remark": fields.String,
            "config_value": fields.String,
            "config_key": fields.String,
            "add_time": fields.String,
            "config_group": fields.String
        }))
    })
}

def get_config(page, query, limit):
    page = int(page) if page else 1
    limit = int(limit) if limit else 10
    status = ''
    message = ''
    data = {"config_total": '', "configs": []}
    resp = {"status": status, "message": message, "data": data}
    sfo_configs = SfoCofigureMethod.query_all_config(page, query, limit)
    if sfo_configs:
        data['config_total'] = sfo_configs.total
        data['configs'].extend(sfo_configs.items)
        status = 200
        message = 'OK'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def create_config(config_json):
    status = ''
    message = ''
    data = []
    resp = {"status": status, "message": message, "data": data}
    config_group = config_json.get('config_group', '')
    config_key = config_json.get('config_key', '')
    if SfoCofigureMethod.query_filter_by_group_key(config_group,config_key):
        status = 301
        message = '%s exists in %s'%(config_key, config_group)
        resp.update({"status": status, "message": message, "data": data})
        return resp, status

    if config_group and config_key:
        sfo_config = SfoCofigure()
        for config, value in config_json.items():
            if hasattr(sfo_config, config):
                setattr(sfo_config, config, value)
        sfo_config.guid = str(uuid.uuid4())
        sfo_config.add_time = timestamp_format(time.time())
        db.session.add(sfo_config)
        db.session.commit()
        status = 201
        message = 'Create Success'
    else:
        status = 400
        message = 'config group or key parameters is required'
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def update_config(config_json):
    status = ''
    message = ''
    data = []
    resp = {"status": status, "message": message, "data": data}
    config_group = config_json.get('config_group', '')
    config_key = config_json.get('config_key', '')
    if config_group and config_key:
        sfo_config = SfoCofigureMethod.query_filter_by_group_key(config_group, config_key)
        for config, value in config_json.items():
            if hasattr(sfo_config, config):
                setattr(sfo_config, config, value)
        db.session.add(sfo_config)
        db.session.commit()
        status = 201
        message = 'Update Success'
    else:
        status = 400
        message = 'config group or key parameters is required'
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def delete_config(config_json):
    status = ''
    message = ''
    data = []
    resp = {"status": status, "message": message, "data": data}
    config_group = config_json.get('config_group', '')
    config_key = config_json.get('config_key', '')
    if config_group and config_key:
        sfo_configs = SfoCofigureMethod.query_filter_by_group_key(config_group, config_key)
        if sfo_configs:
            db.session.delete(sfo_configs)
            db.session.commit()
            status = 204
            message = 'Delete Success'
        else:
            status = 404
            message = 'Not Record Found'
    else:
        status = 400
        message = 'config group or key parameters is required'
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


class SfoServerConfigAPI(Resource):

    resource = SfoCofigure

    method_decorators = [permission_required(resource), login_required]

    @marshal_with(config_field)
    def get(self):
        try:
            query = request.args.get('query', '')
            page = request.args.get('page', 1)
            limit = request.args.get('limit', 10)
            resp, status = get_config(page, query, limit)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def post(self):
        try:
            if not request.json:
                abort(400)
            config_json = request.json
            resp, status = create_config(config_json)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def put(self):
        try:
            if not request.json:
                abort(400)
            config_json = request.json
            resp, status = update_config(config_json)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status

    def delete(self):
        try:
            if not request.json:
                abort(400)
            config_json = request.json
            resp, status = delete_config(config_json)
            return resp, status
        except Exception, ex:
            status = 500
            message = str(ex)
            return {'status': status, "message": message}, status



