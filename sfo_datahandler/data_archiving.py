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

from sfo_common.import_common import *

class DataArchiving(object):
    '''
    数据归档类
    '''
    def __init__(self):
        pass

    def nodestat_data_archiving(self, host_name, source_model, target_model, target_internal):
        '''
        归档nodestat数据
        :param host_name:
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == 'minutes':
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.host_name == host_name, source_model.add_time > now_time_min,
                     source_model.add_time < now_time)).order_by(source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(target_obj)
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid', 'host_name',
                                                          'host_runtime', 'host_time', 'add_time']:
                            continue
                        else:
                            tmp_list = []
                            for obj in obj_list:
                                if hasattr(obj, pro):
                                    val = str(getattr(obj, pro)).strip()
                                    if val:
                                        if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                            pass
                                        else:
                                            if str(pro).strip().lower() == 'host_average_load':
                                                if type(eval(str(val))) != list:
                                                    tmp_list.append(copy.deepcopy(str(val).split(',')))
                                                else:
                                                    tmp_list.append(copy.deepcopy(val))
                                            else:
                                                tmp_list.append(copy.deepcopy(val))
                            if tmp_list:
                                if type(eval(str(tmp_list[0]))) == list:
                                    setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                elif type(eval(str(tmp_list[0]))) == dict:
                                    setattr(target_obj, pro,
                                            json.dumps(util.cal_list_p95_for_json(tmp_list), encoding='UTF-8',
                                                       ensure_ascii=True))
                                else:
                                    setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                            else:
                                setattr(target_obj, pro, 'None')
                target_obj.guid = str(uuid.uuid1())
                target_obj.host_name = host_name
                target_obj.host_runtime = getattr(obj_list[0], 'host_runtime')
                target_obj.host_time = getattr(obj_list[0], 'host_time')
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter(target_model.host_name == host_name).order_by(
                    target_model.add_time.desc()).first()
                if last:
                    # diff_time一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("nodestat_data_archiving function excute exception:" + str(ex))

    def clsinfo_data_archiving(self, cluster_name, source_model, target_model, target_internal):
        '''
        归档cluster info 数据
        :param cluster_name:
        :param source_model:
        :param target_model:
        :param target_internal: hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.cluster_name == cluster_name, source_model.add_time > now_time_min,
                     source_model.add_time < now_time)).order_by(source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(target_obj)
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid', 'cluster_name',
                                                          'add_time']:
                            continue
                        else:
                            tmp_list = []
                            for obj in obj_list:
                                if hasattr(obj, pro):
                                    val = str(getattr(obj, pro)).strip()
                                    if val:
                                        if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                            pass
                                        else:
                                            tmp_list.append(copy.deepcopy(val))
                            if tmp_list:
                                if type(eval(str(tmp_list[0]))) == list:
                                    setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                elif type(eval(str(tmp_list[0]))) == dict:
                                    setattr(target_obj, pro,
                                            json.dumps(util.cal_list_p95_for_json(tmp_list), encoding='UTF-8',
                                                       ensure_ascii=True))
                                else:
                                    setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                            else:
                                setattr(target_obj, pro, 'None')
                target_obj.guid = str(uuid.uuid1())
                target_obj.cluster_name = cluster_name
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter(target_model.cluster_name == cluster_name).order_by(
                    target_model.add_time.desc()).first()
                if last:
                    # diff_time一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("clsinfo_data_archiving function excute exception:" + str(ex))

    def diskperform_data_archiving(self, host_name, source_model, target_model, target_internal):
        '''
        归档disk perform数据
        :param host_name:
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "minutes":
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            disks = db.session.query(source_model).filter(source_model.host_name == host_name).group_by(
                source_model.disk_name).all()
            db.session.expunge_all()
            if disks:
                for disk in disks:
                    if disk:
                        obj_list = db.session.query(source_model).filter(
                            and_(source_model.host_name == host_name, source_model.disk_name == disk.disk_name,
                                 source_model.add_time > now_time_min, source_model.add_time < now_time)).order_by(
                            source_model.add_time.desc()).all()
                        if obj_list:
                            target_obj = target_model()
                            pros = dir(target_obj)
                            if pros:
                                for pro in pros:
                                    if '__' in pro or '_' == str(pro)[0:1]:
                                        continue
                                    elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid',
                                                                      'host_name', 'disk_uuid', 'disk_name',
                                                                      'disk_total', 'add_time']:
                                        continue
                                    else:
                                        tmp_list = []
                                        for obj in obj_list:
                                            if hasattr(obj, pro):
                                                val = str(getattr(obj, pro)).strip()
                                                if val:
                                                    if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                                        pass
                                                    else:
                                                        tmp_list.append(copy.deepcopy(val))
                                        if tmp_list:
                                            if type(eval(str(tmp_list[0]))) == list:
                                                setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                            elif type(eval(str(tmp_list[0]))) == dict:
                                                setattr(target_obj, pro,
                                                        json.dumps(util.cal_list_p95_for_json(tmp_list),
                                                                   encoding='UTF-8', ensure_ascii=True))
                                            else:
                                                setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                                        else:
                                            setattr(target_obj, pro, 'None')
                            target_obj.guid = str(uuid.uuid1())
                            target_obj.host_name = host_name
                            target_obj.disk_uuid = disk.disk_uuid
                            target_obj.disk_name = disk.disk_name
                            target_obj.disk_total = disk.disk_total
                            target_obj.add_time = now_time
                            last = db.session.query(target_model).filter(and_(target_model.host_name == host_name,
                                                                              target_model.disk_name == disk.disk_name)).order_by(
                                target_model.add_time.desc()).first()
                            if last:
                                # diff_time 一条数据，已经存在了就跳过
                                if util.datediff_seconds(last.add_time, now_time) < diff_time:
                                    pass
                                else:
                                    db.session.add(target_obj)
                            else:
                                db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("diskperform_data_archiving function excute exception:" + str(ex) + 'the host name is %s'%host_name)

    def nodeperform_data_archiving(self, host_name, source_model, target_model, target_internal):
        '''
        归档node perform数据
        :param host_name:
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "minutes":
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.host_name == host_name, source_model.add_time > now_time_min,
                     source_model.add_time < now_time)).order_by(source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(target_obj)
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        # 以下字段的值不能参与运算，所以排除单独赋值
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid', 'host_name',
                                                          'node_role', 'swift_version', 'node_time', 'stg_diskusage',
                                                          'node_ringmd5', 'swiftconfmd5', 'quarantined_count',
                                                          'account_replication', 'container_replication',
                                                          'object_replication', 'object_expirer', 'add_time']:
                            continue
                        else:
                            tmp_list = []
                            for obj in obj_list:
                                if hasattr(obj, pro):
                                    val = str(getattr(obj, pro)).strip()
                                    if val:
                                        if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                            pass
                                        else:
                                            tmp_list.append(copy.deepcopy(val))
                            if tmp_list:
                                if type(eval(str(tmp_list[0]))) == list:
                                    setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                elif type(eval(str(tmp_list[0]))) == dict:
                                    setattr(target_obj, pro,
                                            json.dumps(util.cal_list_p95_for_json(tmp_list), encoding='UTF-8',
                                                       ensure_ascii=True))
                                else:
                                    setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                            else:
                                setattr(target_obj, pro, 'None')
                target_obj.guid = str(uuid.uuid1())
                target_obj.host_name = host_name
                target_obj.node_role = obj_list[0].node_role
                target_obj.swift_version = obj_list[0].swift_version
                target_obj.node_time = obj_list[0].node_time
                target_obj.stg_diskusage = obj_list[0].stg_diskusage
                target_obj.node_ringmd5 = obj_list[0].node_ringmd5
                target_obj.swiftconfmd5 = obj_list[0].swiftconfmd5
                target_obj.quarantined_count = obj_list[0].quarantined_count
                target_obj.account_replication = obj_list[0].account_replication
                target_obj.container_replication = obj_list[0].container_replication
                target_obj.object_replication = obj_list[0].object_replication
                target_obj.object_expirer = obj_list[0].object_expirer
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter(target_model.host_name == host_name).order_by(
                    target_model.add_time.desc()).first()
                if last:
                    # diff_time 一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("nodeperform_data_archiving function excute exception:" + str(ex) + 'the host name is %s'%host_name)

    def nodesrv_data_archiving(self, host_name, source_model, target_model, target_internal):
        '''
        归档node service stat数据
        :param host_name:
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "minutes":
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.host_name == host_name, source_model.add_time > now_time_min,
                     source_model.add_time < now_time)).order_by(source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(obj_list[0])
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class']:
                            continue
                        else:
                            if hasattr(target_obj, pro):
                                val = str(getattr(obj_list[0], pro)).strip()
                                setattr(target_obj, pro, val)
                target_obj.guid = str(uuid.uuid1())
                target_obj.host_name = host_name
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter(target_model.host_name == host_name).order_by(
                    target_model.add_time.desc()).first()
                if last:
                    # diff_time 一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("nodesrv_data_archiving function excute exception:" + str(ex))

    def hostmon_data_archiving(self, host_name, source_model, target_model, target_internal):
        '''
        归档host monitor数据
        :param host_name:
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "minutes":
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.host_name == host_name, source_model.add_time > now_time_min,
                     source_model.add_time < now_time)).order_by(source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(target_obj)
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        # 以下字段的值不能参与运算，所以排除单独赋值
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid', 'data_model',
                                                          'cluster_name', 'host_name', 'host_net_stat',
                                                          'host_disk_stat', 'host_rw_file', 'extend', 'add_time']:
                            continue
                        else:
                            tmp_list = []
                            for obj in obj_list:
                                if hasattr(obj, pro):
                                    val = str(getattr(obj, pro)).strip()
                                    if val:
                                        if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                            pass
                                        else:
                                            tmp_list.append(copy.deepcopy(val))
                            if tmp_list:
                                if type(eval(str(tmp_list[0]))) == list:
                                    setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                elif type(eval(str(tmp_list[0]))) == dict:
                                    setattr(target_obj, pro,
                                            json.dumps(util.cal_list_p95_for_json(tmp_list), encoding='UTF-8',
                                                       ensure_ascii=True))
                                else:
                                    setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                            else:
                                setattr(target_obj, pro, 'None')
                target_obj.guid = str(uuid.uuid1())
                target_obj.data_model = obj_list[0].data_model
                target_obj.cluster_name = obj_list[0].cluster_name
                target_obj.host_name = host_name
                target_obj.host_net_stat = obj_list[0].host_net_stat
                target_obj.host_disk_stat = obj_list[0].host_disk_stat
                target_obj.host_rw_file = obj_list[0].host_rw_file
                target_obj.extend = obj_list[0].extend
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter(target_model.host_name == host_name).order_by(
                    target_model.add_time.desc()).first()
                if last:
                    # diff_time 一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("diskperform_data_archiving function excute exception:" + str(ex))

    def statsd_data_archiving(self, source_model, target_model, target_internal):
        '''
        归档StatsD数据
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "minutes":
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.add_time > now_time_min, source_model.add_time < now_time)).order_by(
                source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(target_obj)
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        # 以下字段的值不能参与运算，所以排除单独赋值
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid', 'cluster_name',
                                                          'sets', 'pctThreshold', 'add_time']:
                            continue
                        else:
                            tmp_list = []
                            for obj in obj_list:
                                if hasattr(obj, pro):
                                    val = str(getattr(obj, pro)).strip()
                                    if val:
                                        if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                            pass
                                        else:
                                            tmp_list.append(copy.deepcopy(val))
                            if tmp_list:
                                if type(eval(str(tmp_list[0]))) == list:
                                    setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                elif type(eval(str(tmp_list[0]))) == dict:
                                    setattr(target_obj, pro,
                                            json.dumps(util.cal_list_p95_for_json(tmp_list), encoding='UTF-8',
                                                       ensure_ascii=True))
                                else:
                                    setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                            else:
                                setattr(target_obj, pro, 'None')
                target_obj.guid = str(uuid.uuid1())
                target_obj.cluster_name = obj_list[0].cluster_name
                target_obj.sets = obj_list[0].sets
                target_obj.pctThreshold = obj_list[0].pctThreshold
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter().order_by(target_model.add_time.desc()).first()
                if last:
                    # diff_time 一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("statsd_data_archiving function excute exception:" + str(ex))

    def proxystatsd_data_archiving(self, source_model, target_model, target_internal):
        '''
        归档proxy StatsD数据
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "minutes":
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.add_time > now_time_min, source_model.add_time < now_time)).order_by(
                source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(target_obj)
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        # 以下字段的值不能参与运算，所以排除单独赋值
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid', 'cluster_name','add_time']:
                            continue
                        else:
                            tmp_list = []
                            for obj in obj_list:
                                if hasattr(obj, pro):
                                    val = str(getattr(obj, pro)).strip()
                                    if val:
                                        if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                            pass
                                        else:
                                            tmp_list.append(copy.deepcopy(val))
                            if tmp_list:
                                if type(eval(str(tmp_list[0]))) == list:
                                    setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                elif type(eval(str(tmp_list[0]))) == dict:
                                    setattr(target_obj, pro,json.dumps(util.cal_list_p95_for_json(tmp_list), encoding='UTF-8',ensure_ascii=True))
                                else:
                                    setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                            else:
                                setattr(target_obj, pro, 'None')
                target_obj.guid = str(uuid.uuid1())
                target_obj.cluster_name = obj_list[0].cluster_name
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter().order_by(target_model.add_time.desc()).first()
                if last:
                    # diff_time 一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("proxystatsd_data_archiving function excute exception:" + str(ex))

    def objectstatsd_data_archiving(self, source_model, target_model, target_internal):
        '''
        归档object StatsD数据
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "minutes":
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.add_time > now_time_min, source_model.add_time < now_time)).order_by(
                source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(target_obj)
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        # 以下字段的值不能参与运算，所以排除单独赋值
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid', 'cluster_name','add_time']:
                            continue
                        else:
                            tmp_list = []
                            for obj in obj_list:
                                if hasattr(obj, pro):
                                    val = str(getattr(obj, pro)).strip()
                                    if val:
                                        if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                            pass
                                        else:
                                            tmp_list.append(copy.deepcopy(val))
                            if tmp_list:
                                if type(eval(str(tmp_list[0]))) == list:
                                    setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                elif type(eval(str(tmp_list[0]))) == dict:
                                    setattr(target_obj, pro,json.dumps(util.cal_list_p95_for_json(tmp_list), encoding='UTF-8',ensure_ascii=True))
                                else:
                                    setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                            else:
                                setattr(target_obj, pro, 'None')
                target_obj.guid = str(uuid.uuid1())
                target_obj.cluster_name = obj_list[0].cluster_name
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter().order_by(target_model.add_time.desc()).first()
                if last:
                    # diff_time 一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("objectstatsd_data_archiving function excute exception:" + str(ex))

    def containerstatsd_data_archiving(self, source_model, target_model, target_internal):
        '''
        归档container StatsD数据
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "minutes":
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.add_time > now_time_min, source_model.add_time < now_time)).order_by(
                source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(target_obj)
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        # 以下字段的值不能参与运算，所以排除单独赋值
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid', 'cluster_name','add_time']:
                            continue
                        else:
                            tmp_list = []
                            for obj in obj_list:
                                if hasattr(obj, pro):
                                    val = str(getattr(obj, pro)).strip()
                                    if val:
                                        if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                            pass
                                        else:
                                            tmp_list.append(copy.deepcopy(val))
                            if tmp_list:
                                if type(eval(str(tmp_list[0]))) == list:
                                    setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                elif type(eval(str(tmp_list[0]))) == dict:
                                    setattr(target_obj, pro,json.dumps(util.cal_list_p95_for_json(tmp_list), encoding='UTF-8',ensure_ascii=True))
                                else:
                                    setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                            else:
                                setattr(target_obj, pro, 'None')
                target_obj.guid = str(uuid.uuid1())
                target_obj.cluster_name = obj_list[0].cluster_name
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter().order_by(target_model.add_time.desc()).first()
                if last:
                    # diff_time 一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("containerstatsd_data_archiving function excute exception:" + str(ex))

    def accountstatsd_data_archiving(self, source_model, target_model, target_internal):
        '''
        归档account StatsD数据
        :param source_model:
        :param target_model:
        :param target_internal: minutes,hours,days
        :return:
        '''
        try:
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            diff_time = 0
            if str(target_internal).strip().lower() == "minutes":
                diff_time = 300
                now_time_min = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "hours":
                diff_time = 3600
                now_time_min = (datetime.datetime.now() + datetime.timedelta(hours=-1)).strftime("%Y-%m-%d %H:%M:%S")
            elif str(target_internal).strip().lower() == "days":
                diff_time = 43200
                now_time_min = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_time_min = now_time
            obj_list = db.session.query(source_model).filter(
                and_(source_model.add_time > now_time_min, source_model.add_time < now_time)).order_by(
                source_model.add_time.desc()).all()
            db.session.expunge_all()
            if obj_list:
                target_obj = target_model()
                pros = dir(target_obj)
                if pros:
                    for pro in pros:
                        if '__' in pro or '_' == str(pro)[0:1]:
                            continue
                        # 以下字段的值不能参与运算，所以排除单独赋值
                        elif str(pro).strip().lower() in ['metadata', 'query', 'query_class', 'guid', 'cluster_name','add_time']:
                            continue
                        else:
                            tmp_list = []
                            for obj in obj_list:
                                if hasattr(obj, pro):
                                    val = str(getattr(obj, pro)).strip()
                                    if val:
                                        if 'null' in str(val).lower() or 'N/A' in str(val).upper():
                                            pass
                                        else:
                                            tmp_list.append(copy.deepcopy(val))
                            if tmp_list:
                                if type(eval(str(tmp_list[0]))) == list:
                                    setattr(target_obj, pro, str(util.cal_list_p95_for_list(tmp_list)))
                                elif type(eval(str(tmp_list[0]))) == dict:
                                    setattr(target_obj, pro,json.dumps(util.cal_list_p95_for_json(tmp_list), encoding='UTF-8',ensure_ascii=True))
                                else:
                                    setattr(target_obj, pro, str(util.cal_list_p95(tmp_list)))
                            else:
                                setattr(target_obj, pro, 'None')
                target_obj.guid = str(uuid.uuid1())
                target_obj.cluster_name = obj_list[0].cluster_name
                target_obj.add_time = now_time
                last = db.session.query(target_model).filter().order_by(target_model.add_time.desc()).first()
                if last:
                    # diff_time 一条数据，已经存在了就跳过
                    if util.datediff_seconds(last.add_time, now_time) < diff_time:
                        pass
                    else:
                        db.session.add(target_obj)
                else:
                    db.session.add(target_obj)
            db.session.commit()
        except Exception as ex:
            db.session.commit()
            logger.info("accountstatsd_data_archiving function excute exception:" + str(ex))