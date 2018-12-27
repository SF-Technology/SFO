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
from flask import request
from sfo_server import access_logger
from flask_restful import Resource, marshal_with, fields
from sfo_server.models import SfoAlarmLogMethod, SfoClusterNodesMethod, db
from sfo_server.resource.common import timestamp_format
from sfo_server.decorate import login_required, permission_required

# 输出字段的映射表
alarm_log_resource_fields = {

    "status": fields.Integer,
    "message": fields.String,
    "data": fields.Nested({
        "alarm_total": fields.Integer,
        "alarms": fields.List(fields.Nested({
            "alarm": fields.Nested({
                "alarm_device": fields.String,
                "alarm_type": fields.String,
                "hostname": fields.String,
                "device_name": fields.String,
                "alarm_message": fields.String,
                "alarm_result": fields.String,
                "alarm_level": fields.String,
                "add_time": fields.String,
            }),
            "total": fields.Integer,
            "ip": fields.String,
            "cluster_name": fields.String,
            "critical_total": fields.Integer,
            "warning_total": fields.Integer,
        }))
    })
}


def get_alarm_historys_logic(starttime, endtime, page, limit):
    """
    GET 请求历史告警记录信息
    :return: resp, status
              resp: json格式的响应数据
              status: 响应码
    """
    data = {'alarm_total': 0, "alarms": []}
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    alarm_set = SfoAlarmLogMethod.group_by_alarm_device(page=int(page),
                                                        limit=int(limit),
                                                        starttime=starttime,
                                                        endtime=endtime)
    if alarm_set:
        data['alarm_total'] = alarm_set.total
        for alarm in alarm_set.items:
            sfo_alarm_logs = SfoAlarmLogMethod.query_by_alarm_device(alarm.alarm_device, starttime, endtime)
            if len(sfo_alarm_logs) > 0:
                critical_len = filter(lambda x: x.alarm_level == 'critical', sfo_alarm_logs)
                warn_len = filter(lambda x: x.alarm_level == 'warning', sfo_alarm_logs)
                sfo_cluster_node = SfoClusterNodesMethod.query_host_by_host_name(alarm.hostname)
                alarm_info = {"alarm": sfo_alarm_logs[0],
                              "total": len(sfo_alarm_logs),
                              "warning_total": len(warn_len),
                              "critical_total": len(critical_len)}
                if sfo_cluster_node and sfo_cluster_node.cluster_name:
                    alarm_info.update({"cluster_name": sfo_cluster_node.cluster_name})
                    alarm_info.update({"ip": sfo_cluster_node.node_inet_ip})
                data['alarms'].append(alarm_info)
        status = 200
        message = 'OK'
    else:
        status = 404
        message = 'Not Found Record'
    resp.update({"status": status, "data": data, "message": message})
    return resp, status


def update_alarm_log_info(guid):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_swift_alarm_log = SfoAlarmLogMethod.query_by_guid(guid)
    if sfo_swift_alarm_log:
        sfo_swift_alarm_log.alarm_result = '1'
        db.session.add(sfo_swift_alarm_log)
        db.session.commit()
        status = 201
        message = 'Update OK'
    else:
        status = 404
        message = 'Not Found Record by %s'%guid
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterAlarmLogAPI(Resource):

    resource = (SfoAlarmLogMethod, )

    @login_required
    @permission_required(*resource)
    @marshal_with(alarm_log_resource_fields)
    def get(self, guid=None):
        try:
            start_time = request.args.get('starttime', '')
            end_time = request.args.get('endtime', '')
            page = request.args.get('page', 1)
            limit = request.args.get('limit', 10)
            if start_time:
                start_time = timestamp_format(start_time, '%Y-%m-%d %H:%M:%S')
            if end_time:
                end_time = timestamp_format(end_time, '%Y-%m-%d %H:%M:%S')
            else:
                end_time = timestamp_format(time.time(), '%Y-%m-%d %H:%M:%S')
            resp, status = get_alarm_historys_logic(start_time, end_time, page, limit)
            return resp, status
        except Exception, error:
            access_logger.error('Get ClusterAlarmLogAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % (str(error))
            return {'status': status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def put(self, guid):
        try:
            resp = update_alarm_log_info(guid)
            return resp
        except ValueError, error:
            access_logger.error('put ClusterAlarmLogAPI get exception %s' % error)
            status = 400
            message = 'Invaild Parameters %s' % str(error)
            return {'status': status, "message": message}
        except Exception, error:
            access_logger.error('put ClusterAlarmLogAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % str(error)
            return {'status': status, "message": message}

