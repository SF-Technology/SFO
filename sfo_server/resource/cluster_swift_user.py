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
import requests, json, random,os
import swiftclient as swclient
from sfo_utils.apscheduler_utils import scheduler
from flask import request
from sfo_server import access_logger
from sfo_server.models import SfoSwiftUserMethod, db, SfoSwiftRoleMethod, SfoAccountManagerMethod, SfoCofigureMethod, SfoTasksListMethod
from flask_restful import Resource, fields, marshal_with
from sfo_server.resource.common import used_time, timestamp_format
from sfo_common.config_parser import Config
from sfo_utils.utils import Util
from sfo_server.decorate import login_required, permission_required
config = Config()
util = Util()

swift_user_list_field = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.List(fields.Nested({
        "guid": fields.String,
        "cluster_name": fields.String,
        "account_id": fields.String,
        "role_name": fields.String,
        "system_user": fields.String,
        "add_time": fields.String,
    }))
}


swift_user_field = {
    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "guid": fields.String,
        "cluster_name": fields.String,
        "account_id": fields.String,
        "role_name": fields.String,
        "system_user": fields.String,
        "add_time": fields.String,
    })
}


def stg_authenticate(account, user, passwd, domain, admin=False):
    '''
    认证函数，如果认证成功，返回存储路径和token值
    :param account:  swift account账号, 在这就是系统编码
    :param user:   系统编码对应的用户
    :param passwd: 系统编码用户的密码
    :param system_env: 系统编码的系统环境
    :param admin （bool）: 管理员标志位
    :return:
    '''
    try:
        auth_account = user
        auth_passwd = passwd
        auth_version = config.swift_auth_version or 1
        (storage_url, auth_token) = swclient.get_auth(config.swift_auth_url, auth_account, auth_passwd,
                                                      auth_version=auth_version, os_options={'project_name': account,
                                                                                             'project_domain_name': domain,
                                                                                             'user_domain_name': domain if not admin else "Default"})
        return (storage_url, auth_token)
    except Exception as ex:
        raise RuntimeError('swift authenticate fail ,the reason is %s' % ex)


def create_random_password():
    """
    :return: 一串10-13位的随机密码
    """
    password_str = ''
    for i in range(util.randomint(10, 13)):
        random_ascii = util.randomint(35, 125)
        if random_ascii == 34:
            random_ascii = util.randomint(40, 125)
        if random_ascii == 39:
            random_ascii = util.randomint(40, 125)
        if random_ascii == 92:
            random_ascii = util.randomint(93, 125)
        if random_ascii == 96:
            random_ascii = util.randomint(97, 125)
        password_str += chr(random_ascii)
    return password_str


def ensure_headers(up_headers, account_id, swift_user, role_meta):
    u_x_account = up_headers.get('X-Account-Access-Control','')
    if u_x_account:
        json_u_x_account = json.loads(u_x_account)
        u_role_meta_list = json_u_x_account.get(role_meta,'')
        if u_role_meta_list:
            u_role_meta_list.index("%s:%s" % (account_id, swift_user))
        else:
            raise Exception('Ensure update headers X-Account-Access-Control No role_meta_list')
    else:
        raise Exception('Ensure update headers No X-Account-Access-Control')


def cluster_swift_users_logic(cluster_name):
    status = ''
    message = ''
    data = []
    resp = {"status": status, "message": message, "data": data}
    sfo_swift_users = SfoSwiftUserMethod.query_users_by_cluster_name(cluster_name)
    if len(sfo_swift_users) >= 1:
        status = 200
        message = 'OK'
        data = sfo_swift_users
    else:
        status = 404
        message = 'Not Found Record in %s Cluster' % cluster_name
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def cluster_swift_user_info(guid):
    status = ''
    message = ''
    data = []
    resp = {"status": status, "message": message, "data": data}
    sfo_swift_user = SfoSwiftUserMethod.query_user_by_guid(guid)
    if sfo_swift_user:
        status = 200
        message = 'OK'
        data = sfo_swift_user
    else:
        status = 404
        message = 'Not Found Record '
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def create_swift_user(cluster_name, swift_username, account_id='', role=''):
    status = ''
    message = ''
    data = {}
    resp = {"status": status, "message": message, "data": data}
    if role:
        sfo_role = SfoSwiftRoleMethod.query_role(role)
        if not sfo_role:
            raise ValueError('Not Found Role %s '%role)
    if account_id:
        sfo_account = SfoAccountManagerMethod.query_system_by_accountid(account_id)
        if not sfo_account:
            raise ValueError('Not Found Account ID %s '%account_id)
    sfo_swift_user = SfoSwiftUserMethod.create_user(cluster_name, swift_username, account_id, role)
    if sfo_swift_user and account_id and role and sfo_swift_user.system_user:
        admin_user = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_USERNAME')
        admin_password = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_PASSWORD')
        sfo_account = SfoAccountManagerMethod.query_system_by_accountid(account_id)
        sfo_role = SfoSwiftRoleMethod.query_role(role)
        _stg_url, stg_token = stg_authenticate(account=sfo_account.project_name,
                                               user=admin_user.config_value,
                                               passwd=admin_password.config_value,
                                               domain=sfo_account.domain,
                                               admin=True)
        headers = {'X-Auth-Token': stg_token}
        swift_role_header = requests.head(_stg_url, headers=headers, timeout=5)
        access_logger.info('HEAD_URL:%s, Status Code:%s, Headers:%s' % (
            _stg_url, swift_role_header.status_code, swift_role_header.headers))
        if swift_role_header.status_code <= 299:
            x_account_control = swift_role_header.headers.get('X-Account-Access-Control')
            if x_account_control:
                x_account_control = json.loads(x_account_control)
                role_meta_header = x_account_control.get(sfo_role.role_meta)
                if role_meta_header:
                    sub_role_meta_set = set(x_account_control[sfo_role.role_meta])
                    sub_role_meta_set.add("%s:%s" % (account_id, swift_username))
                    x_account_control[sfo_role.role_meta] = list(sub_role_meta_set)
                else:
                    sub_role_meta_set = set()
                    sub_role_meta_set.add("%s:%s" % (account_id, swift_username))
                    x_account_control[sfo_role.role_meta] = list(sub_role_meta_set)
                headers.update({'X-Account-Access-Control': json.dumps(x_account_control)})
            else:
                role_meta_set = set()
                role_meta_set.add("%s:%s" % (account_id, sfo_swift_user.system_user))
                headers['X-Account-Access-Control'] = json.dumps({
                    sfo_role.role_meta: list(role_meta_set)})
            access_logger.info('HEAD_URL:%s, Update Headers:%s' % (
                _stg_url, headers))
            swift_role_control = requests.post(_stg_url,
                                               headers=headers,
                                               timeout=5)
            access_logger.info('HEAD_URL:%s, Status Code:%s, Headers:%s' % (
                _stg_url, swift_role_control.status_code, swift_role_control.headers))
            if swift_role_control.status_code <= 299:
                status = 200
                message = 'Account Control OK'
                sfo_swift_user_passwd = SfoSwiftUserMethod.query_passwd_exists_by_account_id_system_user(
                    account_id=account_id,
                    system_user=swift_username)
                if sfo_swift_user_passwd:
                    _password = json.loads(sfo_swift_user_passwd.extend)
                    password = _password['password']
                else:
                    password = create_random_password()
                if not sfo_swift_user.extend:
                    sfo_swift_user.extend = json.dumps({"password": password})
                else:
                    extend = json.loads(sfo_swift_user.extend)
                    extend['password'] = password
                    sfo_swift_user.extend = json.dumps(extend)
                after_update_header_ensure = requests.head(_stg_url, headers={'X-Auth-Token': stg_token}, timeout=5)
                if after_update_header_ensure.status_code <= 299:
                    ensure_headers(after_update_header_ensure.headers, account_id, swift_username, sfo_role.role_meta)
                    # 创建项目-用户-角色
                    access_logger.info('Add Account:%s User:%s role:%s' % (
                        sfo_account.account_id, sfo_swift_user.system_user, sfo_swift_user.role_name))
                    data['password'] = password
                    data['account'] = account_id
                    data['username'] = swift_username
                    db.session.add(sfo_swift_user)
                    db.session.commit()
            else:
                status = swift_role_control.status_code
                message = 'Account Control Fail , Status Code %s' % swift_role_control.status_code
        else:
            message = 'Head Storage Url %s Fail , Status Code %s' % (_stg_url, swift_role_header.status_code)
    elif sfo_swift_user:
        db.session.add(sfo_swift_user)
        db.session.commit()
        status = 201
        message = 'Create OK'
    else:
        status = 202
        message = 'Account ID:%s  Role:%s  System User:%s Exists' % (account_id, role, swift_username)
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def update_swift_user_info(guid, role='', account_id=''):
    status = ''
    message = ''
    data = {}
    resp = {"status": status, "message": message, "data": data}
    sfo_swift_user = SfoSwiftUserMethod.query_user_by_guid(guid)
    if role:
        sfo_role = SfoSwiftRoleMethod.query_role(role)
        if not sfo_role:
            raise ValueError('Not Found Role %s '%role)
    if account_id:
        sfo_account = SfoAccountManagerMethod.query_system_by_accountid(account_id)
        if not sfo_account:
            raise ValueError('Not Found Account ID %s ' % account_id)
    if sfo_swift_user and (not sfo_swift_user.account_id or not sfo_swift_user.role_name):
        _sfo_swift_user = SfoSwiftUserMethod.query_user_by_unique_constraint(account_id, role,
                                                                             sfo_swift_user.system_user)
        if _sfo_swift_user:
            raise ValueError(
                'Account ID:%s  Role:%s  System User:%s Exists' % (account_id, role, sfo_swift_user.system_user))
        else:
            if role:
                sfo_swift_user.role_name = role
            if account_id:
                sfo_swift_user.account_id = account_id
            if sfo_swift_user.account_id and sfo_swift_user.role_name:
                admin_user = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_USERNAME')
                admin_password = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_PASSWORD')
                sfo_account = SfoAccountManagerMethod.query_system_by_accountid(account_id)
                sfo_role = SfoSwiftRoleMethod.query_role(role)
                _stg_url, stg_token = stg_authenticate(account=sfo_account.project_name,
                                                       user=admin_user.config_value,
                                                       passwd=admin_password.config_value,
                                                       domain=sfo_account.domain,
                                                       admin=True)
                headers = {'X-Auth-Token': stg_token}
                swift_role_header = requests.head(_stg_url, headers=headers)
                access_logger.info('HEAD_URL:%s, Status Code:%s, Headers:%s' % (
                    _stg_url, swift_role_header.status_code, swift_role_header.headers))
                if swift_role_header.status_code <= 299:
                    x_account_control = swift_role_header.headers.get('X-Account-Access-Control')
                    if x_account_control:
                        x_account_control = json.loads(x_account_control)
                        role_meta_header = x_account_control.get(sfo_role.role_meta)
                        if role_meta_header:
                            sub_role_meta_set = set(x_account_control[sfo_role.role_meta])
                            sub_role_meta_set.add("%s:%s" % (account_id, sfo_swift_user.system_user))
                            x_account_control[sfo_role.role_meta] = list(sub_role_meta_set)
                        else:
                            sub_role_meta_set = set()
                            sub_role_meta_set.add("%s:%s" % (account_id, sfo_swift_user.system_user))
                            x_account_control[sfo_role.role_meta] = list(sub_role_meta_set)
                        headers.update({'X-Account-Access-Control': json.dumps(x_account_control)})
                    else:
                        role_meta_set = set()
                        role_meta_set.add("%s:%s" % (account_id, sfo_swift_user.system_user))
                        headers['X-Account-Access-Control'] = json.dumps({
                            sfo_role.role_meta: list(role_meta_set)})
                    access_logger.info('HEAD_URL:%s, Update Headers:%s' % (
                        _stg_url, headers))
                    swift_role_control = requests.post(_stg_url,
                                                       headers=headers,
                                                       timeout=5)
                    access_logger.info('HEAD_URL:%s, Status Code:%s, Headers:%s' % (
                        _stg_url, swift_role_control.status_code, swift_role_control.headers))
                    if swift_role_control.status_code <= 299:
                        status = 200
                        message = 'Account Control OK'
                        sfo_swift_user_passwd = SfoSwiftUserMethod.query_passwd_exists_by_account_id_system_user(
                            account_id=account_id,
                            system_user=sfo_swift_user.system_user)
                        if sfo_swift_user_passwd:
                            _password = json.loads(sfo_swift_user_passwd.extend)
                            password = _password['password']
                        else:
                            password = create_random_password()
                        if not sfo_swift_user.extend:
                            sfo_swift_user.extend = json.dumps({"password": password})
                        else:
                            extend = json.loads(sfo_swift_user.extend)
                            extend['password'] = password
                            sfo_swift_user.extend = json.dumps(extend)
                        after_update_header_ensure = requests.head(_stg_url, headers={'X-Auth-Token': stg_token},
                                                                   timeout=5)
                        if after_update_header_ensure.status_code <= 299:
                            ensure_headers(after_update_header_ensure.headers, account_id, sfo_swift_user.system_user,
                                           sfo_role.role_meta)
                        # 添加角色
                        data['password'] = password
                        data['account'] = account_id
                        data['username'] = sfo_swift_user.system_user
                        db.session.add(sfo_swift_user)
                        db.session.commit()
                    else:
                        status = swift_role_control.status_code
                        message = 'Account Control Fail , Status Code %s' % swift_role_control.status_code
                else:
                    message = 'Head Storage Url %s Fail , Status Code %s' % (_stg_url, swift_role_header.status_code)
            else:
                db.session.add(sfo_swift_user)
                db.session.commit()
                status = 201
                message = 'Update OK'
    elif sfo_swift_user and sfo_swift_user.role_name and sfo_swift_user.account_id and sfo_swift_user.role_name != role:
        _sfo_swift_user = SfoSwiftUserMethod.query_user_by_unique_constraint(account_id, role,
                                                                             sfo_swift_user.system_user)
        if _sfo_swift_user:
            raise ValueError(
                'Account ID:%s  Role:%s  System User:%s Exists' % (account_id, role, sfo_swift_user.system_user))
        else:
            if not role:
                raise ValueError('Role not allow null')
            if sfo_swift_user.account_id and sfo_swift_user.role_name:
                admin_user = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_USERNAME')
                admin_password = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_PASSWORD')
                sfo_account = SfoAccountManagerMethod.query_system_by_accountid(account_id)
                pre_sfo_role = SfoSwiftRoleMethod.query_role(sfo_swift_user.role_name)
                cur_sfo_role = SfoSwiftRoleMethod.query_role(role)
                _stg_url, stg_token = stg_authenticate(account=sfo_account.project_name,
                                                       user=admin_user.config_value,
                                                       passwd=admin_password.config_value,
                                                       domain=sfo_account.domain,
                                                       admin=True)

                headers = {'X-Auth-Token': stg_token}
                swift_role_header = requests.head(_stg_url, headers=headers)
                access_logger.info('HEAD_URL:%s, Status Code:%s, Headers:%s' % (
                    _stg_url, swift_role_header.status_code, swift_role_header.headers))
                if swift_role_header.status_code <= 299:
                    _x_account_control = swift_role_header.headers.get('X-Account-Access-Control', '')
                    if _x_account_control:
                        x_account_control = json.loads(_x_account_control)
                        try:
                            idx = x_account_control[pre_sfo_role.role_meta].index('%s:%s' % (sfo_swift_user.account_id,
                                                                                             sfo_swift_user.system_user))
                            x_account_control[pre_sfo_role.role_meta].pop(idx)
                        except ValueError, error:
                            access_logger.warning(str(error))
                        role_meta_header = x_account_control.get(cur_sfo_role.role_meta, '')
                        if role_meta_header:
                            sub_role_meta_set = set(x_account_control[cur_sfo_role.role_meta])
                            sub_role_meta_set.add("%s:%s" % (account_id, sfo_swift_user.system_user))
                            x_account_control[cur_sfo_role.role_meta] = list(sub_role_meta_set)
                        else:
                            sub_role_meta_set = set()
                            sub_role_meta_set.add("%s:%s" % (account_id, sfo_swift_user.system_user))
                            x_account_control[cur_sfo_role.role_meta] = list(sub_role_meta_set)
                    else:
                        role_meta_set = set()
                        role_meta_set.add("%s:%s" % (account_id, sfo_swift_user.system_user))
                        x_account_control = {cur_sfo_role.role_meta: list(role_meta_set)}
                    headers.update({'X-Account-Access-Control': json.dumps(x_account_control)})
                    access_logger.info('HEAD_URL:%s, Update Headers:%s' % (
                        _stg_url, headers))
                    password = json.loads(sfo_swift_user.extend)['password']
                    swift_role_control = requests.post(_stg_url,
                                                       headers=headers,
                                                       timeout=5)
                    access_logger.info('HEAD_URL:%s, Status Code:%s, Headers:%s' % (
                        _stg_url, swift_role_control.status_code, swift_role_control.headers))
                    if swift_role_control.status_code <= 299:
                        status = 200
                        message = 'Account Control OK'
                        after_update_header_ensure = requests.head(_stg_url, headers={'X-Auth-Token': stg_token},
                                                                   timeout=5)
                        if after_update_header_ensure.status_code <= 299:
                            ensure_headers(after_update_header_ensure.headers, account_id, sfo_swift_user.system_user,
                                           cur_sfo_role.role_meta)
                        # 删除之前的角色,添加当前的角色
                        access_logger.info('Add Scheduler Job give_away_file_to_proxy')
                        data['password'] = password
                        data['account'] = account_id
                        data['username'] = sfo_swift_user.system_user
                        data['storage_url'] = sfo_account.storage_url
                        data['auth_url'] = sfo_account.auth_url
                        sfo_swift_user.role_name = role
                        db.session.add(sfo_swift_user)
                        db.session.commit()
                    else:
                        status = swift_role_control.status_code
                        message = 'Account Control Fail , Status Code %s' % swift_role_control.status_code
                else:
                    message = 'Head Storage Url %s Fail , Status Code %s' % (_stg_url, swift_role_header.status_code)
    else:
        status = 202
        message = 'Not Found Record From %s or No need to change ' % guid
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


class ClusterSwiftUserListAPI(Resource):

    """
    集群注册账号列表API
    response :
        { 'status': 200/404 , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]

    resource = (SfoAccountManagerMethod, SfoSwiftUserMethod, SfoSwiftRoleMethod)

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(swift_user_list_field)
    def get(self, cluster_name):
        try:
            resp, status = cluster_swift_users_logic(cluster_name)
            return resp, status
        except Exception, error:
            access_logger.error('get ClusterSwiftUserListAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}

    @login_required
    @permission_required(*resource)
    def post(self, cluster_name):
        try:
            user_info_json = request.json
            role = user_info_json.get('role')
            account_id = user_info_json.get('account')
            swift_username = user_info_json.get('swift_username')
            if not swift_username:
                raise ValueError('swift_username is not null')
            resp, status = create_swift_user(cluster_name, swift_username, account_id, role)
            return resp, status
        except ValueError, error:
            access_logger.error('get ClusterSwiftUserInfoAPI get exception %s' % error)
            status = 400
            message = 'Invaild Parameters %s' % str(error)
            return {'status': status, "message": message}
        except Exception, error:
            access_logger.error('get ClusterSwiftUserInfoAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}


class ClusterSwiftUserInfoAPI(Resource):

    resource = (SfoAccountManagerMethod, SfoSwiftUserMethod, SfoSwiftRoleMethod)

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(swift_user_field)
    def get(self, guid):
        try:
            resp = cluster_swift_user_info(guid)
            return resp
        except ValueError, error:
            access_logger.error('get ClusterSwiftUserInfoAPI get exception %s' % error)
            status = 400
            message = 'Invaild Parameters %s' % str(error)
            return {'status': status, "message": message}
        except Exception, error:
            access_logger.error('get ClusterSwiftUserInfoAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}

    @login_required
    @permission_required(*resource)
    def put(self, guid):
        try:
            user_info_json = request.json
            role = user_info_json.get('role')
            account_id = user_info_json.get('account')
            resp = update_swift_user_info(guid, role, account_id)
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

