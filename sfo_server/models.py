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

import datetime
import json
import time
import uuid
from functools import wraps

from sqlalchemy import and_, func, or_, not_
from sqlalchemy.orm.query import _entity_descriptor

from sfo_common.models import *
from sfo_server.resource.common import strft_2_timestamp, timestamp_format
from sfo_utils.utils import Util

sf_utils = Util()

roles_2_users = db.Table('sfo_server_roles_to_users',
                         db.Column('user_account', db.String(128), db.ForeignKey('sfo_server_user.user_account',
                                                                                 ondelete='CASCADE',
                                                                                 onupdate='CASCADE')),
                         db.Column('role_name', db.String(128), db.ForeignKey('sfo_server_role.role_name',
                                                                              ondelete='CASCADE',
                                                                              onupdate='CASCADE')))

permissions_2_roles = db.Table('sfo_server_permissions_to_roles',
                               db.Column('role_name', db.String(128), db.ForeignKey('sfo_server_role.role_name',
                                                                                    ondelete='CASCADE',
                                                                                    onupdate='CASCADE'
                                                                                    )),
                               db.Column('permission_name', db.String(128),
                                         db.ForeignKey('sfo_server_permission.permission_name',
                                                       ondelete='CASCADE',
                                                       onupdate='CASCADE'
                                                       )))


def clean_session_after_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as error:
            pass
        finally:
            if db.session.registry.has():
                db.session.close()
                db.session.remove()
    return wrapper


class SfoClusterMethod(SfoCluster):

    @classmethod
    def create(cls, cluster_name, creater, cluster_stat='public', extend=''):
        clu = db.session.query(cls).filter(cls.cluster_name == cluster_name).first()
        if not clu:
            clu = cls()
            clu.guid = str(uuid.uuid1())
            clu.cluster_name = cluster_name
            clu.creater = creater
            clu.extend = extend
            clu.add_time = timestamp_format(time.time())
            clu.cluster_stat = cluster_stat
            return clu

    @classmethod
    def query_cluster_list(cls):
        return db.session.query(cls).group_by(cls.cluster_name).all()

    @classmethod
    def query_cluster_by_cluster_name(cls, cluster_name):
        return db.session.query(cls).filter(cls.cluster_name == cluster_name).first()

    @classmethod
    def query_cluster_public_list(cls):
        return db.session.query(cls).filter(cls.cluster_stat == 'public').group_by(cls.cluster_name).all()

    @classmethod
    def query_cluster_special_list(cls):
        return db.session.query(cls).filter(cls.cluster_stat == 'dedicated').group_by(cls.cluster_name).all()


class SfoServerAccessLog(db.Model):

    """
    记录用户登录操作信息
    """

    __tablename__ = 'sfo_server_access_log'

    guid = db.Column(db.String(128), primary_key=True)
    access_user = db.Column(db.String(128), nullable=False)
    access_time = db.Column(db.String(128), nullable=False)
    access_method = db.Column(db.String(128), nullable=False)
    access_path = db.Column(db.String(128), nullable=False)
    access_result = db.Column(db.String(128), nullable=True)
    access_result_message = db.Column(db.String(128))
    add_time = db.Column(db.String(128), nullable=False)

    @classmethod
    def add_access_log(cls, user, method, path, ctime, result, resmsg):
        try:
            sfo_server_acc_log = cls()
            sfo_server_acc_log.guid = str(uuid.uuid1())
            sfo_server_acc_log.access_user = user
            sfo_server_acc_log.access_method = method
            sfo_server_acc_log.access_path = path
            sfo_server_acc_log.access_time = ctime
            sfo_server_acc_log.access_result = result
            sfo_server_acc_log.access_result_message = resmsg
            sfo_server_acc_log.add_time = timestamp_format(time.time())
            db.session.add(sfo_server_acc_log)
            db.session.commit()
        except Exception:
            pass


class SfoServerUser(db.Model):

    __tablename__ = 'sfo_server_user'

    guid = db.Column(db.String(128), primary_key=True, nullable=False)
    user_account = db.Column(db.String(128), nullable=False, unique=True)
    cluster_account = db.Column(db.String(128), nullable=True)
    cluster_name = db.Column(db.String(128), nullable=True)
    display_name = db.Column(db.String(128), nullable=True)
    active_status = db.Column(db.Boolean, default=1)
    is_clusteradmin = db.Column(db.Boolean, default=0)
    roles = db.relationship('SfoServerRole',
                            secondary=roles_2_users,
                            backref=db.backref('users', lazy='select'), lazy='select', passive_deletes=True)
    last_login_time = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<%s>' % self.user_account

    @classmethod
    def query_user(cls, guid):
        """
        根据id查询用户信息
        :param guid:
        :return:
        """
        return db.session.query(cls).filter(and_(cls.guid == guid, cls.active_status != 0)).first()

    @classmethod
    def query_user_by_account(cls, user_account):
        """
        根据user_account查询用户信息
        :param user_account:
        :return:
        """
        return db.session.query(cls).filter(and_(cls.user_account == user_account, cls.active_status != 0)).first()

    @classmethod
    def query_active_user_list(cls):
        return db.session.query(cls).filter(and_(cls.active_status == 1, cls.is_clusteradmin == 0)).all()

    @staticmethod
    def create_default_user(username, display_name, is_clusteradmin=False):
        """
        默认创建用户记录 且用户是visitor角色
        :param username:  用户名
        :param display_name:  用户ldap的显示名
        :param is_clusteradmin:  控制是否是超级管理员
        :return:
        """
        new_sfo_server_user = SfoServerUser()
        new_sfo_server_user.guid = str(uuid.uuid4())
        new_sfo_server_user.user_account = username
        new_sfo_server_user.display_name = display_name
        new_sfo_server_user.is_clusteradmin = is_clusteradmin
        if not is_clusteradmin:
            new_sfo_server_user.roles = [SfoServerRole.query_role_by_name('visitor')]
        new_sfo_server_user.add_time = new_sfo_server_user.last_login_time = timestamp_format(time.time())
        return new_sfo_server_user


class SfoServerRole(db.Model):

    __tablename__ = 'sfo_server_role'

    guid = db.Column(db.String(128), primary_key=True, nullable=False)
    role_name = db.Column(db.String(128), unique=True, nullable=False)
    role_desc = db.Column(db.String(256), nullable=True)
    last_modify_time = db.Column(db.String(128), nullable=False)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<%s>' % self.role_name

    @classmethod
    def query_role(cls, guid):
        return db.session.query(cls).filter(cls.guid == guid).first()

    @classmethod
    def query_role_by_name(cls, role_name):
        return db.session.query(cls).filter(cls.role_name == role_name).first()

    @staticmethod
    def create_default_role_permission():
        """
        对给予的资源生成默认的两个角色 ['admin', 'visitor']
        :return:
        """
        default_role = ['admin', 'visitor']
        roles = []
        for role in default_role:
            old_role = SfoServerRole.query_role_by_name(role)
            if not old_role:
                new_role = SfoServerRole()
                new_role.role_name = role
                new_role.guid = str(uuid.uuid4())
                new_role.add_time = new_role.last_modify_time = timestamp_format(time.time())
                if role == 'admin':
                    new_role.role_desc = u'管理员'
                    permissions = SfoServerPermission.query.filter(or_(and_(
                        SfoServerPermission.permission_name.notlike('%_sfo_server_role'),
                        SfoServerPermission.permission_name.notlike('%_sfo_server_user'),
                        SfoServerPermission.permission_name.notlike('%_sfo_server_permission'),
                        SfoServerPermission.permission_name.notlike('%_sfo_server_roles_to_users'),
                        SfoServerPermission.permission_name.notlike('%_sfo_server_permissions_to_roles'),
                    ),
                        SfoServerPermission.permission_name.like('get_%')
                    )).all()
                elif role == 'visitor':
                    new_role.role_desc = u'访问者'
                    permissions = SfoServerPermission.query.\
                        filter(SfoServerPermission.permission_name.like('get_%')).all()
                else:
                    permissions = []
                new_role.permissions = permissions
                roles.append(new_role)
            else:
                if role == 'admin':
                    old_role.role_desc = u'管理员'
                    permissions = SfoServerPermission.query.filter(or_(and_(
                        SfoServerPermission.permission_name.notlike('%_sfo_server_role'),
                        SfoServerPermission.permission_name.notlike('%_sfo_server_user'),
                        SfoServerPermission.permission_name.notlike('%_sfo_server_permission'),
                        SfoServerPermission.permission_name.notlike('%_sfo_server_roles_to_users'),
                        SfoServerPermission.permission_name.notlike('%_sfo_server_permissions_to_roles'),
                    ),
                        SfoServerPermission.permission_name.like('get_%')
                    )).all()
                elif role == 'visitor':
                    old_role.role_desc = u'访问者'
                    permissions = SfoServerPermission.query.\
                        filter(SfoServerPermission.permission_name.like('get_%')).all()
                else:
                    permissions = []
                old_role.permissions = permissions
                roles.append(old_role)
        return roles

    @classmethod
    def query_roles(cls, roles):
        return db.session.query(cls).filter(cls.role_name.in_(roles)).all()


class SfoServerPermission(db.Model):

    __tablename__ = 'sfo_server_permission'

    guid = db.Column(db.String(128), primary_key=True, nullable=False)
    resource_name = db.Column(db.String(128), db.ForeignKey('sfo_server_resource.table_name',
                                                            ondelete='CASCADE',
                                                            onupdate='CASCADE'))
    roles = db.relationship('SfoServerRole', secondary=permissions_2_roles,
                            backref=db.backref('permissions', lazy='select'), lazy='select', passive_deletes=True)
    permission_name = db.Column(db.String(128), nullable=False, unique=True)
    permission_desc = db.Column(db.String(256), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<%s>' % self.permission_name

    @staticmethod
    def create_default_permission(resource_name):
        """
        对给予的资源生成默认的三个权限 ['get',post, put , delete]
        :param resource_name: 权限控制资源名称
        :return:
        """
        default_methods = ['get', 'post', 'put', 'delete']
        desc = 'Can %s %s'
        permission_list = []
        for method in default_methods:
            permission = SfoServerPermission()
            permission.guid = str(uuid.uuid4())
            permission.resource_name = resource_name
            permission.permission_name = method + '_' + resource_name
            permission.permission_desc = desc % (method, resource_name)
            permission.add_time = timestamp_format(time.time())
            permission_list.append(permission)
        return permission_list

    @classmethod
    def query_permissions(cls, permissions):
        return db.session.query(cls).filter(cls.permission_name.in_(permissions)).all()


class SfoServerResource(db.Model):

    __tablename__ = 'sfo_server_resource'

    guid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    table_name = db.Column(db.String(128), unique=True, nullable=False)
    permissions = db.relationship('SfoServerPermission', backref='resource', lazy='select', passive_deletes=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<%s>' % self.table_name

    @classmethod
    def query_resource(cls, guid):
        return db.session.query(cls).filter(cls.guid == guid).first()

    def create_default_resource(self, table_name, permission_list):
        self.table_name = table_name
        self.permissions = permission_list
        self.add_time = timestamp_format(time.time())
        return self

    @classmethod
    def query_all_resource(cls):
        return db.session.query(cls.table_name).all()


class SfoManagerTaskLog(db.Model):

    __tablename__ = 'sfo_manager_task_list'

    guid = db.Column(db.String(128), primary_key=True)
    taskid = db.Column(db.String(128), nullable=False)
    excute_description = db.Column(db.TEXT)
    excute_message = db.Column(db.TEXT)
    add_time = db.Column(db.String(128))
    end_time = db.Column(db.String(128))

    def __repr__(self):
        return '<SfoManagerTaskLog %s>' % self.taskid


class SfoTasksList(db.Model):

    __tablename__ = 'sfo_tasks_list'

    guid = db.Column(db.String(128), primary_key=True)
    create_user = db.Column(db.String(128))
    node_host_name = db.Column(db.String(128))
    service_type = db.Column(db.String(128))
    service_name = db.Column(db.TEXT)
    operation = db.Column(db.String(128))
    service_task_ending_flag = db.Column(db.String(128))
    task_start_time = db.Column(db.DateTime, default=datetime.datetime.now)
    task_end_time = db.Column(db.String(128))

    def __repr__(self):
        return '<SfoTasksList %s %s>' % (self.node_host_name, self.service_name)



class SfoTasksListMethod(SfoTasksList):

    @classmethod
    def query_tasks_by_service(cls, service_type):
        return db.session.query(cls).filter(cls.service_type == service_type, cls.service_task_ending_flag != '1').all()

    @classmethod
    def query_tasks_by_guid(cls, guid):
        return db.session.query(cls).filter(cls.guid == guid).first()

    @classmethod
    def query_service_is_running(cls, hostname, operation, service='', service_type=''):
        return db.session.query(cls).filter(or_(and_(cls.service_name == service,
                                                     cls.node_host_name == hostname,
                                                     cls.operation == operation,
                                                     cls.service_task_ending_flag == '0'),
                                                and_(cls.service_type == service_type,
                                                     cls.node_host_name == hostname,
                                                     cls.operation == operation,
                                                     cls.service_name == service,
                                                     cls.service_task_ending_flag == '0'))).first()

    @classmethod
    def create_or_update_task(cls, operation, service_type='', service_name='', hostname='', end_flag='0', endtime='', username='', guid=''):
        service_task = cls()
        service_task.guid = guid if guid else str(uuid.uuid1())
        service_task.create_user = username
        service_task.node_host_name = hostname
        service_task.service_type = service_type
        service_task.service_name = service_name
        service_task.operation = operation
        service_task.service_task_ending_flag = end_flag
        service_task.task_end_time = endtime
        return service_task

    @classmethod
    def query_by_filterkey(cls, create_user='', **query_map):
        clauses = [_entity_descriptor(db.session.query(cls)._joinpoint_zero(), key) == value
                   for key, value in query_map.items()]
        filter_key = or_(*clauses)
        if create_user:
            filter_key = and_(cls.create_user == create_user, filter_key)
        return db.session.query(cls).filter(filter_key).order_by(SfoTasksListMethod.task_start_time.desc()).all()


class SfoManagerTaskLogMethod(SfoManagerTaskLog):

    @classmethod
    def create_manager_task_log(cls, taskid, excute_message, excute_description, end_time):
        manager_log = cls()
        manager_log.guid = str(uuid.uuid1())
        manager_log.taskid = taskid
        manager_log.excute_message = excute_message
        manager_log.excute_description = excute_description
        manager_log.add_time = timestamp_format(time.time())
        manager_log.end_time = end_time
        return manager_log

    @classmethod
    def query_manager_log_by_taskid(cls, taskid):
        return db.session.query(cls).filter(cls.taskid == taskid).order_by(cls.end_time).all()

    @classmethod
    def query_manager_log_by_filter_key(cls, taskid=None, start_time=None, end_time=None, page=1, limit=10):
        and_clause = []
        if taskid:
            and_clause.append(cls.taskid == taskid)
        if start_time:
            and_clause.append(cls.add_time >= start_time)
        if end_time:
            and_clause.append(cls.add_time <= end_time)
        datas_query = cls.query.filter(and_(*and_clause)).order_by(cls.end_time.desc())
        if page and limit:
            data = datas_query.paginate(page, limit)
        else:
            data = datas_query.all()
        return data


class SfoClusterInfoMethod(SfoClusterInfo):

    @classmethod
    def query_start2end_region_list_info(cls, cluster_name, start_time, end_time):
        """
        根据开始 结束时间获取 集合区间
        :param cluster_name:  集群名
        :param start_time:  开始时间
        :param end_time:    结束时间
        :return:    对象集合列表
        """

        return db.session.query(cls) \
            .filter(and_(cls.cluster_name == cluster_name, cls.add_time >= start_time, cls.add_time <= end_time)) \
            .order_by(cls.add_time).all()

    @classmethod
    def query_last_cluster_overview(cls, cluster_name):
        """
        获取最新 一次集群采集信息"对象模型"
        #假设超过当前时间的半个小时内的最新数据视为无效数据
        :return:  cluster_model_instance 集群模型实例
        """
        return db.session.query(cls).filter(and_(cls.cluster_name == cluster_name,
                                                 ))\
            .order_by(cls.add_time.desc()).first()

    @classmethod
    def query_by_guid(cls, guid):
        """
        根据guid 获取详细信息
        :param guid:  str  guid
        :return: cluster_model_instance 集群模型实例
        """
        return db.session.query(cls).filter_by(guid=guid).first()

    @classmethod
    def query_by_cluster_name(cls, cluster_name):
        return db.session.query(cls).filter(cls.cluster_name == cluster_name).first()

    @classmethod
    def query_last_clusters_info(cls):
        last_mx_time = db.session.query(func.max(cls.add_time).label('mx_time'), cls.cluster_name)\
            .group_by(cls.cluster_name).subquery()
        data = db.session.query(cls).join(last_mx_time, and_(cls.add_time == last_mx_time.c.mx_time,
                                                             cls.cluster_name == last_mx_time.c.cluster_name)).all()
        return data


class SfoClusterInfoHourMethod(SfoClusterInfo_hour, SfoClusterInfoMethod):
    pass


class SfoClusterInfoDayMethod(SfoClusterInfo_day, SfoClusterInfoMethod):
    pass


class SfoClusterNodesMethod(SfoClusterNodes):

    @classmethod
    def query_cluster_list(cls):
        """
        获取现有集群名列表
        :return:
        """
        return db.session.query(cls.cluster_name).filter(cls.cluster_name != '').group_by(cls.cluster_name).all()

    @classmethod
    def query_host_list_by_cluster_name(cls, cluster_name):
        """
        根据集群名查询主机列表
        :param cluster_name:
        :return:
        """
        return db.session.query(cls).filter(and_(cls.cluster_name == cluster_name, cls.node_stat == '1')).all()

    @classmethod
    def category_node_list(cls, cluster_name):
        """
        对集群的节点角色进行分类
        :param cluster_name:  集群名
        :return:    代理节点主机列表, 存储节点主机列表
        """
        host_list = cls.query_host_list_by_cluster_name(cluster_name)
        proxy_host_list = filter(lambda x: json.loads(x.node_role)['Proxy-Server'] == 'YES', host_list)
        storage_host_list = filter(lambda x: json.loads(x.node_role)['Account-Server'] == 'YES' or
                                             json.loads(x.node_role)['Container-Server'] == 'YES' or
                                             json.loads(x.node_role)['Object-Server'] == 'YES'
                                             , host_list)
        return proxy_host_list, storage_host_list

    @classmethod
    def query_host_by_host_name(cls, host_name):
        return db.session.query(cls).filter(cls.node_host_name == host_name).first()

    @classmethod
    def create_or_update(cls, node_host_name, node_inet_ip, node_replicate_ip, node_role, cluster_name=''):
        sfo_node = db.session.query(cls).filter(cls.node_host_name == node_host_name).first()
        if sfo_node and sfo_node.node_stat != '1':
            sfo_node.node_stat = '1'
            sfo_node.cluster_name = cluster_name
        elif not sfo_node:
            sfo_node = cls()
            sfo_node.guid = str(uuid.uuid1())
            sfo_node.node_host_name = node_host_name
            sfo_node.node_inet_ip = node_inet_ip
            sfo_node.node_replicate_ip = node_replicate_ip
            sfo_node.node_stat = '1'
            sfo_node.node_role = node_role
            sfo_node.cluster_name = cluster_name
            sfo_node.add_time = timestamp_format(time.time())
        else:
            pass
        return sfo_node

    @classmethod
    def query_not_used_hosts(cls):
        return db.session.query(cls).filter(not_(cls.cluster_name != '')).all()

    @classmethod
    def query_host_list_by_hostip(cls, hostip):
        """
        根据集群名查询主机列表
        :param hostip:
        :return:
        """
        return db.session.query(cls).filter(and_(cls.node_inet_ip == hostip, cls.node_stat == '1')).first()


class SfoDiskPerformMethod(SfoDiskPerform):

    @classmethod
    def query_disk_list_by_hostname(cls, host_name, starttime, endtime):
        data = db.session.query(cls).filter(and_(cls.host_name == host_name,
                                                 cls.add_time >= starttime,
                                                 cls.add_time <= endtime,
                                                 cls.disk_total != '0')).order_by(cls.add_time).all()
        return data

    @classmethod
    def query_last_disk_info(cls):
        data = db.session.query(cls).filter(cls.disk_total != '0').group_by(cls.disk_name, cls.host_name).all()
        return data

    @classmethod
    def query_disk_io(cls, starttime, endtime):
        data = db.session.query(cls).filter(and_(cls.add_time >= starttime,
                                                 cls.add_time <= endtime,
                                                 cls.disk_total != '0')).order_by(cls.add_time).all()
        return data

    def read_bytes_diff(self, other):
        """
        获取两个对象read_bytes的差值 == > read_bytes差值 = 当前时间段内读取的字节
        :param other:
        :return:
        """
        self_read_bytes = float(self.read_bytes)
        other_read_bytes = float(other.read_bytes)
        time_diff = self.add_time_diff(other)
        return abs(self_read_bytes - other_read_bytes) // time_diff if time_diff else 1

    def read_count_diff(self, other):
        """
        获取两个对象read_count的差值 == > read_count差值 = 当前时间段内读取的字节
        :param other:
        :return:
        """
        self_read_count = float(self.read_count)
        other_read_count = float(other.read_count)
        time_diff = self.add_time_diff(other)
        return abs(self_read_count - other_read_count) // time_diff if time_diff else 1

    def write_count_diff(self, other):
        """
        获取两个对象write_count的差值 == > write_count差值 = 当前时间段内读取的字节
        :param other:
        :return:
        """
        self_write_count = float(self.write_count)
        other_write_count = float(other.write_count)
        time_diff = self.add_time_diff(other)
        return abs(self_write_count - other_write_count) // time_diff if time_diff else 1

    def write_bytes_diff(self, other):
        """
        获取两个对象的write_bytes的差值
        :param other:
        :return:
        """
        self_write_bytes = float(self.write_bytes)
        other_write_bytes = float(other.write_bytes)
        time_diff = self.add_time_diff(other)
        return abs(self_write_bytes - other_write_bytes) // time_diff if time_diff else 1

    def add_time_diff(self, other):
        self_add_time = int(strft_2_timestamp(self.add_time))
        other_add_time = int(strft_2_timestamp(other.add_time))
        return abs(self_add_time - other_add_time)

    def await(self, other):
        self_read_time = float(self.read_time)
        other_read_time = float(other.read_time)
        self_read_count = float(self.read_count)
        other_read_count = float(other.read_count)
        _read_time_diff = abs(self_read_time - other_read_time)
        _read_count_diff = abs(self_read_count - other_read_count)
        return _read_time_diff / _read_count_diff if _read_count_diff else 1

    def await_diff(self, other):
        self_read_time = float(self.read_time)
        other_read_time = float(other.read_time)
        self_write_time = float(self.write_time)
        other_write_time = float(other.write_time)
        self_read_count = float(self.read_count)
        other_read_count = float(other.read_count)
        self_write_count = float(other.write_count)
        other_write_count = float(other.write_count)
        add_time_diff = self.add_time_diff(other)
        _read_time_diff = abs(self_read_time - other_read_time)
        _write_time_diff = abs(self_write_time - other_write_time)
        _read_count_diff = abs(self_read_count - other_read_count)
        _write_count_diff = abs(self_write_count - other_write_count)
        io_time_total = _read_time_diff + _write_time_diff
        io_total = _read_count_diff + _write_count_diff
        refresh_busy_time = io_time_total / io_total if io_total else 1
        return refresh_busy_time / add_time_diff if add_time_diff else 1

    @classmethod
    def query_disk_info(cls, host_name, diskname):
        return db.session.query(cls).filter(and_(cls.host_name == host_name,
                                                 cls.disk_name == diskname)).order_by(cls.add_time.desc()).first()

    @classmethod
    def query_diskinfo_by_hostname(cls, host_name):
        data = db.session.query(cls)\
            .filter(and_(cls.disk_total != '0', cls.host_name == host_name))\
            .group_by(cls.disk_name, cls.host_name).all()
        return data

    @classmethod
    def query_last_diskinfo_by_hostname(cls, host_name):
        data = SfoDiskPerform.query.filter(
            and_(SfoDiskPerform.host_name == host_name, SfoDiskPerform.disk_total != '0')).order_by(
            SfoDiskPerform.add_time.desc()).limit(100).all()
        return data


class SfoDiskPerform5MinMethod(SfoDiskPerform_5min, SfoDiskPerformMethod):
    pass


class SfoDiskPerformHourMethod(SfoDiskPerform_hour, SfoDiskPerformMethod):
    pass


class SfoDiskPerformDayMethod(SfoDiskPerform_day, SfoDiskPerformMethod):
    pass


class SfoDiskPerformHistoryMethod(SfoDiskPerformHistory, SfoDiskPerformMethod):
    pass


class SfoHostInfoMethod(SfoHostInfo):

    @classmethod
    def query_host_info_by_host_name(cls, host_name):
        """
        查询单个节点主机具体信息
        :param host_name:  str  host_name
        :return:  主机信息模型 或者 None
        """
        return db.session.query(cls).filter(cls.host_name == host_name).order_by(cls.add_time.desc()).first()

    @classmethod
    def query_last_host_info_list(cls):
        """
        查询最新采集的集群主机列表
        :return:  主机列表 或者 []
        """
        last_host_mx_time = db.session.query(func.max(cls.add_time).label('mx_time'), cls.host_name)\
            .group_by(cls.host_name).subquery()
        last_host = db.session.query(cls).join(last_host_mx_time,
                                               and_(cls.add_time == last_host_mx_time.c.mx_time,
                                                    cls.host_name == last_host_mx_time.c.host_name)).all()
        return last_host


class SfoNodePerformMethod(SfoNodePerform):

    @classmethod
    def query_node_per_by_host_name(cls, host_name, start_time, end_time):
        """
        根据主机名查询该节点的执行数据信息
       :param host_name:  str  主机
       :param start_time:  str  字符串日期格式  查询范围起始时间
        :param end_time:  str  字符串日期格式    查询范围结束时间
        :return:  所有节点主机信息模型 或者 None
        """
        group_by_host_name = db.session.query(cls.host_name) \
            .group_by(cls.host_name).having(cls.host_name == host_name).subquery()
        return db.session.query(cls) \
            .join(group_by_host_name, cls.host_name == group_by_host_name.c.host_name) \
            .filter(and_(cls.add_time >= start_time, cls.add_time <= end_time)).order_by(cls.add_time).all()

    @classmethod
    def query_node_per_by_cluster_name(cls, cluster_name):
        """
        根据集群名获取该集群下的主机的采集数据
        :param cluster_name: 集群名
        :return:
        """
        last_max_time = db.session.query(func.max(cls.add_time).label('mx_time'),
                                         cls.host_name).group_by(cls.host_name).subquery()
        cluster_node = db.session.query(SfoClusterNodes.node_host_name)\
            .filter(SfoClusterNodes.cluster_name == cluster_name).all()
        data = db.session.query(cls).join(last_max_time, and_(cls.add_time == last_max_time.c.mx_time,
                                                              cls.host_name == last_max_time.c.host_name)) \
            .filter(cls.host_name.in_([host[0] for host in cluster_node])).all()
        return data


class SfoNodePerform5MinMethod(SfoNodePerform_5min, SfoNodePerformMethod):
    pass


class SfoNodePerformHourMethod(SfoNodePerform_hour, SfoNodePerformMethod):
    pass


class SfoNodePerformDayMethod(SfoNodePerform_day, SfoNodePerformMethod):
    pass


class SfoNodePerformHistoryMethod(SfoNodePerformHistory, SfoNodePerformMethod):
    pass


class SfoNodeServiceMethod(SfoNodeService):

    @classmethod
    def query_node_srv_by_host_name(cls, host_name):
        """
        根据主机名获取最新采集的几点服务信息
        :return:  所有节点服务信息模型 或者 None
        """
        return db.session.query(cls).filter(cls.host_name == host_name).order_by(cls.add_time.desc()).first()

    @classmethod
    def query_node_srv_last_info(cls):
        last_mx_time = db.session.query(func.max(cls.add_time).label('mx_time'), cls.host_name)\
            .group_by(cls.host_name).subquery()
        data = db.session.query(cls).join(last_mx_time, and_(cls.add_time == last_mx_time.c.mx_time,
                                                             cls.host_name == last_mx_time.c.host_name)).all()
        return data


class SfoNodeStatMethod(SfoNodeStat):

    @classmethod
    def query_node_stat_list_by_hostname(cls, host_name, start_time, end_time):
        """
        查询节点主机具体信息
       :param host_name:  str  主机名
       :param start_time:  str  字符串日期格式  查询范围起始时间
        :param end_time:  str  字符串日期格式    查询范围结束时间
        :return:  所有节点主机信息模型 或者 None
        """
        group_by_host_name = db.session.query(cls.host_name)\
            .group_by(cls.host_name).having(cls.host_name == host_name).subquery()
        return db.session.query(cls)\
            .join(group_by_host_name, cls.host_name == group_by_host_name.c.host_name) \
            .filter(and_(cls.add_time >= start_time, cls.add_time <= end_time)).order_by(cls.add_time).all()

    @classmethod
    def query_last_node_stat(cls, host_name):
        """
        最新的一次采集数据,返回一个"对象模型"
        :param  host_name : str 主机名
        :return: 对象模型实例 or None
        """
        return db.session.query(cls)\
            .group_by(cls.add_time)\
            .having(cls.host_name == host_name).order_by(cls.add_time.desc()).first()

    @classmethod
    def query_node_mem_info(cls, cluster_name, starttime, endtime):
        """
        查询集群各节点的内存使用信息
        :param cluster_name: 集群名
        :param starttime: 起始时间
        :param endtime: 结束时间
        :return: 数据集,主机名列表
        """
        host_name_list = db.session.query(SfoClusterNodes.node_host_name)\
            .filter(SfoClusterNodes.cluster_name == cluster_name).all()
        data = db.session.query(cls)\
            .filter(and_(cls.add_time >= starttime,
                         cls.add_time <= endtime,
                         cls.host_name.in_([host[0] for host in host_name_list]))).order_by(cls.add_time).all()
        return data, host_name_list

    @classmethod
    def query_cpu_frequency_region(cls, cluster_name, start_time, end_time):
        """
        查询Cpu频率
        :param cluster_name:  集群名
        :param start_time: 开始时间
        :param end_time:   结束时间
        :return:
        """
        host_name_list = db.session.query(SfoClusterNodes)\
            .filter(SfoClusterNodes.cluster_name == cluster_name).all()
        data = db.session.query(cls)\
            .filter(and_(cls.add_time >= start_time,
                         cls.add_time <= end_time,
                         cls.host_name.in_([host.node_host_name for host in host_name_list])))\
            .order_by(cls.add_time).all()
        return data

    @classmethod
    def query_net_used_by_cluster_name(cls, node_list, start_time, end_time):
        """
        查询网卡使用
        :param cluster_name:  集群名
        :param node_role:  节点角色
        :param start_time:  开始时间
        :param end_time:  结束时间
        :return:
        """
        data = db.session.query(cls).filter(and_(cls.add_time >= start_time,
                                                 cls.add_time <= end_time,
                                                 cls.host_name.in_([host.node_host_name for host in node_list])))\
            .order_by(cls.add_time).all()
        return data, node_list

    def diff_net_card_send_bytes(self, other):
        """
        前提：接收的两个对象必须是同一个主机
        返回网卡的发送字节和接收字节
        :param other:
        :return: send_bytes
        """
        net_card_send_map = {}
        diff_add_time = abs(strft_2_timestamp(self.add_time) - strft_2_timestamp(other.add_time))
        self_send_bytes = json.loads(self.net_send_bytes)
        other_send_bytes = json.loads(other.net_send_bytes)
        if self.host_name == other.host_name:
            for net_card in self_send_bytes:
                net_card_send_bytes = round(abs(float(other_send_bytes[net_card]) - float(self_send_bytes[net_card]))/(diff_add_time if diff_add_time else 1), 2)
                net_card_send_map.update({net_card: net_card_send_bytes})
        return net_card_send_map

    def diff_net_card_recv_bytes(self, other):
        """
        前提：接收的两个对象必须是同一个主机
        返回网卡的发送字节和接收字节
        :param other:
        :return: send_bytes
        """
        net_card_recv_map = {}
        diff_add_time = abs(strft_2_timestamp(self.add_time) - strft_2_timestamp(other.add_time))
        self_recv_bytes = json.loads(self.net_recv_bytes)
        other_recv_bytes = json.loads(other.net_recv_bytes)
        if self.host_name == other.host_name:
            for net_card in self_recv_bytes:
                net_card_recv_bytes = round(abs(float(other_recv_bytes[net_card]) - float(self_recv_bytes[net_card]))/(diff_add_time if diff_add_time else 1), 2)
                net_card_recv_map.update({net_card: net_card_recv_bytes})
        return net_card_recv_map


class SfoNodeStat5MinMethod(SfoNodeStat_5min, SfoNodeStatMethod):
    pass


class SfoNodeStatHourMethod(SfoNodeStat_hour, SfoNodeStatMethod):
    pass


class SfoNodeStatDayMethod(SfoNodeStat_day, SfoNodeStatMethod):
    pass


class SfoNodeStatHistoryMethod(SfoNodeStatHistory, SfoNodeStatMethod):
    pass


class SfoAccountStatsDMethod(SfoAccountStatsD):
    pass


class SfoContainerStatsDMethod(SfoContainerStatsD):
    pass


class SfoObjectStatsDMethod(SfoObjectStatsD):
    pass


class SfoProxyStatsDMethod(SfoProxyStatsD):

    @classmethod
    def query_the_last_proxy_stat_data(cls):
        return db.session.query(cls).order_by(cls.add_time.desc()).first()

    @classmethod
    def query_proxt_stat_st2et(cls, starttime, endtime):
        return db.session.query(cls).filter(and_(cls.add_time > starttime,
                                                 cls.add_time <= endtime)).order_by(cls.add_time).all()


class SfoProxyStatsD5MinMethod(SfoProxyStatsD_5min, SfoProxyStatsDMethod):
    pass


class SfoProxyStatsDHourMethod(SfoProxyStatsD_hour, SfoProxyStatsDMethod):
    pass


class SfoProxyStatsDDayMethod(SfoProxyStatsD_day, SfoProxyStatsDMethod):
    pass


class SfoStatsDMethod(SfoStatsD):
    pass


class SfoAccountManagerMethod(SfoAccountManager):

    @classmethod
    def query_systems(cls, cluster_name):
        return db.session.query(cls).filter(and_(cls.cluster_name == cluster_name, cls.account_stat == '1')).all()

    @staticmethod
    def apply_capacity_total(*sfo_account_managers):
        apply_cluster_capacity_total = 0
        for account in sfo_account_managers:
            apply_cluster_capacity = account.system_capacity
            apply_cluster_capacity_total += int(apply_cluster_capacity)
        return apply_cluster_capacity_total

    @classmethod
    def query_system_by_syscode(cls, project_name):
        return db.session.query(cls).filter(and_(cls.project_name == project_name, cls.account_stat == '1')).first()

    @classmethod
    def query_system_by_account(cls, account):
        return db.session.query(cls).filter(and_(cls.system_user == account, cls.account_stat == '1')).first()

    @classmethod
    def query_system_by_accountid(cls, accountid):
        return db.session.query(cls).filter(and_(cls.account_id == accountid, cls.account_stat == '1')).first()

    @classmethod
    def query_system_by_guid(cls, guid):
        return db.session.query(cls).filter(and_(cls.guid == guid, cls.account_stat == '1')).first()


class SfoCofigureMethod(SfoCofigure):

    @classmethod
    def query_by_guid(cls, guid):
        return db.session.query(cls).filter(cls.guid == guid).first()

    @classmethod
    def query_all_config(cls, page, query, limit):
        query = or_(cls.config_group == query, cls.config_key == query) if query else not None
        return SfoCofigure.query.filter(query).order_by(cls.config_group, cls.guid).paginate(page, limit)

    @classmethod
    def query_filter_by_group_key(cls, group, key):
        return db.session.query(cls).filter(cls.config_group == group, cls.config_key == key).first()

    @classmethod
    def query_value_from_con_group(cls, group):
        return db.session.query(cls).filter(cls.config_group == group).all()

    @classmethod
    def query_value_from_con_key(cls, key):
        return db.session.query(cls).filter(cls.config_key == key).first()

    @classmethod
    def update_passwd_md5(cls, file_path, cluster_name):
        sfo_passwd_md5_conf = cls.query_filter_by_group_key(cluster_name, 'swift_passwd_md5')
        if sfo_passwd_md5_conf:
            md5_file = sf_utils.excute_command('md5sum %s' % file_path)
            try:
                _passwd_md5 = md5_file.split(' ')
                if len(_passwd_md5) > 0:
                    sfo_passwd_md5_conf.config_value = _passwd_md5[0]
                    sfo_passwd_md5_conf.add_time = timestamp_format(time.time())
                    db.session.add(sfo_passwd_md5_conf)
                    db.session.commit()
            except Exception, error:
                print 'update passwd md5 fail %s' % str(error)

    @classmethod
    def update_swiftconf_md5(cls, file_path, cluster_name):
        sfo_conf_md5 = cls.query_filter_by_group_key(cluster_name, 'swift_conf_md5')
        if sfo_conf_md5:
            md5_file = sf_utils.excute_command('md5sum %s' % file_path)
            try:
                _conf_md5 = md5_file.split(' ')
                if len(_conf_md5) > 0:
                    sfo_conf_md5.config_value = _conf_md5[0]
                    db.session.add(sfo_conf_md5)
                    db.session.commit()
            except Exception, error:
                print 'update conf md5 get exception %s' % str(error)

    @classmethod
    def update_ring_md5(cls, file_path, cluster_name):
        if isinstance(file_path, (str, unicode)):
            split_file_path = file_path.split('/')
            if len(split_file_path) > 0:
                split_ring_name = split_file_path[-1]
                ring_name, ring_ext, gz_ext = split_ring_name.split('.')
                if ring_name:
                    sfo_ring_md5_conf = cls.query_filter_by_group_key(cluster_name, 'swift_%s_ring_md5' % ring_name)
                    if sfo_ring_md5_conf:
                        md5_file = sf_utils.excute_command('md5sum %s' % file_path)
                        try:
                            _ring_md5 = md5_file.split(' ')
                            if len(_ring_md5) > 0:
                                sfo_ring_md5_conf.config_value = _ring_md5[0]
                                db.session.add(sfo_ring_md5_conf)
                                db.session.commit()
                        except Exception, error:
                            print 'update ring md5 get exception %s' % str(error)


class SfoHostRingMethod(SfoHostRing):

    @classmethod
    def query_rings(cls, cluster_name):
        """
        查询最近的主机内环信息
        :return:  所有主机内环信息模型 或者 []
        """
        hosts = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
        last_hosts_list = db.session.query(func.max(cls.add_time))\
            .filter(cls.host_name.in_([host.node_host_name for host in hosts]))\
            .group_by(cls.host_name).all()
        return db.session.query(cls).filter(and_(cls.add_time.in_(host[0] for host in last_hosts_list))).all()

    @classmethod
    def query_last_collection_info(cls, host_name):
        return db.session.query(cls).filter(cls.host_name == host_name).order_by(cls.add_time.desc()).first()


class SfoAlarmLogMethod(SfoAlarmLog):

    @classmethod
    def create_or_update(cls, device, alarm_type, host, level, message, device_name='', result=0):
        sfo_al_log = db.session.query(cls).filter(cls.alarm_device == device).first()
        if not sfo_al_log:
            sfo_al_log = cls()
            sfo_al_log.guid = str(uuid.uuid1())
            sfo_al_log.alarm_device = device
            sfo_al_log.alarm_level = level
            sfo_al_log.hostname = host
            sfo_al_log.alarm_type = alarm_type
            sfo_al_log.alarm_message = message
            sfo_al_log.alarm_result = result
            sfo_al_log.device_name = device_name
            sfo_al_log.add_time = timestamp_format(time.time())
        else:
            if level != sfo_al_log.alarm_level or result != sfo_al_log.alarm_result:
                sfo_al_log.alarm_level = level
                sfo_al_log.alarm_message = message
                sfo_al_log.alarm_result = result
                sfo_al_log.update_time = timestamp_format(time.time())
        return sfo_al_log

    @classmethod
    def query_by_guid(cls, guid):
        return db.session.query(cls).filter(and_(cls.guid == guid,
                                                 cls.alarm_result == 0)).first()

    @classmethod
    def group_by_alarm_device(cls, page=None, limit=None, starttime='', endtime=''):
        and_filter_caluse = []
        if starttime:
            and_filter_caluse.append(cls.add_time >= starttime)
        if endtime:
            and_filter_caluse.append(cls.add_time <= endtime)
        return cls.query.filter(and_(*and_filter_caluse))\
            .group_by(cls.alarm_device).order_by(cls.add_time.desc(), cls.guid).paginate(page, limit)

    @classmethod
    def query_by_alarm_device(cls, alarm_device, starttime='', endtime=''):
        and_filter_caluse = [cls.alarm_device == alarm_device]
        if starttime:
            and_filter_caluse.append(cls.add_time >= starttime)
        if endtime:
            and_filter_caluse.append(cls.add_time <= endtime)
        history_alarms = db.session.query(cls).filter(and_(*and_filter_caluse)).order_by(cls.add_time.desc()).all()
        return history_alarms


class SfoClusterSrvsMethod(SfoClusterSrvs):

    @classmethod
    def create_srv(cls, service_name, host_name, is_rely_software, srv_stat='1'):
        sfo_srv = db.session.query(cls).filter(and_(cls.service_name == service_name,
                                                    cls.node_host_name == host_name)).first()
        if not sfo_srv:
            sfo_srv = cls()
            sfo_srv.guid = str(uuid.uuid1())
            sfo_srv.service_name = service_name
            sfo_srv.node_host_name = host_name
            sfo_srv.is_rely_software = is_rely_software
            sfo_srv.srv_stat = srv_stat
            sfo_srv.add_time = timestamp_format(time.time())
            return sfo_srv
        else:
            sfo_srv.srv_stat = srv_stat
            sfo_srv.add_time = timestamp_format(time.time())
            return sfo_srv

    @classmethod
    def query_srvlist_by_host_name(cls, node_host_name):
        return db.session.query(cls).filter(cls.node_host_name == node_host_name).all()

    @classmethod
    def query_srv_by_hostname_and_srvname(cls, host_name, srv_name):
        return db.session.query(cls).filter(and_(cls.node_host_name == host_name, cls.service_name == srv_name)).first()


class BeatHeartInfoMethod(BeatHeartInfo):

    @classmethod
    def lived_agent(cls):
        the_max_add_times = db.session.query(func.max(cls.add_time).label('mx_time'), cls.hostname)\
            .group_by(cls.hostname).subquery()
        agents = db.session.query(cls).join(the_max_add_times, and_(cls.add_time == the_max_add_times.c.mx_time,
                                                                    cls.hostname == the_max_add_times.c.hostname)).all()
        return agents

    @classmethod
    def lived_agent_filter_cluster2(cls, cluster_nodes, page=None, limit=None):
        the_max_add_times = db.session.query(func.max(cls.add_time).label('mx_time'), cls.hostname) \
            .group_by(cls.hostname).subquery()
        agents = cls.query.join(the_max_add_times, and_(cls.add_time == the_max_add_times.c.mx_time,
                                                        cls.hostname == the_max_add_times.c.hostname)) \
            .filter(cls.hostname.in_([node.node_host_name for node in cluster_nodes]))
        if page and limit:
            agents = agents.paginate(page, limit)
        else:
            agents = agents.all()
        return agents


class SfoClusterConfigureMethod(SfoClusterConfigure):

    @classmethod
    def create_cluster_config(cls, filename, group, key, value, remark=''):
        sfo_clu_con = cls()
        sfo_clu_con.guid = str(uuid.uuid1())
        sfo_clu_con.config_filename = filename
        sfo_clu_con.config_group = group
        sfo_clu_con.config_key = key
        sfo_clu_con.config_value = value
        sfo_clu_con.remark = remark
        sfo_clu_con.add_time = timestamp_format(time.time())
        return sfo_clu_con

    @classmethod
    def query_all_config(cls):
        return db.session.query(cls).all()

    @classmethod
    def query_group_by_filename(cls):
        return db.session.query(cls).group_by(cls.config_filename).all()

    @classmethod
    def query_by_filename(cls, filename):
        return db.session.query(cls).filter(cls.config_filename == filename).all()

    @classmethod
    def query_group_by_config_group(cls, filename):
        return db.session.query(cls).filter(cls.config_filename == filename).group_by(cls.config_group).all()


class SfoSwiftUserMethod(SfoSwiftUser):

    @classmethod
    def create_user(cls, cluster_name, systemc_user, account_id='', role_name='', ):
        swift_user = cls.query_user_by_unique_constraint(account_id, role_name, systemc_user)
        if not swift_user:
            swift_user = cls()
            swift_user.guid = str(uuid.uuid1())
            swift_user.cluster_name = cluster_name
            swift_user.system_user = systemc_user
            swift_user.account_id = account_id
            swift_user.role_name = role_name
            swift_user.add_time = timestamp_format(time.time())
            return swift_user

    @classmethod
    def query_user_by_guid(cls, guid):
        return db.session.query(cls).filter(cls.guid == guid).first()

    @classmethod
    def query_user_by_unique_constraint(cls, account_id, role_name, system_user):
        return db.session.query(cls).filter(and_(cls.account_id == account_id,
                                                 cls.role_name == role_name,
                                                 cls.system_user == system_user)).first()

    @classmethod
    def query_users_by_cluster_name(cls, cluster_name):
        return db.session.query(cls).filter(cls.cluster_name == cluster_name).all()

    @classmethod
    def query_passwd_exists_by_account_id_system_user(cls, account_id, system_user):
        return db.session.query(cls).filter(and_(cls.account_id == account_id,
                                                 cls.system_user == system_user,
                                                 cls.role_name != '')).first()

    @classmethod
    def query_user_by_system_user(cls, system_user):
        return db.session.query(cls).filter(cls.system_user == system_user).all()


class SfoSwiftRoleMethod(SfoSwiftRole):

    @classmethod
    def create_role(cls, role_name, role_meta, role_desc=''):
        swift_role = cls.query_role(role_name)
        if not swift_role:
            swift_role = cls()
            swift_role.guid = str(uuid.uuid1())
            swift_role.role_name = role_name
            swift_role.role_meta = role_meta
            swift_role.role_desc = role_desc
            swift_role.add_time = timestamp_format(time.time())
            return swift_role

    @classmethod
    def query_role(cls, role_name):
        return db.session.query(cls).filter(cls.role_name == role_name).first()

    @classmethod
    def query_roles(cls):
        return db.session.query(cls).all()

    @classmethod
    def query_role_by_guid(cls, guid):
        return db.session.query(cls).filter(cls.guid == guid).first()


class SfoClusterTpsMethod(SfoClusterTps):

    @classmethod
    def query_start2end_region_list_info(cls, cluster_name, start_time, end_time):
        return db.session.query(cls).filter(and_(cls.cluster_name == cluster_name,
                                                 cls.add_time >= start_time,
                                                 cls.add_time < end_time)).order_by(cls.add_time).all()