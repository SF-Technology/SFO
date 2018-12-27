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
import json
from functools import wraps
from flask_restful import ResponseBase
from sfo_server.models import SfoServerUser, SfoAccountManagerMethod, SfoServerAccessLog
from sfo_server.resource.common import timestamp_format
from flask import request, g, session


def access_log_decorate(func):
    """
    用于记录用户登录后访问网址行为的装饰器
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_user = request.headers.get('X-Real-IP ', request.remote_addr)
        access_method = request.method
        access_path = request.path
        access_time = timestamp_format(time.time())
        resp = func(*args, **kwargs)
        access_result = resp[0].get('status')
        access_message = resp[0].get('message', 'Internal Server Error') if resp else 'Internal Server Error'
        SfoServerAccessLog.add_access_log(access_user, access_method, access_path, access_time, access_result, access_message)
        return resp
    return wrapper


def login_required(func):
    """
    验证是否登录
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        user_account = session.get('username', '')
        if user_account:
            login_user = SfoServerUser.query_user_by_account(user_account)
            g.user = login_user
            return func(*args, **kwargs)
        else:
            return ResponseBase(json.dumps({'status': 401, "message": u'请先登录'}),
                                status=401, content_type='application/json')
    return wrapper


def permission_required(*resources):
    """
    权限验证的前提是用户已经登录
    权限验证
    :param resources:  控制的资源对象
    """
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            method = func.__name__
            resource_names = [resource.__tablename__ for resource in resources]
            need_permission = set([method + '_' + resource_name for resource_name in resource_names])
            user = getattr(g, 'user', '')
            has_permission_set = set()
            is_clusteradmin = user.is_clusteradmin if user else 0
            if is_clusteradmin:
                return func(*args, **kwargs)
            if user:
                for role in user.roles:
                    for permission in role.permissions:
                        has_permission_set.add(permission.permission_name)

                if not need_permission.issubset(has_permission_set):
                    return ResponseBase(json.dumps({'status': 403, 'message': u'权限不足，请联系管理员'}),
                                status=403, content_type='application/json')
                else:
                    return func(*args, **kwargs)
            else:
                return ResponseBase(json.dumps({'status': 401, "message": u'请先登录'}),
                                status=401, content_type='application/json')
        return wrapper
    return decorate

