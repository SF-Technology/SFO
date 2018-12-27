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

from functools import wraps

from flask import request, session
from sqlalchemy import and_

from sfo_common.models import SfoSystemInput
from sfo_server.models import SfoServerUser


def authentication(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        user_account = session.get('username', '')
        if user_account:
            login_user = SfoServerUser.query_user_by_account(user_account)
            is_clusteradmin = login_user.is_clusteradmin if login_user else 0
            if is_clusteradmin:
                return func(*args, **kwargs)
        prams = request.json
        url = str(request.url)[str(request.url).find('/api'):]
        sys_auths = SfoSystemInput.query.filter(and_(SfoSystemInput.sys_id == prams['id'],SfoSystemInput.sys_key==prams['key'],SfoSystemInput.sys_stat == '1')).all()
        if sys_auths and len(sys_auths) > 0:
            for auth in sys_auths:
                if str(auth.sys_url).strip().upper() == str(url).strip().upper():
                    return func(*args,**kwargs)
                elif 'string:' in str(auth.sys_url).strip().lower():
                    auth_url = str(auth.sys_url)[:str(auth.sys_url).find('<string:')]
                    if str(url).strip().lower().find(auth_url.strip().lower()) == 0:
                        return func(*args,**kwargs)
                else:
                    pass
            status = 403
            message = "Lack of authority"
            return {'status': status, "message": message}, status
        else:
            status = 401
            message = "auth failed"
            return {'status': status, "message": message}, status
    return wrapper