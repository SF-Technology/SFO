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

import json
import random
import time
import uuid

import requests
from flask import request
from flask_restful import Resource
from keystoneauth1 import session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client
from sqlalchemy import and_
from swiftclient import client as swclient

from sfo_common.config_parser import Config
from sfo_common.models import SfoAccountManager
from sfo_datahandler import db
from sfo_server import access_logger
from sfo_server.models import SfoCofigureMethod, SfoSwiftUserMethod
from sfo_server.resource.cluster_out_api.api_decorate import authentication
from sfo_server.resource.common import capacity_translate
from sfo_utils.utils import Util
from sfo_server.decorate import login_required, permission_required

config = Config()
util = Util()


def rollback(keystonecli,proj_id,user_id):
    """
    错误操作后的回滚操作
    :param keystonecli: keystone初始化客户端
    :param proj_id:   项目id
    :param user_id:   用户id
    :return:
    """
    if proj_id:
        keystonecli.projects.delete(proj_id)
    if user_id:
        keystonecli.users.delete(user_id)



def find_domain(keystonecli, domain_name):
    """
    :param keystonecli:   keystone初始化客户端
    :param domain_name:  寻找的域对象
    :return:
    """
    domains = keystonecli.domains.list()
    for domain in domains:
        if domain.name == domain_name:
            domain_id = domain.id
            return domain_id


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



def init_keystonecli(user, password):
    """
    :param user:   keystone用户,一般为admin
    :param password:  keystone密码
    :return:
    """
    try:
        auth = v3.Password(user_domain_name='default',
                           username=user,
                           password=password,
                           project_domain_name='default',
                           project_name='admin',
                           auth_url=config.swift_auth_url)
        sess = session.Session(auth=auth)
        cli = client.Client(session=sess)
        return cli
    except Exception, error:
        raise RuntimeError(str(error))


def keystone_user_create(keystonecli, username, description, random_password, domain):
    """
    :param keystonecli:  keystone初始化后的客户端
    :param syscode:  系统编码
    :param description:  系统描述
    :param random_password:  用户密码
    :param domain:  系统环境域
    :return:
    """
    try:
        domain_id = find_domain(keystonecli=keystonecli, domain_name=domain)
        if not domain_id:
            raise ValueError('Could Not Found %s'%domain)
        user = keystonecli.users.create(name=username,
                                        description=description,
                                        domain=domain_id,
                                        password=random_password,
                                        enabled=True)
        return user
    except Exception, error:
        raise RuntimeError(str(error))


def keystone_project_create(keystonecli, project, domain, description=None):
    '''
    在keystone中创建project
    :param keystonecli:  keystone初始化后的客户端
    :param domain:  创建项目的系统环境
    :param project: str project name
    :param description: str
    :return:
    '''
    try:
        domain_id = find_domain(keystonecli=keystonecli, domain_name=domain)
        if not domain_id:
            raise ValueError('Could Not Found %s' % domain)
        project = keystonecli.projects.create(name=project, description=description, domain=domain_id, enabled=True)
        return project
    except Exception as ex:
        raise RuntimeError(str(ex))


def keystone_project_delete(keystonecli, project):
    '''
    在keystone中删除project
    :param keystonecli:  keystone初始化后的客户端
    :param project: str keystone project id  or keystone project object
    :return:
    '''
    try:
        keystonecli.projects.delete(project=project)
        return True
    except Exception as ex:
        raise RuntimeError(str(ex))


def get_role_id(keystonecli, rolename):
    '''
    通过角色名获取keystone中的角色id
    :param keystonecli:  keystone初始化后的客户端
    :param rolename: str   role name
    :return:
    '''
    try:
        ls_roles = keystonecli.roles.list()
        for role in ls_roles:
            if role:
                if rolename == role.name:
                    return role.id
                else:
                    continue
    except Exception as ex:
        raise RuntimeError(str(ex))


def grant_role_user_project(keystonecli, rolename, userid, projectid):
    '''
    通过角色授予指定用户指定project的相关角色权限
    :param keystonecli:  keystone初始化后的客户端
    :param rolename: str role name
    :param userid: str userid in keystone
    :param projectid: keystone project id
    :return:
    '''
    try:
        ls_roles = keystonecli.roles.list()
        for role in ls_roles:
            if role:
                if rolename == role.name:
                    keystonecli.roles.grant(role.id, user=userid, project=projectid)
                    return True
                else:
                    continue
        return False
    except Exception as ex:
        raise RuntimeError(str(ex))


def revoke_roles_project(keystonecli,projectid):
    '''
    删除project中所有除超级用户以外的其他用户权限
    :param keystonecli:  keystone初始化后的客户端
    :param projectid: str keystone project id
    :return:
    '''
    try:
        list_roles = keystonecli.role_assignments.list(project=projectid)
        if list_roles:
            for role in list_roles:
                if role.user['id'] == config.swift_user:
                    continue
                else:
                    keystonecli.roles.revoke(role.role['id'], user=role.user['id'], project=projectid)
        return True
    except Exception as ex:
        raise RuntimeError(str(ex))


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


def add_new_account(project_name, jsonstr):
    '''
    在swift中添加account，并对账号进行授权和限制容量
    :param project_name: 项目名
    :param sysname: 项目描述
    :param capacity: 申请容量
    :return:
    '''
    status = ''
    message = ''
    data = {}
    resp = {"status": status, "message": message, "data": data}
    par = jsonstr
    try:
        sysinfo = db.session.query(SfoAccountManager).filter(
            and_(SfoAccountManager.system_code == project_name,
                 SfoAccountManager.account_stat == '1',
                 SfoAccountManager.domain == par['domain'])).first()

        admin_user = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_USERNAME')
        admin_password = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_PASSWORD')
        admin_user_id = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_USER_ID')
        keystonecli = init_keystonecli(user=admin_user.config_value,
                                       password=admin_password.config_value)  #初始化admin keystone用户

        # 如果账号已经存在，不再创建，直接返回相关信息
        if sysinfo:
            access_logger.info('Exists account %s extend capacity entrance'%(sysinfo.account_id))
            access_logger.info('Exists account input parameter %s'%jsonstr)
            if int(par['capacity']) > int(sysinfo.system_capacity):
                ex_capa_rec, status = extend_account_capacity(project_name, par['capacity'], sysinfo.domain)
                if status == 200:
                    sysinfo.system_capacity = par['capacity']
                    access_logger.info('account %s extend capacity %s'%(sysinfo.account_id, sysinfo.system_capacity))
            data['user'] = sysinfo.system_user
            data['account'] = sysinfo.account_id
            data['system_code'] = sysinfo.project_name
            data['capacity'] = capacity_translate(sysinfo.system_capacity)
            sysinfo.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            db.session.add(sysinfo)
            db.session.commit()
            status = 200
            message = 'OK'
        else:
            sysin = SfoAccountManager()
            access_logger.info('Create Account Parameters : %s' % str(jsonstr))
            sysin.project_name = project_name
            sysin.cluster_name = par['clusterName']
            access_logger.info('system_code:%s system_user:%s '%(sysin.system_code, sysin.system_user))
            sysin.description = par['description']
            sysin.system_capacity = par['capacity']
            try:
                random_password = create_random_password()
                username = par.get('username', project_name)
                user = keystone_user_create(keystonecli=keystonecli,
                                            username=username,
                                            description=sysin.system_name,
                                            random_password=random_password,
                                            domain=par['domain'])
                sysin.system_passwd = random_password
                sysin.system_user = username
                sysin.keystone_user_id = user.id
                data['passwd'] = random_password
                # 创建keystone中的project用于swift中的account
                # API
                proj = keystone_project_create(keystonecli=keystonecli,
                                               project=sysin.project_name,
                                               description=sysin.description,
                                               domain=par['domain'])
                if proj:
                    sysin.account_id = proj.id
                    # 添加超级管理权限
                    grec = grant_role_user_project(keystonecli=keystonecli,
                                                   rolename='admin',
                                                   userid=admin_user_id.config_value,
                                                   projectid=proj.id)
                    grec = grec and grant_role_user_project(keystonecli=keystonecli,
                                                            rolename='ResellerAdmin',
                                                            userid=admin_user_id.config_value,
                                                            projectid=proj.id)
                    # 授权用户访问
                    grec = grec and grant_role_user_project(keystonecli=keystonecli,
                                                            rolename='swiftuser',
                                                            userid=sysin.keystone_user_id,
                                                            projectid=proj.id)

                    stg_url, stg_token = stg_authenticate(account=sysin.project_name,
                                                          user=admin_user.config_value,
                                                          passwd=admin_password.config_value,
                                                          domain=par['domain'],
                                                          admin=True)
                else:
                    rollback(keystonecli, sysin.account_id, sysin.keystone_user_id)
                    raise Exception('create project from keystone fail')
                access_logger.info('Create Account auth %s ' % stg_url)
                sfo_swift_user = SfoSwiftUserMethod.create_user(cluster_name=par['clusterName'],
                                                                systemc_user=sysin.system_user,
                                                                account_id=sysin.account_id,
                                                                role_name='admin')
                if sfo_swift_user:
                    sfo_swift_user.extend = json.dumps({"password": sysin.system_passwd})
                    db.session.add(sfo_swift_user)
                    access_logger.info(
                        'clusterName:%s, role: admin, user:%s account_id:%s  Create Swift User Success, ' % (
                            par['clusterName'], sysin.system_user, sysin.account_id))
                else:
                    access_logger.info(
                        'clusterName:%s, role: admin, user:%s account_id:%s  Create Swift User Fail, Reason: Duplicate records ' % (
                            par['clusterName'], sysin.system_user, sysin.account_id))
                capacity = par.get('capacity')
                headers = {'X-Account-Meta-Quota-Bytes': bytes(capacity),
                           "X-Auth-Token": stg_token}
                rrec = requests.post(stg_url,
                                     headers=headers,
                                     timeout=5)
                access_logger.info('Create Account auth %s Return_code:%s' % (stg_url, rrec.status_code))
                if rrec.status_code == 204:
                    data['capacity'] = capacity_translate(par['capacity'])
                    sysin.account_stat = '1'
                    sysin.guid = str(uuid.uuid1())
                    sysin.expire_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                                      time.localtime(time.time() + (86400 * 365)))
                    sysin.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    db.session.add(sysin)
                    container_name = par.get('containerName')
                    if container_name:
                        requrl = stg_url + '/' + container_name
                        crec = requests.put(requrl,
                                            headers={"X-Auth-Token": stg_token},
                                            timeout=5)
                        access_logger.info('Create Container auth %s Return_code:%s ' % (requrl, crec.status_code))
                        if crec.status_code <= 202:
                            status = 200
                            message = 'OK'
                            data['container'] = container_name
                        else:
                            data = {}
                            status = 506
                            message = 'create container for account failed,error code is %s' % (
                                str(crec.status_code))
                            rollback(keystonecli, sysin.account_id, sysin.keystone_user_id)
                    else:
                        status = 200
                        message = 'OK'
                    db.session.commit()
                else:
                    data = {}
                    status = 505
                    message = 'grant role failed or set capacity failed'
                    rollback(keystonecli, sysin.account_id, sysin.keystone_user_id)
            except requests.ConnectTimeout, ex:
                status = 501
                message = str(ex)
                rollback(keystonecli, sysin.account_id, sysin.keystone_user_id)
            except Exception, ex:
                status = 501
                message = str(ex)
                rollback(keystonecli, sysin.account_id, sysin.keystone_user_id)
    except Exception, ex:
        status = 501
        message = str(ex)
    finally:
        resp.update({"status": status, "message": message, "data": data})
        return resp, status


def extend_account_capacity(project_name, capacity, domain):
    '''
    系统扩容，这里通过系统编码查询对应的account然后对account进行扩容
    :param project_name:
    :param capacity:
    :param domain:
    :return:
    '''
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    try:
        ainfo = db.session.query(SfoAccountManager).filter(
            and_(SfoAccountManager.project_name == project_name,
                 SfoAccountManager.account_stat == '1',
                 SfoAccountManager.domain == domain)).first()
        admin_user = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_USERNAME')
        admin_password = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_PASSWORD')
        if ainfo:
            # 设置account容量
            stg_url, stg_token = stg_authenticate(account=project_name,
                                                  user=admin_user.config_value,
                                                  passwd=admin_password.config_value,
                                                  domain=domain,
                                                  admin=True)
            if str(capacity).isdigit() and int(capacity) > int(ainfo.system_capacity):
                rec = requests.post(stg_url,
                                    headers={'X-Account-Meta-Quota-Bytes': bytes(capacity), "X-Auth-Token": stg_token})
                if rec.status_code == 204:
                    ainfo.system_capacity = capacity
                    ainfo.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    db.session.add(ainfo)
                    db.session.commit()
                    status = 200
                    message = 'OK'
                else:
                    status = 503
                    message = 'extend capacity failed'
            else:
                status = 304
                message = 'No expansion is needed'
        else:
            status = 404
            message = 'No system code was found!'
    except Exception as ex:
        status = 501
        message = str(ex)
    finally:
        resp.update({"status": status, "message": message})
        return resp, status


def disable_account(project_name, domain):
    '''
    禁用account，实际并不会真正禁用account，只是将account上除系统管理员以外的所有授权清除
    :param project_name:
    :param domain:
    :return:
    '''
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    try:
        ainfo = db.session.query(SfoAccountManager).filter(
            and_(SfoAccountManager.project_name == project_name,
                 SfoAccountManager.account_stat == '1',
                 SfoAccountManager.domain == domain)).first()
        admin_user = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_USERNAME')
        admin_password = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_PASSWORD')
        keystonecli = init_keystonecli(user=admin_user.config_value,
                                       password=admin_password.config_value)
        if ainfo:
            remove_result = revoke_roles_project(keystonecli=keystonecli, projectid=ainfo.account_id)
            if remove_result:
                ainfo.account_stat = '0'
                ainfo.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                db.session.add(ainfo)
                db.session.commit()
                status = 200
                message = 'OK'
            else:
                status = 503
                message = 'revoke roles failed'
        else:
            status = 404
            message = 'No system code was found!'
    except Exception as ex:
        status = 501
        message = str(ex)
    finally:
        resp.update({"status": status, "message": message})
        return resp, status


def create_container_to_account(container_name, project_name, domain):
    '''
    校验account和manager，然后向指定的account下创建传入名称的container
    :param container_name:
    :param account:
    :param manager:
    :return:
    '''
    status = ''
    message = ''
    data = {}
    resp = {"status": status, "data": data, "message": message}
    try:
        ainfo = db.session.query(SfoAccountManager).filter(
            and_(SfoAccountManager.account_stat == '1',
                 SfoAccountManager.project_name == project_name,
                 SfoAccountManager.domain == domain)).first()
        admin_user = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_USERNAME')
        admin_password = SfoCofigureMethod.query_value_from_con_key('KEYSTONE_PASSWORD')
        if ainfo:
            stg_url, stg_token = stg_authenticate(account=project_name,
                                                  user=admin_user.config_value,
                                                  passwd=admin_password.config_value,
                                                  domain=domain,
                                                  admin=True)
            account_stat, container_list = swclient.get_account(stg_url, stg_token)
            if container_name:
                if len(container_list) > 0:
                    has_ctn_list = map(lambda x: x['name'], container_list)
                    if container_name in has_ctn_list:
                        raise ValueError('Container %s exists ' % container_name )
            requrl = stg_url + '/' + container_name
            crec = requests.put(requrl, headers={"X-Auth-Token": stg_token})
            if crec.status_code <= 202:
                status = 200
                message = 'OK'
                data['url'] = requrl
            else:
                status = 503
                message = 'Container create failed'
        else:
            status = 404
            message = "Not Found Record"
    except Exception as ex:
        status = 501
        message = str(ex)
    finally:
        resp.update({"status": status, "data": data, "message": message})
        return resp, status


class SystemAccessApi(Resource):

    resource = (SfoAccountManager, SfoSwiftUserMethod)

    @login_required
    @permission_required(*resource)
    def post(self, project_name):
        try:
            params = request.json
            if project_name is None or params is None:
                status = 400
                message = 'null param is not supported!'
                return {'status': status, "message": message}, status
            else:
                if not params.get('clusterName', ''):
                    status = 400
                    message = 'clusterName is None!'
                    return {'status': status, "message": message}, status
                if not params.get('domain', ''):
                    status = 400
                    message = 'domain is None!'
                    return {'status': status, "message": message}, status
                else:
                    params['domain'] = params['domain'].upper()
                if not params.get('description', ''):
                    status = 400
                    message = 'description is None!'
                    return {'status': status, "message": message}, status
                if not params.get('capacity', ''):
                    status = 400
                    message = 'capacity is None!'
                    return {'status': status, "message": message}, status
                if not str(params['capacity']).isdigit():
                    status = 400
                    message = 'capacity must be number!'
                    return {'status': status, "message": message}, status
                else:
                    params['capacity'] = int(params['capacity']) * pow(1024, 3)
            resp, status = add_new_account(project_name, params)
            return resp
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def put(self, project_name):
        try:
            param = request.json
            capacity = param.get('capacity', '')
            domain = param.get('domain')
            if project_name is None or capacity is None or domain is None:
                status = 400
                message = '(capacity/domain) null param is not supported!'
                return {'status': status, "message": message}, status
            capacity = int(capacity) * pow(1024, 3)
            resp, status = extend_account_capacity(project_name, capacity, domain)
            return resp
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def delete(self, project_name):
        try:
            param = request.json
            domain = param.get('domain', '')
            if project_name is None:
                status = 400
                message = 'null param is not supported!'
                return {'status': status, "message": message}, status
            resp, status = disable_account(project_name, domain)
            return resp, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status


class SystemManagerApi(Resource):

    resource = (SfoAccountManager, SfoSwiftUserMethod)

    @login_required
    @permission_required(*resource)
    def post(self, project_name):
        try:
            param = request.json
            keyword = param.get('keyword', '')
            domain = param.get('domain', '')
            if project_name is None or domain is None:
                status = 400
                message = 'null param is not supported!'
                return {'status': status, "message": message}, status
            if keyword == 'add_container':
                container_name = param.get('containerName', '')
                resp, status = create_container_to_account(container_name, project_name, domain)
                return resp, status
            else:
                message = 'keyword is null'
                raise ValueError(message)
        except ValueError, error:
            status = 400
            message = str(error)
            return {'status': status, "message": message}
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status
