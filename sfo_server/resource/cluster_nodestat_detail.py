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
from copy import deepcopy
from flask import request
from sfo_server import access_logger
from flask_restful import Resource, marshal_with, fields
from sfo_server.models import (SfoNodeStatMethod,
                               SfoNodeStat5MinMethod,
                               SfoNodeStatHourMethod,
                               SfoNodeStatDayMethod)
from sfo_server.resource.common import (JsonDecodeListField,
                                        used_time,
                                        SplitField,
                                        EnvelopeField,
                                        timestamp_format,
                                        RecuDictField,
                                        is_less_than_nhours)
from sfo_server.decorate import login_required, permission_required


cluster_node_stat_resource_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data": EnvelopeField({
        "host_info": {"host_name": fields.String,
                      "host_runtime": fields.String,
                      "host_time": fields.String},
        "host_average_load_list": {"list": fields.List(SplitField(attribute='host_average_load'))},
        "host_login_users_list": {"list": fields.List(fields.String(attribute='host_login_users'))},
        "addtime_list": {"list": fields.List(fields.String(attribute='add_time'))},
        "thread_total_list": {"list": fields.List(fields.String(attribute='thread_total'))},
        "thread_running_list": {"list": fields.List(fields.String(attribute='thread_running'))},
        "thread_sleeping_list": {"list": fields.List(fields.String(attribute='thread_sleeping'))},
        "thread_stopedl_list": {"list": fields.List(fields.String(attribute='thread_stoped'))},
        "thread_zombie_list": {"list": fields.List(fields.String(attribute='thread_zombie'))},
        "cpu_us_list": {"list": fields.List(fields.String(attribute='cpu_us'))},
        "cpu_sy_list": {"list": fields.List(fields.String(attribute='cpu_sy'))},
        "cpu_ni_list": {"list": fields.List(fields.String(attribute='cpu_ni'))},
        "cpu_id_list": {"list": fields.List(fields.String(attribute='cpu_id'))},
        "cpu_wa_list": {"list": fields.List(fields.String(attribute='cpu_wa'))},
        "cpu_hi_list": {"list": fields.List(fields.String(attribute='cpu_hi'))},
        "cpu_si_list": {"list": fields.List(fields.String(attribute='cpu_si'))},
        "cpu_st_list": {"list": fields.List(fields.String(attribute='cpu_st'))},
        "cpu_core_used_list": {"list": fields.List(JsonDecodeListField(attribute='cpu_core_used'))},
        "cpu_core_frq_list": {"list": fields.List(fields.String(attribute='cpu_core_frq'))},
        "mem_total_list": {"list": fields.List(fields.String(attribute='mem_total'))},
        "mem_used_list": {"list": fields.List(fields.String(attribute='mem_used'))},
        "mem_free_list": {"list": fields.List(fields.String(attribute='mem_free'))},
        "swap_total_list": {"list": fields.List(fields.String(attribute='swap_total'))},
        "swap_used_list": {"list": fields.List(fields.String(attribute='swap_used'))},
        "swap_free_list": {"list": fields.List(fields.String(attribute='swap_free'))},
        "swap_cached_list": {"list": fields.List(fields.String(attribute='swap_cached'))},
        "net_used_list": {"map": RecuDictField()},
        "net": {

                    "net_send_packages": RecuDictField(),
                    "net_recv_packages": RecuDictField(),
                    "net_send_bytes": RecuDictField(),
                    "net_recv_bytes": RecuDictField(),
                    "net_in_err": RecuDictField(),
                    "net_out_err": RecuDictField(),
                    "net_in_drop": RecuDictField(),
                    "net_out_drop": RecuDictField(),
                }
    })
}


def get_cluster_nodestat_detail_logic(host_name, start_time, end_time):
    """
    GET 请求集群节点信息处理逻辑
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = ''
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    if is_less_than_nhours(start_time, end_time, 1):
        node_stat_detail = SfoNodeStatMethod.query_node_stat_list_by_hostname(host_name, start_time, end_time)
    elif is_less_than_nhours(start_time, end_time, 8):
        node_stat_detail = SfoNodeStat5MinMethod.query_node_stat_list_by_hostname(host_name, start_time, end_time)
    elif is_less_than_nhours(start_time, end_time, 24):
        node_stat_detail = SfoNodeStatHourMethod.query_node_stat_list_by_hostname(host_name, start_time, end_time)
    else:
        node_stat_detail = SfoNodeStatDayMethod.query_node_stat_list_by_hostname(host_name, start_time, end_time)
    net_map = {"net_send_bytes": {}, "net_recv_bytes": {}}
    for idx, node in enumerate(node_stat_detail):
        if idx == len(node_stat_detail)-1:
            continue
        else:
            node_send_bytes_map = node.diff_net_card_send_bytes(node_stat_detail[idx+1])
            node_recv_bytes_map = node.diff_net_card_recv_bytes(node_stat_detail[idx+1])
            for net_card in node_send_bytes_map:
                if net_map['net_send_bytes'].get(net_card) < 0:
                    net_map['net_send_bytes'].update({net_card: [node_send_bytes_map[net_card]]})
                    net_map['net_recv_bytes'].update({net_card: [node_recv_bytes_map[net_card]]})
                else:
                    net_map['net_send_bytes'][net_card].append(node_send_bytes_map[net_card])
                    net_map['net_recv_bytes'][net_card].append(node_recv_bytes_map[net_card])

    if node_stat_detail:
        status = 200
        message = 'OK'
        node_stat_detail_deepcopy = deepcopy(node_stat_detail)
        net_map_deepcopy = deepcopy(net_map)
        ins = SfoNodeStatMethod.query_last_node_stat(host_name)
        if ins:
            node_stat_ins = ins
        else:
            node_stat_ins = node_stat_detail_deepcopy[-1]
        node_stat_ins.list = node_stat_detail_deepcopy
        node_stat_ins.map = net_map_deepcopy
        data = node_stat_ins
    else:
        status = 404
        message = 'Not Found Record Cluster NodeStat By %s' % host_name
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


class ClusterNodeStatDetailAPI(Resource):

    """
    GET 获取一段时间内主机节点状态
    request: GET，POST, DELETE
    response :
        { 'status': 200/404 ,"data":data , "message": message}
    content-type : application/json
    """

    resource = (SfoNodeStatMethod,)
    # method_decorators = [access_log_decorate]

    @used_time
    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_node_stat_resource_fields)
    def get(self, host_name):
        start_time = request.args.get('starttime', '')
        end_time = request.args.get('endtime', '')
        try:
            start_time = timestamp_format(start_time) if start_time else timestamp_format(time.time() - 600)
            end_time = timestamp_format(end_time) if end_time else timestamp_format(time.time())
            resp, status = get_cluster_nodestat_detail_logic(host_name, start_time=start_time, end_time=end_time)
            return resp, status
        except ValueError, error:
            access_logger.error('access ClusterNodeStatDetailAPI get exception %s' % error)
            status = 400
            message = 'Invalid Parameter %s' % str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            access_logger.error('access ClusterNodeStatDetailAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}, status
