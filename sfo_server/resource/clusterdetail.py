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
import numpy
import datetime
from flask import request
from sfo_server import access_logger
from flask_restful import Resource, marshal_with, fields
from sfo_server.models import SfoClusterInfoMethod, SfoClusterInfo,\
    SfoClusterNodesMethod, SfoNodeServiceMethod, SfoAccountManagerMethod, SfoHostInfoMethod, BeatHeartInfoMethod, SfoClusterMethod, db
from sfo_server.decorate import access_log_decorate,login_required,permission_required
from sfo_server.resource.common import (timestamp_format,
                                        strft_2_timestamp,
                                        RecuDictField,
                                        strft_2_timestamp)


def p95_ops(cluster_set):
    if cluster_set:
        ops_list = map(lambda x: float(x.uri_total), cluster_set)
        p95_value = numpy.percentile(ops_list, 95)
        return '%0.2f' % p95_value
    else:
        return 'The data was empty 24 hours ago.'


def p95_band_width(cluster_set):
    if cluster_set:
        band_width_list = map(lambda x: float(json.loads(x.band_width)['band_used']), cluster_set)
        p95_value = numpy.percentile(band_width_list, 95)
        return '%0.2f' % (p95_value / 8)
    else:
        return 'The data was empty 24 hours ago.'


def p95_band_width_rep(cluster_set):
    if cluster_set:
        band_width_rep_list = map(lambda x: float(json.loads(x.band_width)['band_rep_used']), cluster_set)
        p95_value = numpy.percentile(band_width_rep_list, 95)
        return '%0.2f' % (p95_value / 8)
    else:
        return 'The data was empty 24 hours ago.'


def account_used(x):
    if hasattr(x, "system_used"):
        try:
            used_json = json.loads(x.system_used)
            account_used = used_json.get('account-used', 0)
            return account_used
        except TypeError:
            return 0
    return 0


def Mb_translate_MB(cluster_info):
    _band_width = {}
    if cluster_info:
        band_width = json.loads(cluster_info.band_width)
        _band_width.update(band_width)
        Mb_band_width = band_width.get('band_total', 0)
        Mb_rep_band_width = band_width.get('band_rep_total', 0)
        Mb_band_width_used = band_width.get('band_used', 0)
        Mb_rep_band_width_used = band_width.get('band_rep_used', 0)
        MB_band_width = int(Mb_band_width) // 8
        MB_rep_band_width = int(Mb_rep_band_width) // 8
        MB_band_width_used = float(Mb_band_width_used) // 8
        MB_rep_band_width_used = float(Mb_rep_band_width_used) // 8
        _band_width.update({'band_total': MB_band_width,
                            "band_rep_total": MB_rep_band_width,
                            "band_used": MB_band_width_used,
                            "band_rep_used": MB_rep_band_width_used,
                            })
    return _band_width


# 输出字段的映射表
cluster_detail_resource_fields = {

    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({"cluster_physical": fields.Nested({
                                "proxy_num": RecuDictField(),
                                "storage_num": RecuDictField(),
                                "disk_num": fields.String,
                                "band_width": RecuDictField(attribute=lambda x: Mb_translate_MB(x)),
                                "capacity_total": RecuDictField(),
                            }),
                           "cluster_virtual": fields.Nested({
                               "account_num": fields.String,
                               "container_num": fields.String,
                               "object_num": fields.String
                            }),
                           "cluster_ops_24h_ago": fields.Nested({
                               "cluster_ops_p95": fields.String(
                                   attribute=lambda x: p95_ops(x.list if hasattr(x, 'list') else []))
                            }),
                           "band_width_24h_ago": fields.Nested({
                               "band_width_p95": fields.String(attribute=lambda x: p95_band_width(x.list if hasattr(x, 'list') else [])),
                               "band_width_rep_p95": fields.String(attribute=lambda x: p95_band_width_rep(x.list if hasattr(x, 'list') else [])),
                            }),
                           "abnormal": fields.Nested({
                                "proxy": fields.List(fields.String(attribute='host_name')),
                                "account": fields.List(fields.String(attribute='host_name')),
                                "container": fields.List(fields.String(attribute='host_name')),
                                "object": fields.List(fields.String(attribute='host_name')),
                            }),
                           "cluster_capacity_info": fields.Nested({
                                "apply_system_total": fields.Integer,
                                "apply_systems_info": fields.Nested({
                                    "system_code": fields.String,
                                    "account_id": fields.String,
                                    "system_capacity": fields.Integer,
                                    "account_used": fields.Integer(attribute=lambda x: account_used(x)),
                                })
                            }),
                           "cluster_proxy_total_ops": fields.Integer,
                           "cluster_node": fields.Nested({
                               "node_online": fields.Integer,
                               "node_outline": fields.Integer,
                               "node_total": fields.Integer,
                               "outline_nodes": fields.List(fields.String),
                           })
    })
}


def cluster_total_proxy_ops(cluster_name):
    """
    集群的预估iops值 与cpu core num 有关, 集群下Proxy节点的cpu核数* 单个(cpu核数能力)80 * 0.8
    单个能力 : 48核的cpu 预估ops是4000 ,单个由此计算
    公式 4000/48 * 0.8 * 集群proxy节点的总cpu核数
    :param cluster_name:
    :return:
    """
    sfo_proxy_nodes = []
    sfo_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    for node in sfo_nodes:
        try:
            node_role_js = json.loads(node.node_role)
            if isinstance(node_role_js, dict) and node_role_js.get('Proxy-Server') == 'YES':
                sfo_proxy_nodes.append(node)
        except ValueError:
            continue
    _estimate_proxy_ops_total = 0
    for node in sfo_proxy_nodes:
        sfo_node = SfoHostInfoMethod.query_host_info_by_host_name(node.node_host_name)
        if sfo_node:
            _estimate_proxy_ops_total += int(sfo_node.cpu_cores) * 80
    estimate_proxy_ops_total = _estimate_proxy_ops_total*0.8
    return estimate_proxy_ops_total


def get_cluster_detail_logic(cluster_name, start_time, end_time):
    """
    GET 请求集群信息列表处理逻辑
    :param start_time: str  字符串日期格式
    :param end_time: str  字符串日期格式
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """

    status = ''
    message = ''
    abnormal_dic = {"proxy": [], 'account': [], 'container': [], 'object': []}
    abnormal_node = {"node_online": 0, "node_outline": 0, "node_total": 0, "outline_nodes": []}
    cluster_capacity_info = {"apply_system_total": 0, "apply_systems_info": []}
    estimate_proxy_ops_total = cluster_total_proxy_ops(cluster_name)
    data = {"cluster_physical": "",
            "cluster_virtual": "",
            "cluster_ops_24h_ago": "",
            "band_width_24h_ago": "",
            "abnormal": abnormal_dic,
            "cluster_capacity_info": cluster_capacity_info,
            "cluster_proxy_total_ops": estimate_proxy_ops_total,
            "cluster_node": abnormal_node}
    resp = {"status": status, "data": data, "message": message}
    instances = SfoClusterInfoMethod.query_last_cluster_overview(cluster_name)
    yesterady_cluster_set = SfoClusterInfoMethod.query_start2end_region_list_info(cluster_name, start_time, end_time)
    cluster_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
    sfo_cluster_beatheart = BeatHeartInfoMethod.lived_agent_filter_cluster2(cluster_nodes)
    sfo_aco_man = SfoAccountManagerMethod.query_systems(cluster_name)
    if instances:
        status = 200
        message = 'OK'
        proxy_json = json.loads(instances.proxy_num)
        storage_json = json.loads(instances.storage_num)
        current_time = time.time()
        if len(cluster_nodes) >= len(sfo_cluster_beatheart):
            for node_beatheart in sfo_cluster_beatheart:
                if current_time - strft_2_timestamp(node_beatheart.add_time) > 180:
                    abnormal_node['outline_nodes'].append(node_beatheart.hostname)
            else:
                abnormal_node['node_total'] = len(cluster_nodes)
                abnormal_node['node_outline'] = len(abnormal_node['outline_nodes']) + (len(cluster_nodes) - len(sfo_cluster_beatheart))
                abnormal_node['node_online'] = len(sfo_cluster_beatheart) - len(abnormal_node['outline_nodes'])

            for node in cluster_nodes:
                try:
                    map(lambda x: x.hostname, sfo_cluster_beatheart).index(node.node_host_name)
                except (IndexError, ValueError):
                    abnormal_node['outline_nodes'].append(node.node_host_name)

        if proxy_json and storage_json:
            if int(proxy_json['proxy_online']) < int(proxy_json['proxy_total']) or \
                    int(storage_json['account_online']) < int(storage_json['account_num']) or \
                    int(storage_json['container_online']) < int(storage_json['container_num']) or \
                    int(storage_json['object_online']) < int(storage_json['object_num']):
                sfo_cluster_nodes = SfoClusterNodesMethod.query_host_list_by_cluster_name(cluster_name)
                sfo_node_srv = SfoNodeServiceMethod.query_node_srv_last_info()
                sfo_cluster_node_srv = filter(lambda x: x.host_name in [node.node_host_name for node in sfo_cluster_nodes],
                                              sfo_node_srv)
                if int(proxy_json['proxy_online']) < int(proxy_json['proxy_total']):
                    sfo_proxy_nodes = []
                    for node in sfo_cluster_nodes:
                        try:
                            node_role_js = json.loads(node.node_role)
                            if isinstance(node_role_js, dict) and node_role_js.get('Proxy-Server') == 'YES':
                                sfo_proxy_nodes.append(node)
                        except ValueError:
                            continue
                    sfo_proxy_node_srv = filter(lambda x: x.host_name in [node.node_host_name for node in sfo_proxy_nodes], sfo_cluster_node_srv)
                    for node_srv in sfo_proxy_node_srv:
                        if current_time - strft_2_timestamp(node_srv.add_time) < 60 and (node_srv.srv_proxy != 'running' or node_srv.srv_proxy == 'stopped'):
                            abnormal_dic['proxy'].append(node_srv)
                if int(storage_json['account_online']) < int(storage_json['account_num']):
                    sfo_acc_nodes = []
                    for node in sfo_cluster_nodes:
                        try:
                            node_role_js = json.loads(node.node_role)
                            if isinstance(node_role_js, dict) and node_role_js.get('Account-Server') == 'YES':
                                sfo_acc_nodes.append(node)
                        except ValueError:
                            continue
                    sfo_acc_node_srv = filter(lambda x: x.host_name in [node.node_host_name for node in sfo_acc_nodes], sfo_cluster_node_srv)
                    for node_srv in sfo_acc_node_srv:
                        if current_time - strft_2_timestamp(node_srv.add_time) < 60 and (node_srv.srv_account != 'running' or node_srv.srv_account == 'stopped'):
                            abnormal_dic['account'].append(node_srv)
                if int(storage_json['container_online']) < int(storage_json['container_num']):
                    sfo_con_nodes = []
                    for node in sfo_cluster_nodes:
                        try:
                            node_role_js = json.loads(node.node_role)
                            if isinstance(node_role_js, dict) and node_role_js.get('Container-Server') == 'YES':
                                sfo_con_nodes.append(node)
                        except ValueError:
                            continue
                    sfo_con_node_srv = filter(lambda x: x.host_name in [node.node_host_name for node in sfo_con_nodes], sfo_cluster_node_srv)
                    for node_srv in sfo_con_node_srv:
                        if current_time - strft_2_timestamp(node_srv.add_time) < 60 and (node_srv.srv_container != 'running' or node_srv.srv_container == 'stopped'):
                            abnormal_dic['container'].append(node_srv)
                if int(storage_json['object_online']) < int(storage_json['object_num']):
                    sfo_obj_nodes = []
                    for node in sfo_cluster_nodes:
                        try:
                            node_role_js = json.loads(node.node_role)
                            if isinstance(node_role_js, dict) and node_role_js.get('Object-Server') == 'YES':
                                sfo_obj_nodes.append(node)
                        except ValueError:
                            continue
                    sfo_obj_node_srv = filter(lambda x: x.host_name in [node.node_host_name for node in sfo_obj_nodes], sfo_cluster_node_srv)
                    for node_srv in sfo_obj_node_srv:
                        if current_time - strft_2_timestamp(node_srv.add_time) < 60 and (node_srv.srv_object != 'running' or node_srv.srv_object == 'stopped'):
                            abnormal_dic['object'].append(node_srv)
        if yesterady_cluster_set:
            instances.list = yesterady_cluster_set
        if sfo_aco_man:
            cluster_capacity_info['apply_system_total'] = len(sfo_aco_man)
            cluster_capacity_info['apply_systems_info'] = sfo_aco_man
        data.update({"cluster_physical": instances,
                     "cluster_virtual": instances,
                     "cluster_ops_24h_ago": instances,
                     "band_width_24h_ago": instances})
    else:
        status = 404
        message = 'Not Found Record By %s' % cluster_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def update_cluster_info_logic(cluster_name, cluster_json):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_clu = SfoClusterMethod.query_cluster_by_cluster_name(cluster_name)
    if sfo_clu:
        alias = cluster_json.get('alias')
        desc = cluster_json.get('desc')
        extend = json.dumps({"alias": alias, "description": desc})
        sfo_clu.extend = extend
        db.session.add(sfo_clu)
        db.session.commit()
        status = 200
        message = 'OK'
    else:
        status = 404
        message = "%s cluster doesn't exists" % cluster_name
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterDetailAPI(Resource):

    """
    用于获取集群采集数据
    request: GET
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    resource = (SfoClusterInfo,)

    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_detail_resource_fields)
    def get(self, cluster_name):
        try:
            _time = strft_2_timestamp(datetime.datetime.now().date().strftime('%Y-%m-%d %H:%M:%S'))
            start_time = timestamp_format(_time - 86400)
            end_time = timestamp_format(_time)
            resp, status = get_cluster_detail_logic(cluster_name, start_time, end_time)
            return resp, status
        except ValueError, error:
            access_logger.error('GET ClusterDetailAPI get exception %s' % error)
            import sys, traceback
            print traceback.print_exc()
            status = 400
            message = "Invalid Parameters %s" % str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('GET ClusterDetailAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def put(self, cluster_name):
        try:
            cluster_json = request.json
            resp, status = update_cluster_info_logic(cluster_name, cluster_json)
            return resp, status
        except ValueError, error:
            access_logger.error('PUT ClusterDetailAPI get exception %s' % error)
            status = 400
            message = "Invalid Parameters %s" % str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('GET ClusterDetailAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status