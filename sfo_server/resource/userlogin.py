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
from flask import request, abort, session
from sfo_server import access_logger
from flask_restful import Resource
from sfo_server.models import SfoServerUser, db
from sfo_server.decorate import access_log_decorate
from sfo_server.resource.common import used_time, timestamp_format,is_super_admin



def create_or_update_userinfo(username, display_name, is_clusteradmin=False, sfo_server_user=None):
    if sfo_server_user is None:
        sfo_server_user = SfoServerUser.create_default_user(username, display_name, is_clusteradmin)
    else:
        sfo_server_user.last_login_time = timestamp_format(time.time())
    db.session.add(sfo_server_user)
    db.session.commit()


def user_login(login_json):
    """
    :param login_json: 登录传入的json格式
    :return:
    """
    data = {}
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    username = login_json.get('username')
    password = login_json.get('password')
    logined_username = session.get('username', '')
    if username == logined_username:
        status = 200
        message = u'您已经登录'
        data = {}
        if username == 'root':
            data.update({'token': str(uuid.uuid4())})
            data.update({'roles': ['superadmin']})
        resp.update({"status": status, "message": message, "data": data})
        return resp, status
    if username and password:
        if not is_super_admin(username, password):
            status = 401
            message = u'请检查你的账户和密码'
        else:
            token = str(uuid.uuid4())
            roles = ['superadmin']
            sfo_cluster_admin = SfoServerUser.query_user_by_account(username)
            create_or_update_userinfo(username, '超级管理员', is_clusteradmin=True, sfo_server_user=sfo_cluster_admin)
            data.update({'token': token})
            data.update({"roles": roles})
            session['token'] = token
            session['username'] = username
            status = 200
            message = 'OK'
    else:
        status = 401
        message = u'请输入账号和密码'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class UserLoginAPI(Resource):

    """
    request: POST
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    @used_time
    def post(self):
        try:
            if not request.json:
                abort(400)
            login_json = request.json
            resp, status = user_login(login_json)
            return resp, status
        except ValueError, error:
            access_logger.error('Post UserLoginAPI get exception %s' % error)
            status = 400
            message = 'Invalid Parameter %s' % str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('Post UserLoginAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status


