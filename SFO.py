#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import json
from multiprocessing import RLock
from sfo_common.config_parser import Config
from flask import Flask, request, render_template, Response, abort
# from flask_cors import CORS
from flask_restful import Api
from sfo_common import db
from sfo_utils.apscheduler_utils import scheduler
from sfo_server.models import SfoServerResource, SfoServerPermission, SfoServerRole, SfoClusterMethod
from sfo_server.resource.userlogin import UserLoginAPI
from sfo_server.resource.userlogout import UserLogoutAPI
from sfo_server.resource.cluster_topological_graph import TopologicalGraphAPI

#集群监控
from sfo_server.resource.clusterlist import ClusterListAPI
from sfo_server.resource.clusterdisk import ClusterDiskAPI
from sfo_server.resource.clusterdetail import ClusterDetailAPI
from sfo_server.resource.cluster_req_count import ClusterRequestCountApi
from sfo_server.resource.cluster_hostlist import ClusterHostListAPI
from sfo_server.resource.cluster_overview import (ClusterOverViewAPI,
                                                  ClusterCpuFrequencyAPI,
                                                  ClusterMemoryAPI,
                                                  ClusterStorNetUsedAPI,
                                                  ClusterProNetUsedAPI,
                                                  ClusterBandWidthAPI,
                                                  ClusterDiskPerformAPI,
                                                  ClusterNodePerformAPI)
from sfo_server.resource.cluster_disk_io import ClusterDiskIOAPI
from sfo_server.resource.cluster_hostinfo_detail import ClusterHostInfoDetailAPI
from sfo_server.resource.cluster_nodestat_detail import ClusterNodeStatDetailAPI
from sfo_server.resource.cluster_node_srv_detail import ClusterNodeSrvDetailAPI
from sfo_server.resource.cluster_node_perform_detail import ClusterNodePerformDetailAPI
from sfo_server.resource.cluster_parition import ClusterPartitionAPI
from sfo_server.resource.cluster_async_num import ClusterAysncPendingAPI
from sfo_server.resource.cluster_tps_info import ClusterTPSInfoAPI
from sfo_server.resource.cluster_swift_role import ClusterSwiftRoleListAPI, ClusterSwiftRoleInfoAPI
from sfo_server.resource.cluster_swift_user import ClusterSwiftUserListAPI, ClusterSwiftUserInfoAPI

#集群管理
from sfo_server.resource.cluster_node_manager import ClusterNodeManagerApi
from sfo_server.resource.cluster_node_manager_signle import ClusterNodeManagerSignleApi
from sfo_server.resource.cluster_srv_manager import ClusterSrvManagerApi
from sfo_server.resource.cluster_policy_manager import ClusterPolicyManagerApi
from sfo_server.resource.agent_manager import ClusterAgentManagerAPI
from sfo_server.resource.cluster_manager.disk_manager.disk_manager import ClusterDiskManagerApi
from sfo_server.resource.cluster_ring_manager import ClusterRingManagerApi
from sfo_server.resource.cluster_ring_manager import ClusterRingManagerDetailApi
from sfo_server.resource.cluster_manager.user import UserAPI
from sfo_server.resource.cluster_manager.userlist import UserListAPI
from sfo_server.resource.cluster_manager.permissionlist import SfoServerPermissionListAPI
from sfo_server.resource.cluster_manager.role import SfoServerRoleAPI
from sfo_server.resource.cluster_manager.rolelist import SfoServerRoleListAPI
from sfo_server.resource.cluster_manager.config_manager import SfoServerConfigAPI
from sfo_server.resource.system_access import SystemAccessApi
from sfo_server.resource.system_access import SystemManagerApi
from sfo_server.resource.cluster_accounts import ClusterAccountListAPI
from sfo_server.resource.cluster_accounts import ClusterAccountInfoAPI
from sfo_server.resource.cluster_manager.node_manager.swift_config import SwiftConfigAPI
from sfo_server.resource.cluster_manager.node_manager.service_task import ServiceTaskAPI
from sfo_server.resource.cluster_manager.node_manager.service_task_detail import ServiceTaskDetailAPI
from sfo_server.resource.cluster_manager.manager_log import ManagerLogDetailAPI
from sfo_server.resource.cluster_alarm_log import ClusterAlarmLogAPI

#集群报表
from sfo_server.resource.cluster_report import ClusterReportApi
#容量平台


app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)),'static'),static_url_path='')
app.config['SECRET_KEY'] = 'youneverguesssecretpassword'
# app.config['PERMANENT_SESSION_LIFETIME'] = 7200  #session 过期时间两个小时
api = Api(app)
#启动定时任务调度器
scheduler.start()
scheduler.wake_up()

thread = None
pre_alarm_logs = None
processlock = RLock()
config = Config()

#用户信息登录页面API
api.add_resource(UserLoginAPI, '/api/userlogin/', endpoint='user_login')
api.add_resource(UserLogoutAPI, '/api/userlogout/', endpoint='user_logout')

#首页
api.add_resource(ClusterListAPI, '/api/cluster/', endpoint='cluster_list')
api.add_resource(ClusterDetailAPI, '/api/cluster/<string:cluster_name>/', endpoint='cluster_detail')
api.add_resource(ClusterRequestCountApi, '/api/cluster/requeststat/<string:cluster_name>/', endpoint='request_stat')

#集群监控 -- >总览页
api.add_resource(ClusterOverViewAPI, '/api/cluster/<string:cluster_name>/overview/', endpoint='cluster_overview')
api.add_resource(ClusterCpuFrequencyAPI, '/api/cluster/<string:cluster_name>/overview/cpu/', endpoint='cluster_overview_cpu')
api.add_resource(ClusterMemoryAPI, '/api/cluster/<string:cluster_name>/overview/mem/', endpoint='cluster_overview_mem')
api.add_resource(ClusterStorNetUsedAPI, '/api/cluster/<string:cluster_name>/overview/storage/', endpoint='cluster_overview_storage_net')
api.add_resource(ClusterProNetUsedAPI, '/api/cluster/<string:cluster_name>/overview/proxy/', endpoint='cluster_overview_proxy_net')
api.add_resource(ClusterDiskIOAPI, '/api/cluster/<string:cluster_name>/diskio/', endpoint='cluster_disk_io')
api.add_resource(ClusterPartitionAPI, '/api/cluster/<string:cluster_name>/partition/', endpoint='cluster_partition_info')
api.add_resource(ClusterBandWidthAPI, '/api/cluster/<string:cluster_name>/bandwidth/', endpoint='cluster_bandwidth')
api.add_resource(ClusterDiskPerformAPI, '/api/cluster/<string:cluster_name>/diskper/', endpoint='cluster_disk_per')
api.add_resource(ClusterNodePerformAPI, '/api/cluster/<string:cluster_name>/node/', endpoint='cluster_node_per')
api.add_resource(ClusterAysncPendingAPI, '/api/cluster/<string:cluster_name>/async/', endpoint='cluster_async')
api.add_resource(ClusterTPSInfoAPI, '/api/cluster/<string:cluster_name>/tps/', endpoint='cluster_tps')

#集群监控 -- >节点页
api.add_resource(ClusterHostListAPI, '/api/cluster/<string:cluster_name>/hostlist/', endpoint='cluster_hostlist')
api.add_resource(ClusterHostInfoDetailAPI, '/api/cluster/hostinfo/<string:host_name>/', endpoint='cluster_hostinfo_detail')
api.add_resource(ClusterNodeStatDetailAPI, '/api/cluster/nodestat/<string:host_name>/', endpoint='cluster_nodestat_detail')
api.add_resource(ClusterNodeSrvDetailAPI, '/api/cluster/nodesrv/<string:host_name>/', endpoint='cluster_nodesrv_detail')
api.add_resource(ClusterNodePerformDetailAPI, '/api/cluster/nodeperform/<string:host_name>/', endpoint='cluster_nodeperform_detail')
api.add_resource(ClusterDiskAPI, '/api/cluster/disk/<string:host_name>/', endpoint='cluster_disk_detail')

#集群管理 --- >节点列表
api.add_resource(ClusterNodeManagerApi, '/api/clusternodes/', endpoint='node_list')
api.add_resource(ClusterSrvManagerApi, '/api/clustersrvs/<string:cluster_name>/', endpoint='srv_list')
api.add_resource(ClusterNodeManagerSignleApi, '/api/clusternodes/<string:guid>/', endpoint='node_manager')

#节点管理 --- >
api.add_resource(SwiftConfigAPI, '/api/swift/config/', endpoint='swift_config')
api.add_resource(ServiceTaskDetailAPI, '/api/tasks/logs/', endpoint='service_task_detail')
api.add_resource(ServiceTaskAPI, '/api/tasks/', endpoint='service_tasks')

#磁盘管理 --- >
api.add_resource(ClusterDiskManagerApi, '/api/clusterdisks/<string:cluster_name>/', endpoint='disk_list')

#环管理 --- >
api.add_resource(ClusterRingManagerApi, '/api/clusterrings/<string:cluster_name>/', endpoint='ring_list')
api.add_resource(ClusterRingManagerDetailApi, '/api/clusterdetail/<string:cluster_name>/', endpoint='ring_info')

#存储策略管理 --- >
api.add_resource(ClusterPolicyManagerApi, '/api/clusterpolicys/<string:cluster_name>/', endpoint='policy_list')

#agent管理 --- >
api.add_resource(ClusterAgentManagerAPI, '/api/clusteragents/<string:cluster_name>/', endpoint='agent_list')

#系统管理 --- > 用户管理
api.add_resource(UserAPI, '/api/user/<string:user_account>/', endpoint='user_manager')
api.add_resource(UserListAPI, '/api/userlist/', endpoint='userlist_manager')
api.add_resource(SfoServerRoleAPI, '/api/role/<string:role_name>/', endpoint='role_manager')
api.add_resource(SfoServerRoleListAPI, '/api/rolelist/', endpoint='rolelist_manager')
api.add_resource(SfoServerPermissionListAPI, '/api/permissionlist/', endpoint='permissionlist_manager')
api.add_resource(ClusterAccountListAPI, '/api/accounts/', endpoint='accounts_manager')
api.add_resource(ClusterAccountInfoAPI, '/api/account/', endpoint='account_detail_manager')
api.add_resource(ClusterSwiftUserListAPI, '/api/swift/users/<string:cluster_name>/', endpoint='users_manager')
api.add_resource(ClusterSwiftUserInfoAPI, '/api/swift/user/<string:guid>/', endpoint='user_detail_manager')
api.add_resource(ClusterSwiftRoleListAPI, '/api/swift/roles/', endpoint='roles_manager')
api.add_resource(ClusterSwiftRoleInfoAPI, '/api/swift/role/<string:guid>/', endpoint='role_detail_manager')

#集群管理 --- > 通用配置
api.add_resource(SfoServerConfigAPI, '/api/configlist/', endpoint='config_manager')

#集群管理 --- > 警告信息
api.add_resource(ManagerLogDetailAPI, '/api/managerlog/<string:taskid>/', endpoint='manager_log')
api.add_resource(ClusterAlarmLogAPI, '/api/alarmlog/', endpoint='alarm_logs')
api.add_resource(ClusterAlarmLogAPI, '/api/alarmlog/<string:guid>/', endpoint='alarm_log')


#集群管理 -- >
api.add_resource(SystemAccessApi, '/api/systemaccess/<string:project_name>/', endpoint='system_access')
api.add_resource(SystemManagerApi, '/api/systemmanager/<string:project_name>/', endpoint='system_manager')

#集群报表
api.add_resource(ClusterReportApi, '/api/report/daily/', endpoint='daily')

#媒体介质管理接口
api.add_resource(TopologicalGraphAPI, '/api/topological/graph/<string:cluster_name>/', endpoint='topological_graph')

def init_permission_and_resource(tables):
    for table in tables:
        exists_table = SfoServerResource.query_all_resource()
        exists_table = [table_name[0] for table_name in exists_table]
        if table.name not in exists_table:
            resource = SfoServerResource()
            permission = SfoServerPermission()
            permission_list = permission.create_default_permission(table.name)
            resource = resource.create_default_resource(table.name, permission_list)
            db.session.add(resource)
    db.session.commit()


def create_default_role_permission():

    roles = SfoServerRole.create_default_role_permission()
    if roles:
        for role in roles:
            db.session.add(role)
        db.session.commit()

@app.before_request
def interceptor():
    com = re.compile(r"<[^>]+?style=[\w]+?:expression\(|\b(alert|confirm|prompt)\b|^\+/v(8|9)|<[^>]*?=[^>]*?&#[^>]*?>|\b(and|or)\b.{1,6}?(=|>|<|\bin\b|\blike\b)|/\*.+?\*/|<\s*script\b|<\s*img\b|\bEXEC\b|UNION.+?SELECT|UPDATE.+?SET|INSERT\s+INTO.+?VALUES|(SELECT|DELETE).+?FROM|(CREATE|ALTER|DROP|TRUNCATE)\s+(TABLE|DATABASE)")
    result = com.findall(request.path)
    if result:
        abort(400)
    if request.method != 'GET' and request.method != 'OPTIONS':
        params = request.json
        if params:
            for param, val in params.items():
                if isinstance(val, (str, unicode)):
                    val_result = com.findall(val)
                    param_result = com.findall(param)
                    if val_result or param_result:
                        abort(400)
    else:
        params = request.args
        if params:
            for param, val in params.items():
                if isinstance(val, (str, unicode)):
                    val_result = com.findall(val)
                    param_result = com.findall(param)
                    if val_result or param_result:
                        abort(400)

@app.before_first_request
def init_sfo_server():
    """
    初始化相关操作
        权限操作表和资源表
        默认角色和对应权限
    :return:
    """
    with processlock:
        tables = db.get_tables_for_bind()
        try:
            init_permission_and_resource(tables)
            create_default_role_permission()
        except Exception, err:
            print err
        finally:
            db.session.remove()


@app.route('/api/topological/graph/<string:cluster_name>/', methods=['GET'])
def topological(cluster_name):
    try:
        sfo_clu = SfoClusterMethod.query_cluster_by_cluster_name(cluster_name=cluster_name)
        if sfo_clu:
            extend_json = sfo_clu.extend
            extend = json.loads(extend_json)
            if extend.get('topologic'):
                topological_graph_path = extend['topologic']
                with open(topological_graph_path, 'rb') as fp:
                    data = fp.read()
                resp = Response(data, 200, content_type='image/png')
                return resp, 200
            else:
                resp_json = {"status": 404, "message": "No Topologic Graph"}
                resp = Response(json.dumps(resp_json), 404, content_type='application/json')
                return resp, 404
        else:
            resp_json = {"status": 404, "message": "Not Found Cluster"}
            resp = Response(json.dumps(resp_json), 404, content_type='application/json')
            return resp, 404
    except Exception, error:
        resp_json = {"status": 500, "message": str(error)}
        return Response(json.dumps(resp_json), 500, content_type='application/json'), 500


@app.teardown_request
def clean_session(exception=None):
    """
    确保sql链接在每次都被断开
    :param exception:
    :return:
    """
    try:
        db.session.close()
        db.session.remove()
    except Exception, error:
        print error


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception, error:
        pass