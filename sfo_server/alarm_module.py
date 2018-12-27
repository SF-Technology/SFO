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

from sfo_server.models import SfoClusterNodesMethod


def compare_pre_and_cur_log(pre_logs, cur_logs):
    """
    比对上一次发送的数据和当前数据要发送的数据是否有改变
    :param pre_logs:
    :param cur_logs:
    :return:
    """
    pre_guids = [plog.guid for plog in pre_logs]
    if len(pre_logs) == len(cur_logs):
        for log in cur_logs:
            if log.guid in pre_guids:
                idx = pre_guids.index(log.guid)
                if log.alarm_level == pre_logs[idx].alarm_level:
                    continue
                else:
                    return False
            else:
                return False
        else:
            return True


def category_alarm_level(alarm_list):
    """
    构建输出数据格式,根据报警等级划分,还要根据软硬件划分？
    :param alarm_list: 告警列表
    :return:
    """
    sum_alarm = len(alarm_list)
    alarm_level_dict = {}
    alarm_level_set = set(map(lambda x: x.alarm_level, alarm_list))
    nodes = SfoClusterNodesMethod.query.group_by(SfoClusterNodesMethod.node_host_name).all()
    for level in alarm_level_set:
        alarm_level_dict.setdefault(level, {"%s_total" % level: len(filter(lambda x: x.alarm_level == level, alarm_list)),
                                            "alarms": []})
    for alarm_log in alarm_list:
        level = alarm_log.alarm_level
        ip = ''
        cluster_name = ''
        for node in nodes:
            if alarm_log.hostname == node.node_host_name:
                cluster_name = node.cluster_name
                ip = node.node_inet_ip
        alarm_level_dict[level]["alarms"].append({"alarm_device": alarm_log.device_name,
                                                  "alarm_type": alarm_log.alarm_type,
                                                  "alarm_guid": alarm_log.guid,
                                                  "alarm_host": alarm_log.hostname,
                                                  "ip": ip,
                                                  "cluster_name": cluster_name,
                                                  "alarm_message": alarm_log.alarm_message,
                                                  "alarm_level": alarm_log.alarm_level,
                                                  "add_time": alarm_log.add_time})
    return sum_alarm, alarm_level_dict