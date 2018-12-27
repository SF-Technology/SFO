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
import re
import time
import datetime
from flask_restful import fields
from collections import OrderedDict

SUPER_ADMIN_ACCOUNT = 'admin'
SUPER_ADMIN_PASSWORD = 'admin'
SUPER_ADMIN_NAME = 'superadmin'
SUPER_ADMIN_DISPLAY_NAME = '超级管理员'


def is_super_admin(username, password):
    if username == SUPER_ADMIN_ACCOUNT and password == SUPER_ADMIN_PASSWORD:
        return True
    return False


def strft_2_timestamp(strft, format_str=''):
    """
    日期字符串转换成时间戳
    :param strft: str 日期字符串
    :param format_str: str 默认('%Y-%m-%d %H:%M:%S') 格式化的格式
    :return: str timestamp
    """
    import time
    format_str = format_str if format_str else '%Y-%m-%d %H:%M:%S'
    time_array = time.strptime(strft, format_str)
    timestamp = time.mktime(time_array)
    return timestamp



def is_more_than_24hours(st, et):
    """
    判断时间是否超过24个小时
    :param st:  开始时间  日期字符串
    :param et:  结束时间  日期字符串
    :return:  bool   True  or False
    """
    st = int(strft_2_timestamp(st))
    et = int(strft_2_timestamp(et))
    return abs(st - et)//3600 >= 24


def is_less_than_nhours(st, et, n):
    """
    判断时间是否低于n个小时
    :param st:  开始时间  日期字符串
    :param et:  开始时间  日期字符串
    :param n:  int  单位 小时
    :return:  bool   True  or False
    """
    st = int(strft_2_timestamp(st))
    et = int(strft_2_timestamp(et))
    return abs(st - et)//3600 <= n


def timestamp_format(timestamp, format_str=''):
    """
    时间戳转换成日期字符串
    :param timestamp:  str 字符串类型的时间戳
    :param format_str: str 默认('%Y-%m-%d %H:%M:%S') 格式化的格式
    :return:  str 日期字符串
    """
    try:
        format_str = format_str if format_str else '%Y-%m-%d %H:%M:%S'
        timestamp = int(timestamp)
        time_array = time.localtime(timestamp)
        strf = time.strftime(format_str, time_array)
        return strf
    except (ValueError, OverflowError):
        raise ValueError('Invalid Parameters')


def timedelta_for_str(strft, timedelta, format_str=''):
    format_str = format_str if format_str else '%Y-%m-%d %H:%M:%S'
    datetime_ = (datetime.datetime.strptime(strft, format_str) - datetime.timedelta(seconds=timedelta))\
        .strftime(format_str)
    return datetime_


def proxy_server_stat(text):
    hostname_httpmethod_map = {}
    req_timing = json.loads(text)
    for key, values in req_timing.items():
        rec = re.compile(r'proxy_server_([\w\d]+)\.[a-z-.\dA-Z]+?([A-Z]{3,10})\.\d{3}.+')
        result = re.search(rec, key)
        if result:
            hostname, httpmethod = result.groups()
            count = values['count_ps']
            try:
                count = float(count)
            except Exception:
                count = 0.0
            hostname_httpmethod_map.setdefault(hostname, {})
            if not hostname_httpmethod_map[hostname].get(httpmethod):
                hostname_httpmethod_map[hostname].update({httpmethod: count})
            else:
                hostname_httpmethod_map[hostname][httpmethod] += count
    return hostname_httpmethod_map


def sum_times_group_by_httpmethod(x, y):
    keys = []
    diff_set = set(y.keys()) ^ set(x.keys())
    cross_set = set(y.keys()) & set(x.keys())
    keys.extend(diff_set)
    keys.extend(cross_set)
    for key in diff_set:
        if key in x.keys():
            x.update({key: x[key]})
        elif key in y.keys():
            x.update({key: y[key]})
    for key in cross_set:
        x[key] = x[key] + y[key]
    return x


class HostGroup(object):

    def __init__(self, region):
        self.region = region
        self.group_list = []
        self.next_host_group = ''

    def used_total(self):
        cluster_core_frq_sum = 0
        group_list = self.group_by_host_name()
        for host_list in group_list.values():
            max_host = max(host_list, key=lambda x: x.add_time)
            cpu_core_used = json.loads(max_host.cpu_core_used)
            total_cpu_core_used = sum(cpu_core_used)
            cluster_core_frq_sum += total_cpu_core_used
        return cluster_core_frq_sum

    def group_by_host_name(self):
        host_group = {}
        for host in self.group_list:
            host_name = host.host_name
            if host_name not in host_group.keys():
                host_group.setdefault(host_name, [host])
            else:
                host_group[host_name].append(host)
        return host_group

    def group_by_disk_uuid(self):
        disk_group = {}
        for disk in self.group_list:
            disk_uuid = disk.disk_uuid
            if disk_uuid not in disk_group.keys():
                disk_group.setdefault(disk_uuid, [disk])
            else:
                disk_group[disk_uuid].append(disk)
        return disk_group

    def next_group(self):
        group = self.group_by_disk_uuid()
        next_group = self.next_host_group.group_by_disk_uuid()
        for key in group.keys():
            group[key].extend(next_group[key])
        return group

    def cluster_cpu_rate_list(self, host_cpu_total):
        cpu_core_frq_sum = self.used_total()
        cpu_frequency_val = (cpu_core_frq_sum / host_cpu_total) * 100 if host_cpu_total else 1
        cpu_frequency_val = '%0.2f' % cpu_frequency_val
        return cpu_frequency_val

    def server_net_used(self):
        group_list = self.group_by_host_name()
        cluster_net_total_send = 0
        cluster_net_total_recv = 0
        for host_list in group_list.values():
            net_diff_total_send, net_diff_total_recv = 0.0, 0.0
            for idx, host in enumerate(host_list):
                if idx == len(host_list)-1:
                    continue
                pre_host_send = json.loads(host_list[idx].net_send_bytes)
                pre_host_recv = json.loads(host_list[idx].net_recv_bytes)
                next_host_send = json.loads(host_list[idx+1].net_send_bytes)
                next_host_recv = json.loads(host_list[idx+1].net_recv_bytes)
                pre_send_total = self.net_card_used_total(pre_host_send)
                pre_recv_total = self.net_card_used_total(pre_host_recv)
                next_send_total = self.net_card_used_total(next_host_send)
                next_recv_total = self.net_card_used_total(next_host_recv)
                net_send_diff = next_send_total - pre_send_total
                net_recv_diff = next_recv_total - pre_recv_total
                net_diff_total_send += net_send_diff
                net_diff_total_recv += net_recv_diff
            else:
                try:
                    _net_diff_total_send = net_diff_total_send/((len(host_list)-1) if (len(host_list)-1) > 0 else 1)
                    _net_diff_total_recv = net_diff_total_recv/((len(host_list)-1) if (len(host_list)-1) > 0 else 1)
                except Exception:
                    _net_diff_total_send = 0
                    _net_diff_total_recv = 0
                cluster_net_total_send += _net_diff_total_send
                cluster_net_total_recv += _net_diff_total_recv
        return cluster_net_total_send, cluster_net_total_recv

    def net_card_used_total(self, net_bytes):
        net_used_total = 0
        for value in net_bytes.values():
            try:
                net_used_total += float(value)
            except ValueError:
                pass
        return net_used_total

    def net_used_from_group(self, host_group):
        recv_total, send_total = 0, 0
        for host in host_group.group_list:
            recv = json.loads(host.net_recv_bytes)
            send = json.loads(host.net_send_bytes)
            for recv_values in recv.values():
                recv_total += recv_values
            for send_values in send.values():
                send_total += send_values
        return recv_total, send_total

    def avg_mem_used(self):
        mem_total_list = []
        avg_mem_used_list = []
        avg_mem_total_list = []
        group_list = self.group_by_host_name()
        for host_list in group_list.values():
            mem_total_list.extend(host_list)
        max_mem_total = max(mem_total_list, key=lambda x: float(x.mem_total))
        for host_list in group_list.values():
            if host_list:
                avg_mem_used = sum(map(lambda x: float(x.mem_used), host_list))/len(host_list)
                weight = float(max_mem_total.mem_total)/(float(host_list[0].mem_total))
                avg_mem_total_list.append(float(host_list[0].mem_total))
                avg_mem_used_list.append(avg_mem_used*weight)
        else:
            cluster_mem_avg = (sum(avg_mem_used_list) / (sum(avg_mem_total_list) if sum(avg_mem_total_list) else 1)) * 100
        return cluster_mem_avg

    def disk_io_used(self):
        disk_group = self.group_by_disk_uuid() if not self.next_host_group else self.next_group()
        cluster_disk_total_read = 0
        cluster_disk_total_write = 0
        for disk_list in disk_group.values():
            diff_total_read, diff_total_write = 0.0, 0.0
            for idx, disk in enumerate(disk_list):
                if idx == len(disk_list) - 1:
                    continue
                pre_read = float(disk_list[idx].read_bytes)
                pre_write = float(disk_list[idx].write_bytes)
                next_read = float(disk_list[idx + 1].read_bytes)
                next_write = float(disk_list[idx + 1].write_bytes)
                read_diff = next_read - pre_read
                write_diff = next_write - pre_write
                diff_total_read += read_diff
                diff_total_write += write_diff
            else:
                try:
                    _diff_total_read = diff_total_read//((len(disk_list)-1) if (len(disk_list)-1) > 0 else 1)
                    _diff_total_write = diff_total_write//((len(disk_list)-1) if (len(disk_list)-1) > 0 else 1)
                except Exception:
                    _diff_total_read = 0
                    _diff_total_write = 0
                cluster_disk_total_read += _diff_total_read
                cluster_disk_total_write += _diff_total_write
        return cluster_disk_total_read, cluster_disk_total_write

    def disk_io_count(self):
        disk_group = self.group_by_disk_uuid() if not self.next_host_group else self.next_group()
        cluster_disk_total_read_count = 0
        cluster_disk_total_write_count = 0
        for disk_list in disk_group.values():
            diff_total_read, diff_total_write = 0.0, 0.0
            for idx, disk in enumerate(disk_list):
                if idx == len(disk_list) - 1:
                    continue
                pre_read = float(disk_list[idx].read_count)
                pre_write = float(disk_list[idx].write_count)
                next_read = float(disk_list[idx + 1].read_count)
                next_write = float(disk_list[idx + 1].write_count)
                read_diff = next_read - pre_read
                write_diff = next_write - pre_write
                diff_total_read += read_diff
                diff_total_write += write_diff
            else:
                try:
                    _diff_total_read = diff_total_read//((len(disk_list)-1) if (len(disk_list)-1) > 0 else 1)
                    _diff_total_write = diff_total_write//((len(disk_list)-1) if (len(disk_list)-1) > 0 else 1)
                except Exception:
                    _diff_total_read = 0
                    _diff_total_write = 0
                cluster_disk_total_read_count += _diff_total_read
                cluster_disk_total_write_count += _diff_total_write
        return cluster_disk_total_read_count, cluster_disk_total_write_count

    def disk_io_await(self):
        disk_group = self.group_by_disk_uuid() if not self.next_host_group else self.next_group()
        cluster_disk_total_await = 0
        for disk_list in disk_group.values():
            disk_avg_await = 0
            for idx, disk in enumerate(disk_list):
                disk_avg_await += float(disk.busy_time)
            disk_avg_await /= len(disk_list) if len(disk_list) else 1
            cluster_disk_total_await += disk_avg_await
        return cluster_disk_total_await


def group_data(data, region):
    dot_group_list = []
    region_time_list = []
    groupby_region = OrderedDict()
    for idx, obj in enumerate(data):
        add_timestamp = int(strft_2_timestamp(obj.add_time))
        mod_region, mod_sec = divmod(add_timestamp, region)
        if str(mod_region) not in groupby_region.keys():
            groupby_region.setdefault(str(mod_region), [obj])
        else:
            groupby_region[str(mod_region)].append(obj)
    for timestamp_mod, obj_list in groupby_region.items():
        date_str = timestamp_format(int(timestamp_mod) * region)
        if date_str not in region_time_list:
            region_time_list.append(date_str)
            host_group = HostGroup(region)
            host_group.group_list.extend(obj_list)
            dot_group_list.append(host_group)
    return dot_group_list, region_time_list


class RecuDictField(fields.Raw):
    """
    自定义的用于解析JSON格式的对象数据
    """
    def output(self, key, obj):
        value = fields.get_value(key if not self.attribute else self.attribute, obj)
        if value is not None:
            try:
                value = json.loads(value)
            except TypeError:
                value = value
        else:
            value = self.default
        return value


class SplitField(fields.Raw):
    """
    用于分割字符串成列表
    """
    def format(self, value):
        return [float(json.loads(val.strip('[').strip(']').strip().replace('\'', '"'))) for val in value.split(',')]

        
class JsonDecodeListField(fields.Raw):

    """
    用于解析字符串类型的列表  '[1.0,2.0]' ====output====> [1.0,2.0]
    """

    def format(self, value):
        can_be_loads = True
        try:
            value = json.loads(value)
        except ValueError:
            can_be_loads = False
        if not can_be_loads:
            if '\'' in value:
                value = value.replace('\'', '"')
            value = json.loads(value)
        for idx, val in enumerate(value):
            if isinstance(val, (str, unicode)):
                value[idx] = float(val)
        return value


class EnvelopeField(fields.Nested):

    """
    用于生成外壳Key,方便将对象数据进行一定程度的分类,使用
        { "envelope_key": { "obj_attr": fields_type }} === outout ===> { 'envelope':{"obj_attr":obj_val}}

    """

    def output(self, key, obj):
        envelope_field = {}
        value = fields.get_value(key if self.attribute else key, obj)
        if value is not None:
            for key, items in self.nested.items():
                field_obj = fields.marshal(value, items, key)
                for item_key, field in items.items():
                    if isinstance(field, fields.List):
                        if hasattr(value, item_key):
                            list_value = getattr(value, item_key)
                            field_obj = {key: field.format(list_value)}
                        else:
                            field_obj = {key: self.default}
                envelope_field.update(field_obj)
            return envelope_field
        else:
            return self.default


def capacity_translate(capacity):
    """
    容量单位自动转换
    :param capacity: capacity 以B为的单位的值
    :return: 自适应单位
    """
    unit_list = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    idx = 0
    capacity = float(capacity)
    while True:
        capacity /= 1024
        if capacity > 1024:
            idx += 1
            continue
        else:
            idx += 1
            break
    return '%0.2f' % capacity + ' ' + unit_list[idx]


def reverse_unit(strcapacity):
    unit_list = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    capacity, unit = strcapacity.split(' ')
    idx = unit_list.index(unit)
    return float(capacity) * pow(1024, idx)


def weight_con(capacity):
    """
    以TB为单位控制容量的权重: 1T = 100
    :param capacity:
    :return:
    """
    capacity = float(capacity)
    weight = capacity//pow(1024, 3)//10
    return int(weight)


def used_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        resp = func(*args, **kwargs)
        end = time.time()
        used = end - start
        print(u'使用时间:',used)
        return resp
    return wrapper


def _pickle_method(m):
    """
    解决进程池无法序列化类方法的问题
    import copy_reg
    import types
    copy_reg.pickle(types.MethodType, _pickle_method)
    :param m:
    :return:
    """
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)


def output_extend_field(obj, attr):
    if obj:
        extend = obj.extend
        if extend:
            try:
                extend = json.loads(extend)
                if isinstance(extend, dict):
                    attr = extend[attr] if extend.has_key(attr) else ''
                    return attr
                else:
                    return ''
            except ValueError:
                return ''
    return ''