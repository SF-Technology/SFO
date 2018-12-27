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
from sfo_server import access_logger
from sfo_server.models import SfoSwiftRoleMethod, db
from flask_restful import Resource, fields, marshal_with
from sfo_server.resource.common import used_time
from sfo_server.decorate import login_required, permission_required


swift_role_list_field = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "guid": fields.String,
        "role_name": fields.String,
        "role_desc": fields.String,
        "role_meta": fields.String,
        "add_time": fields.String,
    }))
}


swift_role_field = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "guid": fields.String,
        "role_name": fields.String,
        "role_desc": fields.String,
        "role_meta": fields.String,
        "add_time": fields.String,
    })
}


def cluster_swift_roles_logic():
    status = ''
    message = ''
    data = []
    resp = {"status": status, "message": message, "data": data}
    sfo_swift_roles = SfoSwiftRoleMethod.query_roles()
    if len(sfo_swift_roles) >= 1:
        status = 200
        message = 'OK'
        data = sfo_swift_roles
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def cluster_swift_role_info(role_name):
    status = ''
    message = ''
    data = []
    resp = {"status": status, "message": message, "data": data}
    sfo_swift_role = SfoSwiftRoleMethod.query_role(role_name)
    if sfo_swift_role:
        status = 200
        message = 'OK'
        data = sfo_swift_role
    else:
        status = 404
        message = 'Not Found Record '
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def create_swift_role(role_name, role_meta, role_desc=''):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_swift_role = SfoSwiftRoleMethod.create_role(role_name, role_meta, role_desc)
    if sfo_swift_role:
        db.session.add(sfo_swift_role)
        db.session.commit()
        status = 201
        message = 'Create OK'
    else:
        status = 202
        message = 'Role :%s Exists' % role_name
    resp.update({"status": status, "message": message})
    return resp, status


def update_swift_role_info(guid, role_meta, role_desc=''):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_swift_role = SfoSwiftRoleMethod.query_role_by_guid(guid)
    if sfo_swift_role:
        sfo_swift_role.role_meta = role_meta
        sfo_swift_role.role_desc = role_desc
        db.session.add(sfo_swift_role)
        db.session.commit()
        status = 201
        message = 'Update OK'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterSwiftRoleListAPI(Resource):

    """
    集群注册账号列表API
    response :
        { 'status': 200/404 , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]

    resource = (SfoSwiftRoleMethod, )

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(swift_role_list_field)
    def get(self):
        try:
            resp, status = cluster_swift_roles_logic()
            return resp, status
        except Exception, error:
            access_logger.error('get ClusterSwiftRoleListAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}

    @login_required
    @permission_required(*resource)
    def post(self):
        try:
            role_info_json = request.json
            role = role_info_json.get('role')
            role_meta = role_info_json.get('role_meta')
            role_desc = role_info_json.get('role_desc')
            if not role:
                raise ValueError('role is not null')
            if not role_meta:
                raise ValueError('role_meta is not null')
            resp, status = create_swift_role(role, role_meta, role_desc)
            return resp, status
        except ValueError, error:
            access_logger.error('get ClusterSwiftRoleListAPI get exception %s' % error)
            status = 400
            message = 'Invaild Parameters %s' % str(error)
            return {'status': status, "message": message}
        except Exception, error:
            access_logger.error('get ClusterSwiftUserInfoAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}


class ClusterSwiftRoleInfoAPI(Resource):

    resource = (SfoSwiftRoleMethod, )

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(swift_role_field)
    def get(self, guid):
        try:
            resp = cluster_swift_role_info(guid)
            return resp
        except ValueError, error:
            access_logger.error('get ClusterSwiftRoleInfoAPI get exception %s' % error)
            status = 400
            message = 'Invaild Parameters %s' % str(error)
            return {'status': status, "message": message}
        except Exception, error:
            access_logger.error('get ClusterSwiftRoleInfoAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}

    @login_required
    @permission_required(*resource)
    def put(self, guid):
        try:
            user_info_json = request.json
            role_meta = user_info_json.get('role_meta')
            role_desc = user_info_json.get('role_desc')
            resp = update_swift_role_info(guid, role_meta, role_desc)
            return resp
        except ValueError, error:
            access_logger.error('put ClusterSwiftUserInfoAPI get exception %s' % error)
            status = 400
            message = 'Invaild Parameters %s' % str(error)
            return {'status': status, "message": message}
        except Exception, error:
            access_logger.error('put ClusterSwiftUserInfoAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}

