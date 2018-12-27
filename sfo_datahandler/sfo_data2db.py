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
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))

from sfo_common.agent import Agent
from sfo_datahandler.data_archiving import *

config = Config()
logging.config.fileConfig(config.logging_conf)
logger = logging.getLogger("agent")
util = Util()
evt = Event()
pids = []
thread_workers = []
# kafka
from pykafka import KafkaClient
from swiftclient import client


class ConsumeData2Db(object):
    '''
    数据处理类
    消费kafka数据
    数据统计
    数据归档
    '''
    def __init__(self):
        pass

    def consume_data(self):
        '''
        消费kafka_sys_topic数据，入mysql数据库
        数据来源于节点agent采集
        :return:
        '''
        try:
            mkcli = KafkaClient(zookeeper_hosts=config.zookeeper_server)
            if mkcli:
                if mkcli.topics.has_key(config.kafka_sys_topic):
                    mtopic = mkcli.topics[config.kafka_sys_topic]
                    if mtopic is not None:
                        if config.process_workers > 1 :
                            mconsumer = mtopic.get_balanced_consumer(consumer_group='sfo-cluster-group',auto_commit_enable=True,zookeeper_connect=config.zookeeper_server)
                        else:
                            mconsumer = mtopic.get_simple_consumer()
                        for message in mconsumer:
                            if message.value:
                                if util.is_json(message.value):
                                    msg = json.loads(message.value, encoding="UTF-8")
                                else:
                                    continue
                                if isinstance(msg, list):
                                    for submsg in msg:
                                        if not submsg:
                                            continue
                                        if isinstance(submsg, dict):
                                            if submsg.has_key('data_model'):
                                                if str(submsg['data_model']).strip().upper() == 'SfoDiskPerform'.upper():
                                                    spd = SfoDiskPerform()
                                                    spdh = SfoDiskPerformHistory()
                                                    for key in submsg.keys():
                                                        if hasattr(spd, key):
                                                            setattr(spd, key, str(submsg[key]))
                                                            setattr(spdh, key, str(submsg[key]))
                                                    if spd:
                                                        rows = db.session.query(SfoDiskPerform).filter_by(guid=spd.guid).all()
                                                        if len(rows) == 0:
                                                            try:
                                                                db.session.add(spd)
                                                                db.session.add(spdh)
                                                                db.session.commit()
                                                            except Exception as ex:
                                                                db.session.close()
                                                                db.session.remove()
                                                                logger.info(
                                                                    "insert disk perform history data table exception:{}".format(
                                                                        str(ex)))
                                                else:
                                                    logger.info('this data type is not supported,datatype is: %s',
                                                                str(type(submsg)))
                                            else:
                                                logger.info('this data has no key data_model,data is: %s', str(submsg))
                                        else:
                                            logger.info('this data type is not supported,data type is: %s',
                                                        str(type(submsg)))
                                elif isinstance(msg, dict):
                                    if msg is None:
                                        continue
                                    if msg.has_key('data_model'):
                                        if str(msg['data_model']).strip().upper() == 'SfoHostInfo'.upper():
                                            hi = SfoHostInfo()
                                            for key in msg.keys():
                                                if hasattr(hi, key):
                                                    setattr(hi, key, str(msg[key]))
                                            if hi:
                                                try:
                                                    rows = db.session.query(SfoHostInfo).filter_by(guid=hi.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(hi)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(str(ex))
                                        elif str(msg['data_model']).strip().upper() == 'SfoClusterInfo'.upper():
                                            sli = SfoClusterInfo()
                                            for key in msg.keys():
                                                if hasattr(sli, key):
                                                    setattr(sli, key, str(msg[key]))
                                            if sli:
                                                try:
                                                    rows = SfoClusterInfo.query.filter_by(guid=sli.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(sli)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(str(ex))
                                        elif str(msg['data_model']).strip().upper() == 'SfoNodePerform'.upper():
                                            snp = SfoNodePerform()
                                            snph = SfoNodePerformHistory()
                                            for key in msg.keys():
                                                if hasattr(snp, key):
                                                    setattr(snp, key, str(msg[key]))
                                                    setattr(snph, key, str(msg[key]))
                                            if snp is not None:
                                                try:
                                                    rows = SfoNodePerform.query.filter_by(guid=snp.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(snp)
                                                        # add to histoty table
                                                        db.session.add(snph)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(
                                                        "insert node perform history data table exception:{}".format(
                                                            str(ex)))
                                        elif str(msg['data_model']).strip().upper() == 'SfoHostMonitor'.upper():
                                            shm = SfoHostMonitor()
                                            shmh = SfoHostMonitorHistory()
                                            for key in msg.keys():
                                                if hasattr(shm, key):
                                                    setattr(shm, key, str(msg[key]))
                                                    setattr(shmh, key, str(msg[key]))
                                            if shm:
                                                try:
                                                    rows = SfoHostMonitor.query.filter_by(guid=shm.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(shm)
                                                        # add to histoty table
                                                        db.session.add(shmh)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(
                                                        "insert host monitor history data table exception:{}".format(
                                                            str(ex)))
                                        elif str(msg['data_model']).strip().upper() == 'SfoNodeService'.upper():
                                            sns = SfoNodeService()
                                            snsh = SfoNodeServiceHistory()
                                            for key in msg.keys():
                                                if hasattr(sns, key):
                                                    setattr(sns, key, str(msg[key]))
                                                    setattr(snsh, key, str(msg[key]))
                                            if sns:
                                                try:
                                                    rows = SfoNodeService.query.filter_by(guid=sns.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(sns)
                                                        # add to histoty table
                                                        db.session.add(snsh)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(
                                                        "insert node service history data table exception:{}".format(
                                                            str(ex)))
                                        elif str(msg['data_model']).strip().upper() == 'SfoNodeStat'.upper():
                                            snst = SfoNodeStat()
                                            snsth = SfoNodeStatHistory()
                                            for key in msg.keys():
                                                if hasattr(snst, key):
                                                    setattr(snst, key, str(msg[key]))
                                                    setattr(snsth, key, str(msg[key]))
                                            if snst:
                                                try:
                                                    rows = SfoNodeStat.query.filter_by(guid=snst.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(snst)
                                                        # add to histoty table
                                                        db.session.add(snsth)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(
                                                        "insert node status history data table exception:{}".format(
                                                            str(ex)))
                                        elif str(msg['data_model']).strip().upper() == 'SfoAccountStatsD'.upper():
                                            sas = SfoAccountStatsD()
                                            for key in msg.keys():
                                                if hasattr(sas, key):
                                                    setattr(sas, key, str(msg[key]))
                                            if sas is not None:
                                                try:
                                                    rows = SfoAccountStatsD.query.filter_by(guid=sas.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(sas)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(str(ex))
                                        elif str(msg['data_model']).strip().upper() == 'SfoContainerStatsD'.upper():
                                            scs = SfoContainerStatsD()
                                            for key in msg.keys():
                                                if hasattr(scs, key):
                                                    setattr(scs, key, str(msg[key]))
                                            if scs is not None:
                                                try:
                                                    rows = SfoContainerStatsD.query.filter_by(guid=scs.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(scs)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(str(ex))
                                        elif str(msg['data_model']).strip().upper() == 'SfoObjectStatsD'.upper():
                                            sos = SfoObjectStatsD()
                                            for key in msg.keys():
                                                if hasattr(sos, key):
                                                    setattr(sos, key, str(msg[key]))
                                            if sos:
                                                try:
                                                    rows = SfoObjectStatsD.query.filter_by(guid=sos.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(sos)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(str(ex))
                                        elif str(msg['data_model']).strip().upper() == 'SfoProxyStatsD'.upper():
                                            sps = SfoProxyStatsD()
                                            for key in msg.keys():
                                                if hasattr(sps, key):
                                                    setattr(sps, key, str(msg[key]))
                                            if sps:
                                                try:
                                                    rows = SfoProxyStatsD.query.filter_by(guid=sps.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(sps)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(str(ex))
                                        elif str(msg['data_model']).strip().upper() == 'SfoHostRing'.upper():
                                            shr = SfoHostRing()
                                            for key in msg.keys():
                                                if hasattr(shr, key):
                                                    setattr(shr, key, str(msg[key]))
                                            if shr is not None:
                                                try:
                                                    rows = SfoHostRing.query.filter_by(guid=shr.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(shr)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(str(ex))
                                        elif str(msg['data_model']).strip().upper() == 'BeatHeart'.upper():
                                            bhi = BeatHeartInfo()
                                            for key in msg.keys():
                                                if hasattr(bhi, key):
                                                    setattr(bhi, key, str(msg[key]))
                                            if bhi:
                                                try:
                                                    rows = BeatHeartInfo.query.filter_by(guid=bhi.guid).all()
                                                    if len(rows) == 0:
                                                        db.session.add(bhi)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(str(ex))
                                        elif str(msg['data_model']).strip().upper() == 'SfoAlarmLog'.upper():
                                            sal = SfoAlarmLog()
                                            for key in msg.keys():
                                                if hasattr(sal, key):
                                                    setattr(sal, key, str(msg[key]))
                                            if sal:
                                                try:
                                                    salh = SfoAlarmLog.query.filter(
                                                        and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                             SfoAlarmLog.alarm_result == '0')).first()
                                                    if salh:
                                                        salh.alarm_result = '1'
                                                        db.session.add(salh)
                                                        db.session.add(sal)
                                                        db.session.commit()
                                                except Exception as ex:
                                                    db.session.close()
                                                    db.session.remove()
                                                    logger.info(str(ex))
                                        else:
                                            logger.info(str(msg))
                                    else:
                                        logger.info('this data has no key data_model,data is: %s', str(msg))
                                else:
                                    logger.info("the data type is not supported:" + str(msg))
                    else:
                        logger.info("topic %s is None:" % (str(config.kafka_sys_topic)))
                else:
                    logger.info("kafka has no topic %s:" % (str(config.kafka_sys_topic)))
            else:
                logger.info("init to kafka fialed")
        except Exception, error:
            logger.info("consume_data function excute exception:" + str(error))
        else:
            logger.info("consume_data function excute strange, no exception catched but the program  excute failed")
        finally:
            db.session.close()
            db.session.remove()
            logger.info("consume_data is stopping,now time is " + str(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            return

    def reg_match(self, param, str):
        '''
        正则匹配
        判断param是否在str中
        :param param:
        :param str:
        :return:
        '''
        result = False
        try:
            res = re.findall(param, str)
            if len(res) == 0:
                result = False
            else:
                result = True
        except Exception as ex:
            result = False
            logger.info("reg_match function excute exception:" + str(ex))
        finally:
            return result

    def get_counter_values(self, key, counter):
        '''
        从counter数据中统计key的累加值
        :param key:
        :param counter:
        :return: key对应的值的和
        '''
        msum = 0
        try:
            for ckey in counter.keys():
                if self.reg_match(key, ckey):
                    if counter[ckey]:
                        msum += int(counter[ckey])
        except Exception as ex:
            msum = -1
            logger.info("get_counter_value function excute exception:" + str(ex))
        finally:
            return str(msum)

    def get_timer_data_value(self, key, timer_data):
        '''
        从timer_data中找出包含key项的值
        :param key:
        :param timer_data:
        :return:
        '''
        result = {}
        try:
            for tkey in timer_data.keys():
                if self.reg_match(key, tkey):
                    result[tkey] = timer_data[tkey]
        except Exception as ex:
            logger.info("get_timer_data_value function excute exception:" + str(ex))
        finally:
            return json.dumps(result, encoding='utf-8', ensure_ascii=True)

    def consume_statsd_data(self):
        '''
        消费kafka_statd_topic主题的kafka数据 （statsD服务器数据，各项参考statsD官方文档）
        将数据存入mysql数据库
        :return:
        '''
        try:
            csdkcli = KafkaClient(zookeeper_hosts=config.zookeeper_server)
            mtp = csdkcli.topics[config.kafka_statd_topic]
            if config.process_workers > 1:
                csdconsumer = mtp.get_balanced_consumer(consumer_group='sfo-statsd-group', auto_commit_enable=True,
                                                        zookeeper_connect=config.zookeeper_server)
            else:
                csdconsumer = mtp.get_simple_consumer()
            for csdmsg in csdconsumer:
                if csdmsg.value is not None:
                    if util.is_json(csdmsg.value):
                        msg = json.loads(csdmsg.value, encoding="UTF-8")
                    else:
                        continue
                    if isinstance(msg, dict):
                        addtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        statsd = SfoStatsD()
                        statsd.guid = str(uuid.uuid1())
                        if msg.has_key('timestamp'):
                            if str(msg['timestamp']).isdigit():
                                addtime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(msg['timestamp']) / 1000))

                        for key in msg.keys():
                            if hasattr(statsd, key):
                                setattr(statsd, key, json.dumps(msg[key], encoding="utf-8", ensure_ascii=True))
                        if statsd is not None:
                            statsd.add_time = addtime
                            db.session.add(statsd)
                        # account container object proxy data to db
                        sasd = SfoAccountStatsD()
                        scsd = SfoContainerStatsD()
                        sosd = SfoObjectStatsD()
                        spsd = SfoProxyStatsD()

                        if msg.has_key('counters'):
                            if isinstance(msg['counters'], dict):
                                if msg['counters'] is not None:
                                    sasd.auditor_errors = self.get_counter_values('account-auditor.errors',msg['counters'])
                                    sasd.auditor_passes = self.get_counter_values('account-auditor.passes',msg['counters'])
                                    sasd.auditor_failures = self.get_counter_values('account-auditor.failures', msg['counters'])

                                    sasd.reaper_errors = self.get_counter_values('account-reaper.errors',msg['counters'])
                                    sasd.reaper_return_codes = self.get_counter_values('account-reaper.return_codes', msg['counters'])
                                    sasd.reaper_ctn_failures = self.get_counter_values('account-reaper.containers_failures', msg['counters'])
                                    sasd.reaper_ctn_deleted = self.get_counter_values('account-reaper.containers_deleted', msg['counters'])
                                    sasd.reaper_ctn_remaining = self.get_counter_values('account-reaper.containers_remaining', msg['counters'])
                                    sasd.reaper_ctn_psb_remaining = self.get_counter_values('account-reaper.containers_possibly_remaining', msg['counters'])
                                    sasd.reaper_obj_failures = self.get_counter_values('account-reaper.objects_failures', msg['counters'])
                                    sasd.reaper_obj_deleted = self.get_counter_values('account-reaper.objects_deleted', msg['counters'])
                                    sasd.reaper_obj_remaining = self.get_counter_values('account-reaper.objects_remaining', msg['counters'])
                                    sasd.reaper_obj_psb_remaining = self.get_counter_values('account-reaper.objects_possibly_remaining', msg['counters'])

                                    sasd.replicator_diffs = self.get_counter_values('account-replicator.diffs',msg['counters'])
                                    sasd.replicator_diff_caps = self.get_counter_values('account-replicator.diff_caps', msg['counters'])
                                    sasd.replicator_no_changes = self.get_counter_values('account-replicator.no_changes', msg['counters'])
                                    sasd.replicator_hashmatches = self.get_counter_values('account-replicator.hashmatches', msg['counters'])
                                    sasd.replicator_rsyncs = self.get_counter_values('account-replicator.rsyncs', msg['counters'])
                                    sasd.replicator_remote_merges = self.get_counter_values('account-replicator.remote_merges', msg['counters'])
                                    sasd.replicator_attempts = self.get_counter_values('account-replicator.attempts',msg['counters'])
                                    sasd.replicator_failures = self.get_counter_values('account-replicator.failures',msg['counters'])
                                    sasd.replicator_removes = self.get_counter_values('account-replicator.removes', msg['counters'])
                                    sasd.replicator_successes = self.get_counter_values('account-replicator.successes', msg['counters'])

                                    scsd.auditor_errors = self.get_counter_values('container-auditor.errors', msg['counters'])
                                    scsd.auditor_passes = self.get_counter_values('container-auditor.passes', msg['counters'])
                                    scsd.auditor_failures = self.get_counter_values('container-auditor.failures', msg['counters'])

                                    scsd.replicator_diffs = self.get_counter_values('container-replicator.diffs',msg['counters'])
                                    scsd.replicator_diff_caps = self.get_counter_values('container-replicator.diff_caps', msg['counters'])
                                    scsd.replicator_no_changes = self.get_counter_values( 'container-replicator.no_changes', msg['counters'])
                                    scsd.replicator_hashmatches = self.get_counter_values('container-replicator.hashmatches', msg['counters'])
                                    scsd.replicator_rsyncs = self.get_counter_values('container-replicator.rsyncs',msg['counters'])
                                    scsd.replicator_remote_merges = self.get_counter_values('container-replicator.remote_merges', msg['counters'])
                                    scsd.replicator_attempts = self.get_counter_values('container-replicator.attempts',msg['counters'])
                                    scsd.replicator_failures = self.get_counter_values('container-replicator.failures', msg['counters'])
                                    scsd.replicator_removes = self.get_counter_values('container-replicator.removes',msg['counters'])
                                    scsd.replicator_successes = self.get_counter_values('container-replicator.successes', msg['counters'])

                                    scsd.sync_skips = self.get_counter_values('container-sync.skips', msg['counters'])
                                    scsd.sync_failures = self.get_counter_values('container-sync.failures', msg['counters'])
                                    scsd.sync_syncs = self.get_counter_values('container-sync.syncs', msg['counters'])
                                    scsd.sync_deletes = self.get_counter_values('container-sync.deletes',msg['counters'])
                                    scsd.sync_puts = self.get_counter_values('container-sync.puts', msg['counters'])

                                    scsd.updater_successes = self.get_counter_values('container-updater.successes', msg['counters'])
                                    scsd.updater_failures = self.get_counter_values('container-updater.failures', msg['counters'])
                                    scsd.updater_no_changes = self.get_counter_values('container-updater.no_changes',msg['counters'])

                                    sosd.auditor_quarantines = self.get_counter_values('object-auditor.quarantines',msg['counters'])
                                    sosd.auditor_errors = self.get_counter_values('object-auditor.errors', msg['counters'])

                                    sosd.expirer_objects = self.get_counter_values('object-expirer.objects', msg['counters'])
                                    sosd.expirer_errors = self.get_counter_values('object-expirer.errors',msg['counters'])

                                    sosd.reconstructor_part_del_count = self.get_counter_values('object-reconstructor.partition.delete.count', msg['counters'])
                                    sosd.reconstructor_part_update_count = self.get_counter_values('object-reconstructor.partition.update.count.', msg['counters'])
                                    sosd.reconstructor_suffix_hashes = self.get_counter_values('object-reconstructor.suffix.hashes', msg['counters'])
                                    sosd.reconstructor_suffix_syncs = self.get_counter_values('object-reconstructor.suffix.syncs', msg['counters'])

                                    sosd.replicator_part_del_count = self.get_counter_values('object-replicator.partition.delete.count', msg['counters'])
                                    sosd.replicator_part_update_count = self.get_counter_values('object-replicator.partition.update.count', msg['counters'])
                                    sosd.replicator_suffix_hashes = self.get_counter_values('object-replicator.suffix.hashes', msg['counters'])
                                    sosd.replicator_suffix_syncs = self.get_counter_values('object-replicator.suffix.syncs', msg['counters'])

                                    sosd.req_quarantines = self.get_counter_values('object-server.quarantines',msg['counters'])
                                    sosd.req_async_pendings = self.get_counter_values('object-server.async_pendings', msg['counters'])

                                    sosd.req_put_timeouts = self.get_counter_values('object-server.PUT.timeouts', msg['counters'])

                                    sosd.updater_errors = self.get_counter_values('object-updater.errors', msg['counters'])
                                    sosd.updater_quarantines = self.get_counter_values('object-updater.quarantines',msg['counters'])
                                    sosd.updater_successes = self.get_counter_values('object-updater.successes',msg['counters'])
                                    sosd.updater_failures = self.get_counter_values('object-updater.failures', msg['counters'])
                                    sosd.updater_unlinks = self.get_counter_values('object-updater.unlinks',msg['counters'])

                                    spsd.req_errors = self.get_counter_values('proxy-server.errors', msg['counters'])
                                    spsd.req_handoff_count = self.get_counter_values('proxy-server.*.handoff_count',msg['counters'])
                                    spsd.req_handoff_all_count = self.get_counter_values('proxy-server.*.handoff_all_count', msg['counters'])
                                    spsd.req_client_timeouts = self.get_counter_values('proxy-server.*.client_timeouts', msg['counters'])
                                    spsd.req_client_disconnects = self.get_counter_values('proxy-server.*.client_disconnects', msg['counters'])
                                    spsd.req_xfer = self.get_counter_values('proxy-server.*.*.*.xfer', msg['counters'])
                                    spsd.req_obj_policy_xfer = self.get_counter_values('proxy-server.object.policy.[\d].*.*.xfer', msg['counters'])
                                    spsd.req_auth_unauthorized = self.get_counter_values('tempauth.*.unauthorized', msg['counters'])
                                    spsd.req_auth_forbidden = self.get_counter_values('tempauth.*.forbidden', msg['counters'])
                                    spsd.req_auth_token_denied = self.get_counter_values('tempauth.*.token_denied', msg['counters'])
                                    spsd.req_auth_errors = self.get_counter_values('tempauth.*.errors', msg['counters'])
                                else:
                                    logger.info('msg[\'counters\'] is None!')
                            else:
                                logger.info(
                                    'the data type of msg[\'counters\'] is not supported,the data type is {}'.format(
                                        str(type(msg['counters']))))
                        if msg.has_key('timers'):
                            pass
                        if msg.has_key('timer_data'):
                            if isinstance(msg['timer_data'], dict):
                                if msg['timer_data'] is not None:
                                    sasd.auditor_timing = self.get_timer_data_value('account-auditor.timing',msg['timer_data'])

                                    sasd.reaper_timing = self.get_timer_data_value('account-reaper.timing', msg['timer_data'])

                                    sasd.req_del_err_timing = self.get_timer_data_value('account-server.DELETE.errors.timing', msg['timer_data'])
                                    sasd.req_del_timing = self.get_timer_data_value('account-server.DELETE.timing',msg['timer_data'])
                                    sasd.req_put_err_timing = self.get_timer_data_value('account-server.PUT.errors.timing', msg['timer_data'])
                                    sasd.req_put_timing = self.get_timer_data_value('account-server.PUT.timing',msg['timer_data'])
                                    sasd.req_head_err_timing = self.get_timer_data_value('account-server.HEAD.errors.timing', msg['timer_data'])
                                    sasd.req_head_timing = self.get_timer_data_value('account-server.HEAD.timing',msg['timer_data'])
                                    sasd.req_get_err_timing = self.get_timer_data_value('account-server.GET.errors.timing', msg['timer_data'])
                                    sasd.req_get_timing = self.get_timer_data_value('account-server.GET.timing',msg['timer_data'])
                                    sasd.req_rep_err_timing = self.get_timer_data_value('account-server.REPLICATE.errors.timing', msg['timer_data'])
                                    sasd.req_rep_timing = self.get_timer_data_value('account-server.REPLICATE.timing',msg['timer_data'])
                                    sasd.req_post_err_timing = self.get_timer_data_value('account-server.POST.errors.timing', msg['timer_data'])
                                    sasd.req_post_timing = self.get_timer_data_value('account-server.POST.timing', msg['timer_data'])

                                    sasd.replicator_timing = self.get_timer_data_value('account-replicator.timing',msg['timer_data'])

                                    scsd.auditor_timing = self.get_timer_data_value('container-auditor.timing',msg['timer_data'])

                                    scsd.replicator_timing = self.get_timer_data_value('container-replicator.timing', msg['timer_data'])

                                    scsd.req_del_err_timing = self.get_timer_data_value('container-server.DELETE.errors.timing', msg['timer_data'])
                                    scsd.req_del_timing = self.get_timer_data_value('container-server.DELETE.timing',msg['timer_data'])
                                    scsd.req_put_err_timing = self.get_timer_data_value('container-server.PUT.errors.timing', msg['timer_data'])
                                    scsd.req_put_timing = self.get_timer_data_value('container-server.PUT.timing',msg['timer_data'])
                                    scsd.req_head_err_timing = self.get_timer_data_value('container-server.HEAD.errors.timing', msg['timer_data'])
                                    scsd.req_head_timing = self.get_timer_data_value('container-server.HEAD.timing',msg['timer_data'])
                                    scsd.req_get_err_timing = self.get_timer_data_value( 'container-server.GET.errors.timing', msg['timer_data'])
                                    scsd.req_get_timing = self.get_timer_data_value('container-server.GET.timing',msg['timer_data'])
                                    scsd.req_rep_err_timing = self.get_timer_data_value('container-server.REPLICATE.errors.timing', msg['timer_data'])
                                    scsd.req_rep_timing = self.get_timer_data_value('container-server.REPLICATE.timing',msg['timer_data'])
                                    scsd.req_post_err_timing = self.get_timer_data_value('container-server.POST.errors.timing', msg['timer_data'])
                                    scsd.req_post_timing = self.get_timer_data_value('container-server.POST.timing', msg['timer_data'])

                                    scsd.sync_del_timing = self.get_timer_data_value('container-sync.deletes.timing',msg['timer_data'])
                                    scsd.sync_puts_timing = self.get_timer_data_value('container-sync.puts.timing',msg['timer_data'])

                                    scsd.updater_timing = self.get_timer_data_value('container-updater.timing',msg['timer_data'])

                                    sosd.auditor_timing = self.get_timer_data_value('object-auditor.timing',msg['timer_data'])

                                    sosd.expirer_timing = self.get_timer_data_value('object-expirer.timing',msg['timer_data'])

                                    sosd.reconstructor_part_del_timing = self.get_timer_data_value('object-reconstructor.partition.delete.timing', msg['timer_data'])
                                    sosd.reconstructor_part_update_timing = self.get_timer_data_value('object-reconstructor.partition.update.timing', msg['timer_data'])

                                    sosd.replicator_part_del_timing = self.get_timer_data_value('object-replicator.partition.delete.timing', msg['timer_data'])
                                    sosd.replicator_part_update_timing = self.get_timer_data_value('object-replicator.partition.update.timing', msg['timer_data'])

                                    sosd.req_post_err_timing = self.get_timer_data_value('object-server.POST.errors.timing', msg['timer_data'])
                                    sosd.req_post_timing = self.get_timer_data_value('object-server.POST.timing',msg['timer_data'])
                                    sosd.req_put_err_timing = self.get_timer_data_value('object-server.PUT.errors.timing', msg['timer_data'])
                                    sosd.req_put_timing = self.get_timer_data_value('object-server.PUT.timing', msg['timer_data'])
                                    sosd.req_put_dev_timing = self.get_timer_data_value('object-server.PUT.*.timing',msg['timer_data'])
                                    sosd.req_get_err_timing = self.get_timer_data_value('object-server.GET.errors.timing', msg['timer_data'])
                                    sosd.req_get_timing = self.get_timer_data_value('object-server.GET.timing', msg['timer_data'])
                                    sosd.req_head_err_timing = self.get_timer_data_value('object-server.HEAD.errors.timing', msg['timer_data'])
                                    sosd.req_head_timing = self.get_timer_data_value('object-server.HEAD.timing', msg['timer_data'])
                                    sosd.req_del_err_timing = self.get_timer_data_value('object-server.DELETE.errors.timing', msg['timer_data'])
                                    sosd.req_del_timing = self.get_timer_data_value('object-server.DELETE.timing',
                                                                                    msg['timer_data'])
                                    sosd.req_rep_err_timing = self.get_timer_data_value('object-server.REPLICATE.errors.timing', msg['timer_data'])
                                    sosd.req_rep_timing = self.get_timer_data_value('object-server.REPLICATE.timing',msg['timer_data'])

                                    sosd.updater_timing = self.get_timer_data_value('object-updater.timing',msg['timer_data'])

                                    spsd.req_timing = self.get_timer_data_value('proxy-server.*.*.*.timing',msg['timer_data'])
                                    spsd.req_get_timing = self.get_timer_data_value( 'proxy-server.*.GET.*.first-byte.timing', msg['timer_data'])
                                    spsd.req_obj_policy_timing = self.get_timer_data_value( 'proxy-server.object.policy.[\d].*.*.timing', msg['timer_data'])
                                    spsd.req_obj_policy_get_timing = self.get_timer_data_value('proxy-server.object.policy.[\d].GET.*.first-byte.timing', msg['timer_data'])
                                else:
                                    logger.info('msg[\'timers\'] is None!')
                            else:
                                logger.info('the data type of msg[\'timers\'] is not supported,the data type is {}'.format(str(type(msg['timers']))))
                        if msg.has_key('counter_rates'):
                            pass
                        # add data to database
                        # account
                        try:
                            if sasd:
                                sasd.guid = str(uuid.uuid1())
                                sasd.add_time = addtime
                                if not sasd.cluster_name:
                                    sasd.cluster_name = ''
                                db.session.add(sasd)
                            # container
                            if scsd is not None:
                                scsd.guid = str(uuid.uuid1())
                                scsd.add_time = addtime
                                if not scsd.cluster_name:
                                    scsd.cluster_name = ''
                                db.session.add(scsd)
                            # object
                            if sosd is not None:
                                sosd.guid = str(uuid.uuid1())
                                sosd.add_time = addtime
                                if not sosd.cluster_name:
                                    sosd.cluster_name = ''
                                db.session.add(sosd)
                            # proxy
                            if spsd is not None:
                                spsd.guid = str(uuid.uuid1())
                                spsd.add_time = addtime
                                if not spsd.cluster_name:
                                    spsd.cluster_name = ''
                                db.session.add(spsd)
                            db.session.commit()
                        except Exception as ex:
                            db.session.close()
                            db.session.remove()
                            logger.info(str(ex))
                    else:
                        logger.info('soory,the data format is not supported.we just support list and dict,but this data is {}'.format(str(type(msg))))
                else:
                    logger.info('in consume_statsd_data function,consumer data value is None.')
        except Exception as ex:
            logger.info("consume_statsd_data function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()
            logger.info("consume_statsd_data is stopping,now time is " + str(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))))
            return

    def get_cluster_info(self):
        '''
        集群数据统筹
        按集群将总览数据统计归纳，存入mysql数据库
        :return:
        '''
        try:
            rows = db.session.query(SfoClusterNodes).filter(SfoClusterNodes.node_stat == '1').group_by(SfoClusterNodes.cluster_name).all()
            db.session.expunge_all()
            if len(rows) == 0:
                logger.info("there is no node in this cluster,please add node first...")
            else:
                for row in rows:
                    try:
                        if not row or not row.cluster_name:
                            continue
                        sci = SfoClusterInfo()
                        sci.guid = str(uuid.uuid1())
                        sci.cluster_name = row.cluster_name
                        sci.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        nodes = db.session.query(SfoClusterNodes).filter(and_(SfoClusterNodes.cluster_name == row.cluster_name,SfoClusterNodes.node_stat == '1')).all()
                        db.session.expunge_all()
                        if not nodes:
                            continue
                        pnum = {}  # proxy info
                        pnumtotal = pnumonline = 0  # proxy total number, proxy online number
                        stgnum = {}  # storage node info
                        anum=anumonline=cnum=cnumonline=onum=onumonline = 0  # account server number...
                        netinfo = {}
                        nettotal=obj_nettotal=netused=netreptotal=netreptotal=netrepused = 0
                        disknum=disktotal=diskused=diskfree = 0
                        diskcapacity = {}
                        uri_fail_num=uri_total_num=uri_suc_num = 0
                        arec_pass_num=arec_fail_num=crec_pass_num=crec_fail_num=orec_pass_num=orec_err_num=orec_qua_num = 0
                        rec_auditor = {}
                        arep_no_change_num=arep_suc_num=arep_fail_num=crep_suc_num=crep_fail_num=crep_no_change_num=orep_suc_num=orep_fail_num=orep_remove_num = 0
                        rec_replicater = {}
                        cup_times=oup_times = 0.0
                        rec_updater = {}
                        rec_sync_num = 0
                        statd_proxy = db.session.query(SfoProxyStatsD).order_by(SfoProxyStatsD.add_time.desc()).first()
                        db.session.expunge_all()
                        for node in nodes:
                            if not node:
                                continue
                            # for node role
                            role = {}
                            nodestat = SfoNodeService()
                            if node.node_role:
                                role = json.loads(node.node_role, encoding="UTF-8")
                                nodestat = db.session.query(SfoNodeService).filter(SfoNodeService.host_name == node.node_host_name).order_by(SfoNodeService.add_time.desc()).first()
                                db.session.expunge_all()
                            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            if role.has_key('Proxy-Server') and str(role['Proxy-Server']).strip().upper() == 'YES':
                                pnumtotal += 1
                                if nodestat and util.datediff_seconds(nodestat.add_time, nowtime) < 180:
                                    if str(nodestat.srv_proxy).strip().upper() == 'RUNNING':
                                        pnumonline += 1
                                    else:
                                        sal = SfoAlarmLog()
                                        sal.guid = str(uuid.uuid1())
                                        sal.alarm_device = "proxy-service-{}".format(str(nodestat.host_name))
                                        sal.alarm_type = 'software'
                                        sal.hostname = nodestat.host_name
                                        sal.device_name = 'proxy service'
                                        sal.alarm_message = 'the proxy service is stopped'
                                        sal.alarm_level = 'critical'
                                        sal.alarm_result = '0'
                                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                        db.session.add(sal)
                                        db.session.commit()
                                # for net width
                                host = db.session.query(SfoHostInfo).filter(SfoHostInfo.host_name == node.node_host_name).order_by(SfoHostInfo.add_time.desc()).first()
                                if host and util.datediff_seconds(host.add_time, nowtime) < 500:
                                    if host.net_ip_address:
                                        ips = json.loads(host.net_ip_address, encoding='UTF-8')
                                        if isinstance(ips, dict):
                                            netsps = json.loads(host.net_speed, encoding='UTF-8')
                                            reg_exp = config.host_ip_prefix + '.[0-9]+.*'
                                            for net_key in ips.keys():
                                                if not re.match(reg_exp, str(ips[net_key])):
                                                    continue
                                                if ips[net_key] == re.match(reg_exp, str(ips[net_key])).group(0):
                                                    if netsps and netsps.has_key(net_key):
                                                        if str(netsps[net_key]).replace('Mb/s', '').strip().isdigit():
                                                            nettotal += int(str(netsps[net_key]).replace('Mb/s', '').strip())
                                                    else:
                                                        nettotal += 1000
                                                    # net used
                                                    hoststat = db.session.query(SfoNodeStat).filter(SfoNodeStat.host_name == node.node_host_name).order_by(SfoNodeStat.add_time.desc())[1:3]
                                                    if hoststat and len(hoststat) == 2:
                                                        time_interval = util.datediff_seconds(hoststat[1].add_time,hoststat[0].add_time)
                                                        recv_bytes_min = json.loads(hoststat[1].net_recv_bytes,encoding='UTF-8')
                                                        recv_bytes_max = json.loads(hoststat[0].net_recv_bytes,encoding='UTF-8')
                                                        if recv_bytes_max.has_key(net_key) and recv_bytes_min.has_key(net_key):
                                                            if str(recv_bytes_max[net_key]).isdigit() and str(recv_bytes_min[net_key]).isdigit():
                                                                rbytes = abs(int(recv_bytes_max[net_key]) - int(recv_bytes_min[net_key]))
                                                                if time_interval > 0:
                                                                    netused += round(rbytes / time_interval / 1024 / 1024 * 8, 4)
                                                                else:
                                                                    netused += 0
                            if role.has_key('Account-Server') and role['Account-Server'] == 'YES':
                                anum += 1
                                if nodestat and util.datediff_seconds(nodestat.add_time, nowtime) < 180:
                                    if str(nodestat.srv_account).strip().upper() == 'RUNNING':
                                        anumonline += 1
                                    else:
                                        sal = SfoAlarmLog()
                                        sal.guid = str(uuid.uuid1())
                                        sal.alarm_device = "account-service-{}".format(str(nodestat.host_name))
                                        sal.alarm_type = 'software'
                                        sal.hostname = nodestat.host_name
                                        sal.device_name = 'account service'
                                        sal.alarm_message = 'the account service is stopped'
                                        sal.alarm_level = 'critical'
                                        sal.alarm_result = '0'
                                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                        db.session.add(sal)
                                        db.session.commit()
                            if role.has_key('Container-Server') and role['Container-Server'] == 'YES':
                                cnum += 1
                                if nodestat and util.datediff_seconds(nodestat.add_time, nowtime) < 180:
                                    if str(nodestat.srv_container).strip().upper() == 'RUNNING':
                                        cnumonline += 1
                                    else:
                                        sal = SfoAlarmLog()
                                        sal.guid = str(uuid.uuid1())
                                        sal.alarm_device = "container-service-{}".format(str(nodestat.host_name))
                                        sal.alarm_type = 'software'
                                        sal.hostname = nodestat.host_name
                                        sal.device_name = 'container service'
                                        sal.alarm_message = 'the container service is stopped'
                                        sal.alarm_level = 'critical'
                                        sal.alarm_result = '0'
                                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                        db.session.add(sal)
                                        db.session.commit()
                            if role.has_key('Object-Server') and role['Object-Server'] == 'YES':
                                onum += 1
                                if nodestat and util.datediff_seconds(nodestat.add_time, nowtime) < 180:
                                    if str(nodestat.srv_object).strip().upper() == 'RUNNING':
                                        onumonline += 1
                                    else:
                                        sal = SfoAlarmLog()
                                        sal.guid = str(uuid.uuid1())
                                        sal.alarm_device = "object-service-{}".format(str(nodestat.host_name))
                                        sal.alarm_type = 'software'
                                        sal.hostname = nodestat.host_name
                                        sal.device_name = 'object service'
                                        sal.alarm_message = 'the object service is stopped'
                                        sal.alarm_level = 'critical'
                                        sal.alarm_result = '0'
                                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                        db.session.add(sal)
                                        db.session.commit()
                                # for net width
                                host = db.session.query(SfoHostInfo).filter(SfoHostInfo.host_name == node.node_host_name).order_by(SfoHostInfo.add_time.desc()).first()
                                if host and util.datediff_seconds(host.add_time, nowtime) < 500:
                                    if host.net_ip_address:
                                        ips = json.loads(host.net_ip_address, encoding='UTF-8')
                                        if isinstance(ips, dict):
                                            netsps = json.loads(host.net_speed, encoding='UTF-8')
                                            reg_obj_exp = config.host_ip_prefix + '.[0-9]+.*'
                                            for netkey in ips.keys():
                                                if not re.match(reg_obj_exp, str(ips[netkey])):
                                                    continue
                                                if ips[netkey] == re.match(reg_obj_exp, str(ips[netkey])).group(0):
                                                    if netsps and netsps.has_key(netkey):
                                                        if str(netsps[netkey]).replace('Mb/s', '').strip().isdigit():
                                                            obj_nettotal += int(str(netsps[netkey]).replace('Mb/s', '').strip())
                                                    else:
                                                        nettotal += 1000
                                            reg_exp = config.node_ip_prefix + '.[0-9]+.*'
                                            for net_key in ips.keys():
                                                if not re.match(reg_exp, str(ips[net_key])):
                                                    continue
                                                if ips[net_key] == re.match(reg_exp, str(ips[net_key])).group(0):
                                                    if netsps and netsps.has_key(net_key):
                                                        if str(netsps[net_key]).replace('Mb/s', '').strip().isdigit():
                                                            netreptotal = int(str(netsps[net_key]).replace('Mb/s', '').strip())
                                                    else:
                                                        netreptotal = 1000
                                                    # net rep used
                                                    hoststat = SfoNodeStat.query.filter(SfoNodeStat.host_name == node.node_host_name).order_by(SfoNodeStat.add_time.desc())[1:3]
                                                    if hoststat and len(hoststat) == 2:
                                                        time_interval = util.datediff_seconds(hoststat[1].add_time,hoststat[0].add_time)
                                                        recv_bytes_min = json.loads(hoststat[1].net_recv_bytes,encoding='UTF-8')
                                                        recv_bytes_max = json.loads(hoststat[0].net_recv_bytes,encoding='UTF-8')
                                                        if recv_bytes_max.has_key(net_key) and recv_bytes_min.has_key(net_key):
                                                            if str(recv_bytes_max[net_key]).isdigit() and str(
                                                                    recv_bytes_min[net_key]).isdigit():
                                                                rbytes = abs(int(recv_bytes_max[net_key]) - int(recv_bytes_min[net_key]))
                                                                if time_interval > 0:
                                                                    rep_used = round(rbytes / time_interval / 1024 / 1024 * 8, 4)
                                                                else:
                                                                    rep_used = 0
                                                                if rep_used > netrepused:
                                                                    netrepused = rep_used
                                # for disks capacity
                                sql = "SELECT * FROM (select * from sfo_disk_perform_data WHERE host_name='{}'and disk_total<>0 ORDER BY add_time DESC limit 50) t group by disk_name".format(node.node_host_name)
                                disks = db.session.query(SfoDiskPerform).from_statement(sql)
                                if disks:
                                    for disk in disks:
                                        if not disk:
                                            continue
                                        # if 'sda' not in disk.disk_name:  # 过滤掉系统盘符
                                        if int(disk.disk_total) != 0:
                                            disknum += 1
                                            disktotal += int(disk.disk_total)
                                            diskused += int(disk.disk_used)
                                            diskfree += int(disk.disk_free)
                                db.session.commit()
                            # for recon data auditor
                            recon = db.session.query(SfoNodePerform).filter(SfoNodePerform.host_name == node.node_host_name).order_by(SfoNodePerform.add_time.desc()).first()
                            db.session.expunge_all()
                            if recon and util.datediff_seconds(recon.add_time, nowtime) < 180:
                                if util.is_json(recon.account_auditor):
                                    a_rec = json.loads(recon.account_auditor, encoding="UTF-8")
                                    if a_rec.has_key('account_audits_passed'):
                                        if str(a_rec['account_audits_passed']).isdigit():
                                            arec_pass_num += int(a_rec['account_audits_passed'])
                                    if a_rec.has_key('account_audits_failed'):
                                        if str(a_rec['account_audits_failed']).isdigit():
                                            arec_fail_num += int(a_rec['account_audits_failed'])
                                if util.is_json(recon.container_auditor):
                                    c_rec = json.loads(recon.container_auditor, encoding="UTF-8")
                                    if c_rec.has_key('container_audits_passed'):
                                        if str(c_rec['container_audits_passed']).isdigit():
                                            crec_pass_num += int(c_rec['container_audits_passed'])
                                    if c_rec.has_key('container_audits_failed'):
                                        if str(c_rec['container_audits_failed']).isdigit():
                                            crec_fail_num += int(c_rec['container_audits_failed'])
                                if util.is_json(recon.object_auditor):
                                    o_rec = json.loads(recon.object_auditor, encoding="UTF-8")
                                    if o_rec.has_key('object_auditor_stats_ALL'):
                                        if o_rec['object_auditor_stats_ALL']:
                                            tmprec = o_rec['object_auditor_stats_ALL']
                                            if tmprec.has_key('passes'):
                                                if str(tmprec['passes']).isdigit():
                                                    orec_pass_num += int(tmprec['passes'])
                                            if tmprec.has_key('errors'):
                                                if str(tmprec['errors']).isdigit():
                                                    orec_err_num += int(tmprec['errors'])
                                            if tmprec.has_key('quarantined'):
                                                if str(tmprec['quarantined']).isdigit():
                                                    orec_qua_num += int(tmprec['quarantined'])
                                if util.is_json(recon.account_replication):
                                    a_rep = json.loads(recon.account_replication, encoding="UTF-8")
                                    if a_rep.has_key('replication_stats'):
                                        if a_rep['replication_stats']:
                                            trep = a_rep['replication_stats']
                                            if trep.has_key('no_change'):
                                                if str(trep['no_change']).isdigit():
                                                    arep_no_change_num += int(trep['no_change'])
                                            if trep.has_key('success'):
                                                if str(trep['success']).isdigit():
                                                    arep_suc_num += int(trep['success'])
                                            if trep.has_key('failure'):
                                                if str(trep['failure']).isdigit():
                                                    arep_fail_num += int(trep['failure'])
                                if util.is_json(recon.container_replication):
                                    c_rep = json.loads(recon.container_replication, encoding="UTF-8")
                                    if c_rep.has_key('replication_stats'):
                                        if c_rep['replication_stats']:
                                            trep = c_rep['replication_stats']
                                            if trep.has_key('no_change'):
                                                if str(trep['no_change']).isdigit():
                                                    crep_no_change_num += int(trep['no_change'])
                                            if trep.has_key('success'):
                                                if str(trep['success']).isdigit():
                                                    crep_suc_num += int(trep['success'])
                                            if trep.has_key('failure'):
                                                if str(trep['failure']).isdigit():
                                                    crep_fail_num += int(trep['failure'])
                                if util.is_json(recon.object_replication):
                                    o_rep = json.loads(recon.object_replication, encoding="UTF-8")
                                    if o_rep.has_key('replication_stats'):
                                        if o_rep['replication_stats']:
                                            trep = o_rep['replication_stats']
                                            if trep.has_key('remove'):
                                                if str(trep['remove']).isdigit():
                                                    orep_remove_num += int(trep['remove'])
                                            if trep.has_key('success'):
                                                if str(trep['success']).isdigit():
                                                    orep_suc_num += int(trep['success'])
                                            if trep.has_key('failure'):
                                                if str(trep['failure']).isdigit():
                                                    orep_fail_num += int(trep['failure'])
                                if util.is_json(recon.container_updater):
                                    ctime = json.loads(recon.container_updater, encoding="UTF-8")
                                    if ctime.has_key('container_updater_sweep'):
                                        if ctime['container_updater_sweep']:
                                            cup_times += round(float(ctime['container_updater_sweep']) * 1000.0, 2)
                                if util.is_json(recon.object_updater):
                                    otime = json.loads(recon.object_updater, encoding="UTF-8")
                                    if otime.has_key('object_updater_sweep'):
                                        if otime['object_updater_sweep']:
                                            oup_times += round(float(otime['object_updater_sweep']) * 1000.0, 2)
                                if recon.async_pending:
                                    if str(recon.async_pending).isdigit():
                                        rec_sync_num += int(recon.async_pending)
                            # for statsd data
                            # uri data from proxy statsd
                            if statd_proxy and util.datediff_seconds(statd_proxy.add_time, nowtime) < 180:
                                if statd_proxy.req_auth_unauthorized:
                                    if str(statd_proxy.req_auth_unauthorized).isdigit():
                                        uri_fail_num += int(statd_proxy.req_auth_unauthorized)
                                if statd_proxy.req_auth_forbidden:
                                    if str(statd_proxy.req_auth_forbidden).isdigit():
                                        uri_fail_num += int(statd_proxy.req_auth_forbidden)
                                if statd_proxy.req_auth_token_denied:
                                    if str(statd_proxy.req_auth_token_denied).isdigit():
                                        uri_fail_num += int(statd_proxy.req_auth_token_denied)
                                if statd_proxy.req_auth_errors:
                                    if str(statd_proxy.req_auth_errors).isdigit():
                                        uri_fail_num += int(statd_proxy.req_auth_errors)
                                # total request number
                                if statd_proxy.req_timing:
                                    if util.is_json(statd_proxy.req_timing):
                                        req_rec = json.loads(statd_proxy.req_timing, encoding="UTF-8")
                                        if isinstance(req_rec, dict):
                                            for key in req_rec.keys():
                                                if req_rec[key]:
                                                    tmp_val = req_rec[key]
                                                    if str(node.node_host_name).upper() in str(key).upper():
                                                        if tmp_val.has_key('count_ps'):
                                                            uri_total_num += tmp_val['count_ps']
                                                            suc = re.findall('\.20\[0-9\]\.', str(key))
                                                            if len(suc) > 0:
                                                                uri_suc_num += tmp_val['count_ps']
                        sci.uri_total = str(uri_total_num)
                        sci.uri_success_num = str(uri_suc_num)
                        sci.uri_fail_num = str(uri_fail_num)
                        sci.uri_response_time = '0'

                        rec_auditor['account_audits_passed'] = arec_pass_num
                        rec_auditor['account_audits_failed'] = arec_fail_num
                        rec_auditor['container_audits_passed'] = crec_pass_num
                        rec_auditor['container_audits_failed'] = crec_fail_num
                        rec_auditor['object_auditor_passed'] = orec_pass_num
                        rec_auditor['object_auditor_errors'] = orec_err_num
                        rec_auditor['object_auditor_quarantined'] = orec_qua_num
                        rec_replicater['account_replication_no_change'] = arep_no_change_num
                        rec_replicater['account_replication_success'] = arep_suc_num
                        rec_replicater['account_replication_failure'] = arep_fail_num
                        rec_replicater['container_replication_no_change'] = crep_no_change_num
                        rec_replicater['container_replication_success'] = crep_suc_num
                        rec_replicater['container_replication_failure'] = crep_fail_num
                        rec_replicater['object_replication_success'] = orep_suc_num
                        rec_replicater['object_replication_failure'] = orep_fail_num
                        rec_replicater['object_replication_remove'] = orep_remove_num
                        rec_updater['container_updater_sweep'] = cup_times
                        rec_updater['object_updater_sweep'] = oup_times
                        pnum['proxy_total'] = pnumtotal
                        pnum['proxy_online'] = pnumonline
                        stgnum['account_num'] = anum
                        stgnum['account_online'] = anumonline
                        stgnum['container_num'] = cnum
                        stgnum['container_online'] = cnumonline
                        stgnum['object_num'] = onum
                        stgnum['object_online'] = onumonline
                        sci.proxy_num = json.dumps(pnum, encoding="UTF-8", ensure_ascii=True)
                        sci.storage_num = json.dumps(stgnum, encoding="UTF-8", ensure_ascii=True)
                        sci.disk_num = str(disknum)
                        diskcapacity['disk_total'] = '%d' % (disktotal * 0.88)
                        diskcapacity['disk_used'] = '%d' % (diskused * 0.88)
                        diskcapacity['disk_free'] = '%d' % (diskfree * 0.88)
                        if float(disktotal) - 0.0 > 0:
                            if float(diskused) / float(disktotal) - 0.5 > 0:
                                sal = SfoAlarmLog()
                                sal.guid = str(uuid.uuid1())
                                sal.alarm_device = "cluster-capacity-{}".format(str(row.cluster_name))
                                sal.alarm_type = 'software'
                                sal.hostname = row.cluster_name
                                sal.device_name = 'cluster capacity'
                                sal.alarm_message = 'the cluster capacity is used more than 50 percent'
                                sal.alarm_level = 'critical'
                                sal.alarm_result = '0'
                                sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                db.session.add(sal)
                                db.session.commit()
                        sci.capacity_total = json.dumps(diskcapacity, encoding="UTF-8", ensure_ascii=True)
                        if obj_nettotal - nettotal < 0:
                            netinfo['band_total'] = obj_nettotal
                        else:
                            netinfo['band_total'] = nettotal
                        netinfo['band_used'] = '%.2f' % netused
                        netinfo['band_rep_total'] = netreptotal
                        netinfo['band_rep_used'] = '%.2f' % netrepused
                        sci.band_width = json.dumps(netinfo, encoding="UTF-8", ensure_ascii=True)
                        iops = '%.2f' % (175 * int(disknum) * 10 / 16)
                        sci.cluster_iops = str(iops)
                        # account container object Quantitative statistics
                        acclist = db.session.query(SfoAccountManager).filter(and_(SfoAccountManager.cluster_name == row.cluster_name,SfoAccountManager.account_stat == '1')).all()
                        db.session.expunge_all()
                        if not acclist:
                            sci.account_num = '0'
                            sci.container_num = '0'
                            sci.object_num = '0'
                        else:
                            sci.account_num = str(len(acclist))
                            concounter = 0
                            objcounter = 0
                            for acc in acclist:
                                try:
                                    (storage_url, auth_token) = client.get_auth(acc.auth_url,"{}:{}".format(acc.account_id,acc.system_user),acc.system_passwd, auth_version=1)
                                    account_stat, containers = client.get_account(acc.storage_url, auth_token)
                                    if str(account_stat['x-account-container-count']).isdigit():
                                        concounter += int(account_stat['x-account-container-count'])
                                    else:
                                        concounter += 0
                                    if str(account_stat['x-account-object-count']).isdigit():
                                        objcounter += int(account_stat['x-account-object-count'])
                                    else:
                                        objcounter += 0
                                    sysuse = {}
                                    sysuse['account-used'] = account_stat['x-account-bytes-used']
                                    if type(eval(str(acc.system_capacity))) == int or type(eval(str(acc.system_capacity))) == float:
                                        if float(acc.system_capacity) > 0:
                                            if float(account_stat['x-account-bytes-used']) / float(acc.system_capacity) - 0.8 > 0:
                                                sal = SfoAlarmLog()
                                                sal.guid = str(uuid.uuid1())
                                                sal.alarm_device = "account-uesd-{}".format(str(acc.account_id))
                                                sal.alarm_type = 'software'
                                                sal.hostname = acc.account_id
                                                sal.device_name = 'account capacity used'
                                                sal.alarm_message = 'the account capacity is used more than 80 percent'
                                                sal.alarm_level = 'critical'
                                                sal.alarm_result = '0'
                                                sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                                db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                                db.session.add(sal)
                                                db.session.commit()
                                    if containers:
                                        if len(containers) - 10000 > 0:
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "container-number-{}".format(str(acc.account_id))
                                            sal.alarm_type = 'cluster'
                                            sal.hostname = acc.account_id
                                            sal.device_name = 'container number'
                                            sal.alarm_message = 'this account has more than 10000 containers'
                                            sal.alarm_level = 'warning'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        for ctn in containers:
                                            sysuse[ctn['name']] = ctn['bytes']
                                            if str(ctn['count']).isdigit():
                                                if int(ctn['count']) - 50000000 > 0:
                                                    sal = SfoAlarmLog()
                                                    sal.guid = str(uuid.uuid1())
                                                    sal.alarm_device = "object-number-{}:{}".format(str(acc.account_id),str(ctn['name']))
                                                    sal.alarm_type = 'cluster'
                                                    sal.hostname = '{}:{}'.format(str(acc.account_id), str(ctn['name']))
                                                    sal.device_name = 'object number'
                                                    sal.alarm_message = 'this container has more than 50000000 objects'
                                                    sal.alarm_level = 'warning'
                                                    sal.alarm_result = '0'
                                                    sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                                    db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                                    db.session.add(sal)
                                                    db.session.commit()
                                    acc.system_used = json.dumps(sysuse, encoding="UTF-8", ensure_ascii=True)
                                    db.session.add(acc)
                                    db.session.commit()
                                except Exception as ex:
                                    logger.info('account {} auth failed.exception:{}'.format(acc.system_user, str(ex)))
                            sci.container_num = str(concounter)
                            sci.object_num = str(objcounter)

                        sci.auditor_queue = json.dumps(rec_auditor, encoding="UTF-8", ensure_ascii=True)
                        sci.replicate_num = json.dumps(rec_replicater, encoding="UTF-8", ensure_ascii=True)
                        sci.update_num = json.dumps(rec_updater, encoding="UTF-8", ensure_ascii=True)
                        sci.sync_num = str(rec_sync_num)
                        sci.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        if not sci.guid:
                            sci.guid = str(uuid.uuid1())
                        if sci.cluster_name is None:
                            sci.cluster_name = config.swift_cluster_name
                        if type(eval(str(sci.sync_num))) == int:
                            if int(sci.sync_num) - 2000 > 0:
                                sal = SfoAlarmLog()
                                sal.guid = str(uuid.uuid1())
                                sal.alarm_device = "async-pending-{}".format(str(row.cluster_name))
                                sal.alarm_type = 'software'
                                sal.hostname = row.cluster_name
                                sal.device_name = 'async pending'
                                sal.alarm_message = 'the cluster async pending was {},it`s more than 2000.'.format(str(sci.sync_num))
                                sal.alarm_level = 'critical'
                                sal.alarm_result = '0'
                                sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                db.session.add(sal)
                                db.session.commit()
                        db.session.add(sci)
                        db.session.commit()
                    except Exception as e:
                        logger.info("cluster {} info get exception:{}".format(row.cluster_name, str(e)))
        except Exception as ex:
            logger.info("get_cluster_info function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()

    def expire_data_rows(self):
        '''
        定时删除数据库中不需要保留的数据，以免数据过多影响性能
        每种数据保存时间可自行调整
        :return:
        '''
        try:
            # one hour
            l_time = datetime.datetime.now() + datetime.timedelta(hours=-1)
            l_time_str = l_time.strftime('%Y-%m-%d %H:%M:%S')
            # SfoDiskPerform
            db.session.query(SfoDiskPerform).filter(SfoDiskPerform.add_time < l_time_str).delete()
            # SfoHostMonitor
            db.session.query(SfoHostMonitor).filter(SfoHostMonitor.add_time < l_time_str).delete()
            # SfoHostInfo
            db.session.query(SfoHostInfo).filter(SfoHostInfo.add_time < l_time_str).delete()
            # one day
            yes_time = datetime.datetime.now() + datetime.timedelta(days=-1)
            yes_time_str = yes_time.strftime('%Y-%m-%d %H:%M:%S')
            # SfoNodePerform
            db.session.query(SfoNodePerform).filter(SfoNodePerform.add_time < yes_time_str).delete()
            # SfoNodeService
            db.session.query(SfoNodeService).filter(SfoNodeService.add_time < yes_time_str).delete()
            # SfoNodeStat
            db.session.query(SfoNodeStat).filter(SfoNodeStat.add_time < yes_time_str).delete()
            # BeatHeart
            db.session.query(BeatHeartInfo).filter(BeatHeartInfo.add_time < yes_time_str).delete()
            # statsD
            db.session.query(SfoStatsD).filter(SfoStatsD.add_time < yes_time_str).delete()
            # proxy statsD
            db.session.query(SfoProxyStatsD).filter(SfoProxyStatsD.add_time < yes_time_str).delete()
            # account statsD
            db.session.query(SfoAccountStatsD).filter(SfoAccountStatsD.add_time < yes_time_str).delete()
            # container statsD
            db.session.query(SfoContainerStatsD).filter(SfoContainerStatsD.add_time < yes_time_str).delete()
            # object statsD
            db.session.query(SfoObjectStatsD).filter(SfoObjectStatsD.add_time < yes_time_str).delete()
            # SfoClusterInfo
            db.session.query(SfoClusterInfo).filter(SfoClusterInfo.add_time < yes_time_str).delete()
            # SfoHostRing
            db.session.query(SfoHostRing).filter(SfoHostRing.add_time < yes_time_str).delete()
            # seven day
            last_time = datetime.datetime.now() + datetime.timedelta(days=-8)
            last_time_str = last_time.strftime('%Y-%m-%d %H:%M:%S')
            # rep data
            db.session.query(SfoPartitionsInfo).filter(SfoPartitionsInfo.update_time < last_time_str).delete()
            db.session.commit()
        except Exception as ex:
            logger.info("expire_data_rows function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()

    # 数据归档
    def data_archive_5min(self):
        '''
        5分钟数据归档
        :return:
        '''
        try:
            da = DataArchiving()
            rows = db.session.query(SfoCluster).all()
            db.session.expunge_all()
            if not rows or len(rows) == 0:
                pass
            else:
                for row in rows:
                    nodes = db.session.query(SfoClusterNodes).filter(and_(SfoClusterNodes.cluster_name == row.cluster_name,SfoClusterNodes.node_stat == '1')).all()
                    db.session.expunge_all()
                    if nodes:
                        # 启动线程池
                        with ThreadPoolExecutor(5) as executor:
                            for node in nodes:
                                # 多线程执行
                                # executor.map()  如果需要保证顺序就用map
                                executor.submit(da.nodestat_data_archiving,(node.node_host_name, SfoNodeStat, SfoNodeStat_5min, 'minutes'))
                                executor.submit(da.diskperform_data_archiving, (node.node_host_name, SfoDiskPerform, SfoDiskPerform_5min, 'minutes'))
                                executor.submit(da.nodeperform_data_archiving, (node.node_host_name, SfoNodePerform, SfoNodePerform_5min, 'minutes'))
                                executor.submit(da.nodesrv_data_archiving, (node.node_host_name, SfoNodeService, SfoNodeService_5min, 'minutes'))
                                executor.submit(da.hostmon_data_archiving, (node.node_host_name, SfoHostMonitor, SfoHostMonitor_5min, 'minutes'))
                    else:
                        pass
            # 多线程执行
            with ThreadPoolExecutor(5) as executor1:
                executor1.submit(da.statsd_data_archiving, (SfoStatsD, SfoStatsD_5min, 'minutes'))
                executor1.submit(da.proxystatsd_data_archiving, (SfoProxyStatsD, SfoProxyStatsD_5min, 'minutes'))
                executor1.submit(da.objectstatsd_data_archiving, (SfoObjectStatsD, SfoObjectStatsD_5min, 'minutes'))
                executor1.submit(da.containerstatsd_data_archiving,(SfoContainerStatsD, SfoContainerStatsD_5min, 'minutes'))
                executor1.submit(da.accountstatsd_data_archiving,(SfoAccountStatsD, SfoAccountStatsD_5min, 'minutes'))
            db.session.commit()
        except Exception as ex:
            logger.info("data_archive_5min function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()

    def data_archive_hours(self):
        '''
        1小时数据归档，数据来源于5分钟表
        :return:
        '''
        try:
            da = DataArchiving()
            # rows = db.session.query(SfoCluster).all()
            rows = SfoCluster.query.filter().all()
            db.session.expunge_all()
            if not rows or len(rows) == 0:
                pass
            else:
                for row in rows:
                    # SfoClusterInfo
                    da.clsinfo_data_archiving(row.cluster_name, SfoClusterInfo, SfoClusterInfo_hour, 'hours')
                    nodes = db.session.query(SfoClusterNodes).filter(
                        and_(SfoClusterNodes.cluster_name == row.cluster_name, SfoClusterNodes.node_stat == '1')).all()
                    db.session.expunge_all()
                    if nodes:
                        for node in nodes:
                            da.nodestat_data_archiving(node.node_host_name, SfoNodeStat_5min, SfoNodeStat_hour, 'hours')
                            da.diskperform_data_archiving(node.node_host_name, SfoDiskPerform_5min, SfoDiskPerform_hour,'hours')
                            da.nodeperform_data_archiving(node.node_host_name, SfoNodePerform_5min, SfoNodePerform_hour,'hours')
                            da.nodesrv_data_archiving(node.node_host_name, SfoNodeService_5min, SfoNodeService_hour,'hours')
                            da.hostmon_data_archiving(node.node_host_name, SfoHostMonitor_5min, SfoHostMonitor_hour,'hours')
                    else:
                        pass
            da.statsd_data_archiving(SfoStatsD_5min, SfoStatsD_hour, 'hours')
            da.proxystatsd_data_archiving(SfoProxyStatsD_5min, SfoProxyStatsD_hour, 'hours')
            da.objectstatsd_data_archiving(SfoObjectStatsD_5min, SfoObjectStatsD_hour, 'hours')
            da.containerstatsd_data_archiving(SfoContainerStatsD_5min, SfoContainerStatsD_hour, 'hours')
            da.accountstatsd_data_archiving(SfoAccountStatsD_5min, SfoAccountStatsD_hour, 'hours')
            db.session.commit()
        except Exception as ex:
            logger.info("data_archive_hours function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()

    def data_archive_days(self):
        '''
        按天数据归档,数据来源于小时表
        :return:
        '''
        try:
            da = DataArchiving()
            rows = db.session.query(SfoCluster).all()
            db.session.expunge_all()
            if not rows or len(rows) == 0:
                pass
            else:
                for row in rows:
                    da.clsinfo_data_archiving(row.cluster_name, SfoClusterInfo_hour, SfoClusterInfo_day, 'days')
                    nodes = db.session.query(SfoClusterNodes).filter(
                        and_(SfoClusterNodes.cluster_name == row.cluster_name, SfoClusterNodes.node_stat == '1')).all()
                    db.session.expunge_all()
                    if nodes:
                        for node in nodes:
                            da.nodestat_data_archiving(node.node_host_name, SfoNodeStat_hour, SfoNodeStat_day, 'days')
                            da.diskperform_data_archiving(node.node_host_name, SfoDiskPerform_hour, SfoDiskPerform_day,'days')
                            da.nodeperform_data_archiving(node.node_host_name, SfoNodePerform_hour, SfoNodePerform_day,'days')
                            da.nodesrv_data_archiving(node.node_host_name, SfoNodeService_hour, SfoNodeService_day,'days')
                            da.hostmon_data_archiving(node.node_host_name, SfoHostMonitor_hour, SfoHostMonitor_day,'days')
                    else:
                        pass
            da.statsd_data_archiving(SfoStatsD_hour, SfoStatsD_day, 'days')
            da.proxystatsd_data_archiving(SfoProxyStatsD_hour, SfoProxyStatsD_day, 'days')
            da.objectstatsd_data_archiving(SfoObjectStatsD_hour, SfoObjectStatsD_day, 'days')
            da.containerstatsd_data_archiving(SfoContainerStatsD_hour, SfoContainerStatsD_day, 'days')
            da.accountstatsd_data_archiving(SfoAccountStatsD_hour, SfoAccountStatsD_day, 'days')
            db.session.commit()
        except Exception as ex:
            logger.info("data_archive_days function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()


class BackStageTask(object):
    '''
    后台任务类
    '''
    def __init__(self):
        pass

    def check_swift_service(self, cluster_name, service_name):
        '''
        检查集群中指定服务的运行状态
        循环处理集群中所有节点，有一个节点异常，即返回异常
        :param cluster_name:
        :param service_name:
        :return:
        '''
        result = "OK"
        remark = ""
        status = True
        try:
            cluster_nodes = db.session.query(SfoClusterNodes).filter(and_(SfoClusterNodes.cluster_name == cluster_name, SfoClusterNodes.node_stat == '1')).all()
            db.session.expunge_all()
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            for node in cluster_nodes:
                roles = json.loads(node.node_role, encoding='UTF-8')
                nodeserv = SfoNodeService.query.filter(SfoNodeService.host_name == node.node_host_name).order_by(SfoNodeService.add_time.desc()).first()
                db.session.expunge_all()
                if nodeserv and util.datediff_seconds(nodeserv.add_time, nowtime) < 300:
                    if hasattr(nodeserv, service_name):
                        if 'account' in service_name and roles.has_key('Account-Server') and roles['Account-Server'] == 'YES':
                            if str(getattr(nodeserv, service_name)).strip().upper() == "RUNNING":
                                status = status and True
                            else:
                                status = status and False
                                remark += "{} Failed;".format(nodeserv.host_name)
                        elif 'container' in service_name and roles.has_key('Container-Server') and roles['Container-Server'] == 'YES':
                            if str(getattr(nodeserv, service_name)).strip().upper() == "RUNNING":
                                status = status and True
                            else:
                                status = status and False
                                remark += "{} Failed;".format(nodeserv.host_name)
                        elif 'object' in service_name and roles.has_key('Object-Server') and roles['Object-Server'] == 'YES':
                            if str(getattr(nodeserv, service_name)).strip().upper() == "RUNNING":
                                status = status and True
                            else:
                                status = status and False
                                remark += "{} Failed;".format(nodeserv.host_name)
                        elif 'proxy' in service_name and roles.has_key('Proxy-Server') and roles['Proxy-Server'] == 'YES':
                            if str(getattr(nodeserv, service_name)).strip().upper() == "RUNNING":
                                status = status and True
                            else:
                                status = status and False
                                remark += "{} Failed;".format(nodeserv.host_name)
                        else:
                            pass
                    else:
                        status = status and False
                        result = "Error"
                        remark += "{} Error;".format(nodeserv.host_name)
                else:
                    status = status and False
                    result = "Exception"
                    remark += "{} Exception;".format(nodeserv.host_name)
        except Exception as ex:
            logger.info("check_service function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()
            if not status:
                result = "Warning"
            return result, remark

    def check_os_service(self, cluster_name, service_name):
        '''
        检查主机上swift依赖服务状态
        按集群循环处理所有节点，有一个节点异常视为异常
        :param cluster_name:
        :param service_name:
        :return:
        '''
        result = "OK"
        remark = ""
        status = True
        try:
            cluster_nodes = db.session.query(SfoClusterNodes).filter(and_(SfoClusterNodes.cluster_name == cluster_name, SfoClusterNodes.node_stat == '1')).all()
            db.session.expunge_all()
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            for node in cluster_nodes:
                roles = json.loads(node.node_role, encoding='UTF-8')
                os_services = db.session.query(SfoHostMonitor).filter(SfoHostMonitor.host_name == node.node_host_name).order_by(SfoHostMonitor.add_time.desc()).first()
                db.session.expunge_all()
                if os_services and util.datediff_seconds(os_services.add_time, nowtime) < 300:
                    if util.is_json(os_services.extend):
                        services = json.loads(os_services.extend, encoding='UTF-8')
                        if services.has_key(service_name):
                            # if hasattr(os_services,service_name):
                            if 'ntpd' in service_name:
                                if str(services['ntpd']).strip().upper() == "RUNNING":
                                    status = status and True
                                else:
                                    status = status and False
                                    remark += "{} Failed;".format(os_services.host_name)
                            elif 'memcached' in service_name and roles.has_key('Proxy-Server') and roles['Proxy-Server'] == 'YES':
                                if str(services['memcached']).strip().upper() == "RUNNING":
                                    status = status and True
                                else:
                                    status = status and False
                                    remark += "{} Failed;".format(os_services.host_name)
                            elif 'rsyncd' in service_name and roles.has_key('Object-Server') and roles['Object-Server'] == 'YES':
                                if str(services['rsyncd']).strip().upper() == "RUNNING":
                                    status = status and True
                                else:
                                    status = status and False
                                    remark += "{} Failed;".format(os_services.host_name)
                            else:
                                pass
                        else:
                            status = status and False
                            result = "NoService"
                            remark += "{} no service;".format(os_services.host_name)
                    else:
                        status = status and False
                        result = "NULL"
                        remark += "{} null;".format(os_services.host_name)
                else:
                    status = status and False
                    result = "Timeout"
                    remark += "{} timeout;".format(node.node_host_name)
        except Exception as ex:
            logger.info("check_os_service function excute exception:" + str(ex))
            result = "Exception"
            remark += "{} Exception;".format(cluster_name)
        finally:
            db.session.close()
            db.session.remove()
            return result, remark

    def check_host_monitor(self, cluster_name, mon_item, value):
        '''
        集群节点监控
        根据指定项和目标值对集群中所有节点进行比较，有一个节点异常即视为异常
        :param cluster_name:
        :param mon_item:
        :param value:
        :return:
        '''
        result = "OK"
        remark = ""
        status = True
        try:
            cluster_nodes = db.session.query(SfoClusterNodes).filter(and_(SfoClusterNodes.cluster_name == cluster_name, SfoClusterNodes.node_stat == '1')).all()
            db.session.expunge_all()
            for node in cluster_nodes:
                nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                host_mon = db.session.query(SfoHostMonitor).filter(SfoHostMonitor.host_name == node.node_host_name).order_by(
                    SfoHostMonitor.add_time.desc()).first()
                db.session.expunge_all()
                if host_mon and util.datediff_seconds(host_mon.add_time, nowtime) < 300:
                    if hasattr(host_mon, mon_item):
                        tmp_val = str(getattr(host_mon, mon_item)).strip()
                        if type(eval(tmp_val)) == int or type(eval(tmp_val)) == float:
                            if abs(float(tmp_val)) - value > 0:
                                status = status and False
                                remark += "{} Warning;".format(host_mon.host_name)
                            else:
                                status = status and True
                    else:
                        extend = json.loads(host_mon.extend, encoding="UTF-8")
                        if extend.has_key(mon_item):
                            tmp_val = str(extend[mon_item]).strip()
                            if type(eval(tmp_val)) == int or type(eval(tmp_val)) == float:
                                if abs(float(tmp_val)) - value > 0:
                                    status = status and False
                                    remark += "{} Warning;".format(host_mon.host_name)
                                else:
                                    status = status and True
                        else:
                            status = status and False
                            remark += "{} Error;".format(host_mon.host_name)
                else:
                    status = status and False
                    remark += "{} Exception;".format(node.node_host_name)
            db.session.commit()
        except Exception as ex:
            logger.info("check_host_monitor function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()
            if not status:
                result = "Warning"
            return result, remark

    def check_file_md5(self, cluster_name, file_name, value):
        '''
        检查集群中所有节点上指定文件的md5值，与给定的目标值比较
        :param cluster_name:
        :param file_name:
        :param value:
        :return:
        '''
        result = "OK"
        remark = ""
        status = True
        try:
            cluster_nodes = db.session.query(SfoClusterNodes).filter(
                and_(SfoClusterNodes.cluster_name == cluster_name, SfoClusterNodes.node_stat == '1')).all()
            db.session.expunge_all()
            nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            for node in cluster_nodes:
                host_file = db.session.query(SfoHostRing).filter(SfoHostRing.host_name == node.node_host_name).order_by(
                    SfoHostRing.add_time.desc()).first()
                db.session.expunge_all()
                if host_file and util.datediff_seconds(host_file.add_time, nowtime) < 1860:
                    if host_file.extend and util.is_json(host_file.extend):
                        file_md5 = json.loads(host_file.extend, encoding="UTF-8")
                        if file_md5.has_key(file_name):
                            if str(file_md5[file_name]).strip() == value:
                                status = status and True
                            else:
                                status = status and False
                                result = "Error"
                                remark += "{} Error;".format(host_file.host_name)
                    elif host_file.rings_md5 and util.is_json(host_file.rings_md5):
                        file_md5 = json.loads(host_file.rings_md5, encoding="UTF-8")
                        if file_md5.has_key(file_name):
                            if str(file_md5[file_name]).strip() == value:
                                status = status and True
                            else:
                                status = status and False
                                result = "Error"
                                remark += "{} Error;".format(host_file.host_name)
                    else:
                        status = status and False
                        result = "Data Exception"
                        remark += "{} Data Exception;".format(host_file.host_name)
                else:
                    status = status and False
                    result = "Data overtime"
                    remark += "{} Data overtime;".format(node.node_host_name)
            db.session.commit()
        except Exception as ex:
            logger.info("check_file_md5 function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()
            if not status:
                result = "Warning"
            return result, remark

    def add_report_item(self, cluster_name, subject, item, cmd, result, remark):
        '''
        添加巡检项
        :param cluster_name:
        :param subject:
        :param item:
        :param cmd:
        :param result:
        :param remark:
        :return:
        '''
        try:
            report_item = SfoCheckReport()
            report_item.guid = str(uuid.uuid1())
            report_item.cluster_name = cluster_name
            report_item.subject_name = subject
            report_item.item_name = item
            report_item.check_command = cmd
            report_item.check_result = result
            report_item.check_remark = remark
            report_item.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            db.session.add(report_item)
            db.session.commit()
        except Exception as ex:
            logger.exception("add_report_item function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()

    def daily_inspection(self):
        '''
        日常巡检
        :return:
        '''
        try:
            cluster_list = db.session.query(SfoCluster).filter(or_(SfoCluster.cluster_stat == 'public', SfoCluster.cluster_stat == 'dedicated')).all()
            db.session.expunge_all()
            if cluster_list:
                for cluster in cluster_list:
                    # swift服务
                    subject = "swift服务"
                    # object-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_object")
                    self.add_report_item(cluster.cluster_name, subject, "object-server服务状态","systemctl status openstack-swift-object.service", res, mark)
                    # object-replicator-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_object_replicator")
                    self.add_report_item(cluster.cluster_name, subject, "object-replicator-server服务状态","systemctl status openstack-swift-object-replicator.service", res, mark)
                    # object-auditor-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_object_auditor")
                    self.add_report_item(cluster.cluster_name, subject, "object-auditor-server服务状态","systemctl status openstack-swift-object-auditor.service", res, mark)
                    # object-updater-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_object_updater")
                    self.add_report_item(cluster.cluster_name, subject, "object-updater-server服务状态","systemctl status openstack-swift-object-updater.service", res, mark)
                    # account-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_account")
                    self.add_report_item(cluster.cluster_name, subject, "account-server服务状态","systemctl status openstack-swift-account.service", res, mark)
                    # account-replicator-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_account_replicator")
                    self.add_report_item(cluster.cluster_name, subject, "account-replicator-server服务状态","systemctl status openstack-swift-account-replicator.service", res, mark)
                    # account-auditor-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_account_auditor")
                    self.add_report_item(cluster.cluster_name, subject, "account-auditor-server服务状态","systemctl status openstack-swift-account-auditor.service", res, mark)
                    # account-reaper-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_account_reaper")
                    self.add_report_item(cluster.cluster_name, subject, "account-reaper-server服务状态","systemctl status openstack-swift-account-reaper.service", res, mark)
                    # container-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_container")
                    self.add_report_item(cluster.cluster_name, subject, "container-server服务状态","systemctl status openstack-swift-container.service", res, mark)
                    # container-replicator-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_container_replicator")
                    self.add_report_item(cluster.cluster_name, subject, "container-replicator-server服务状态","systemctl status openstack-swift-container-replicator.service", res, mark)
                    # container-auditor-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_container_auditor")
                    self.add_report_item(cluster.cluster_name, subject, "container-auditor-server服务状态","systemctl status openstack-swift-container-auditor.service", res, mark)
                    # container-updater-server服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_container_updater")
                    self.add_report_item(cluster.cluster_name, subject, "container-updater-server服务状态","systemctl status openstack-swift-container-updater.service", res, mark)
                    # swift-proxy服务状态
                    res, mark = self.check_swift_service(cluster.cluster_name, "srv_proxy")
                    self.add_report_item(cluster.cluster_name, subject, "swift-proxy服务状态","systemctl status openstack-swift-proxy.service", res, mark)
                    # OS标准配置
                    subject = "OS标准配置"
                    # NTP同步状态
                    res, mark = self.check_os_service(cluster.cluster_name, "ntpd")
                    self.add_report_item(cluster.cluster_name, subject, "NTP同步状态", "systemctl status ntpd.service", res, mark)
                    # OS时间一致性
                    res, mark = self.check_host_monitor(cluster.cluster_name, "host_ntp_time", 100.0)
                    self.add_report_item(cluster.cluster_name, subject, "OS时间一致性", "ntpq -p", res, mark)
                    # Memcached 服务状态
                    res, mark = self.check_os_service(cluster.cluster_name, "memcached")
                    self.add_report_item(cluster.cluster_name, subject, "Memcached 服务状态", "systemctl status memcached",res, mark)
                    # rsyncd 服务状态
                    res, mark = self.check_os_service(cluster.cluster_name, "rsyncd")
                    self.add_report_item(cluster.cluster_name, subject, "rsyncd 服务状态", "systemctl status rsyncd.service", res, mark)
                    # swift标准配置
                    subject = "swift标准配置"
                    # swift.conf一致性
                    res, mark = self.check_file_md5(cluster.cluster_name, "swift.conf",self.get_target_md5(cluster.cluster_name, 'swift_conf_md5'))
                    self.add_report_item(cluster.cluster_name, subject, "swift.conf一致性", "md5sum /etc/swift/swift.conf",res, mark)
                    # account.ring.gz一致性
                    res, mark = self.check_file_md5(cluster.cluster_name, "account.ring.gz",self.get_target_md5(cluster.cluster_name, 'swift_account_ring_md5'))
                    self.add_report_item(cluster.cluster_name, subject, "account.ring.gz一致性", "md5sum /etc/swift/account.ring.gz", res, mark)
                    # container.ring.gz一致性
                    res, mark = self.check_file_md5(cluster.cluster_name, "container.ring.gz", self.get_target_md5(cluster.cluster_name, 'swift_container_ring_md5'))
                    self.add_report_item(cluster.cluster_name, subject, "container.ring.gz一致性","md5sum /etc/swift/container.ring.gz", res, mark)
                    # object.ring.gz一致性
                    res, mark = self.check_file_md5(cluster.cluster_name, "object.ring.gz",self.get_target_md5(cluster.cluster_name, 'swift_object_ring_md5'))
                    self.add_report_item(cluster.cluster_name, subject, "object.ring.gz一致性", "md5sum /etc/swift/object.ring.gz", res, mark)
                    # passwd一致性
                    res, mark = self.check_file_md5(cluster.cluster_name, "passwdmd5",self.get_target_md5(cluster.cluster_name, 'swift_passwd_md5'))
                    self.add_report_item(cluster.cluster_name, subject, "passwd一致性", "md5sum /etc/swift/passwd", res, mark)
            else:
                logger.info("there is no cluster in the environment")
            db.session.commit()
        except Exception as ex:
            logger.exception("daily_inspection function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()

    def get_target_md5(self, cluster_name, target_file_key):
        '''
        获取集群指定文件的md5目标值
        :param cluster_name:
        :param target_file_key:
        :return:
        '''
        result = ''
        try:
            swift_conf_md5 = db.session.query(SfoCofigure).filter(and_(SfoCofigure.config_group == cluster_name, SfoCofigure.config_key == target_file_key)).first()
            db.session.expunge_all()
            if swift_conf_md5:
                result = str(swift_conf_md5.config_value).strip()
            else:
                result = "targetmd5value"
            db.session.commit()
        except Exception as ex:
            result = "targetmd5value exception is {}".format(str(ex))
        finally:
            db.session.close()
            db.session.remove()
            return result

    def monitoring_alarm(self):
        '''
        监控告警
        15分钟内不再现的自动删除
        :return:
        '''
        try:
            cluster_rows = db.session.query(SfoCluster).all()
            db.session.expunge_all()
            for cluster in cluster_rows:
                nodes = db.session.query(SfoClusterNodes).filter(and_(SfoClusterNodes.cluster_name == cluster.cluster_name, SfoClusterNodes.node_stat == '1')).all()
                db.session.expunge_all()
                for node in nodes:
                    nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    roles = {}
                    # 节点离线
                    last_row = db.session.query(BeatHeartInfo).filter(BeatHeartInfo.hostname == node.node_host_name).order_by(BeatHeartInfo.add_time.desc()).first()
                    db.session.expunge_all()
                    #db.session.expunge_all()
                    dev_id = "node-offline-{}".format(str(node.node_host_name))
                    if last_row and util.datediff_seconds(last_row.add_time, nowtime) > 180:
                        sal = SfoAlarmLog()
                        sal.guid = str(uuid.uuid1())
                        sal.alarm_device = "node-offline-{}".format(str(node.node_host_name))
                        sal.alarm_type = 'software'
                        sal.hostname = node.node_host_name
                        sal.device_name = 'node offline'
                        sal.alarm_message = 'the node was not upload data more than 180 seconds'
                        sal.alarm_level = 'critical'
                        sal.alarm_result = '0'
                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                        db.session.add(sal)
                        db.session.commit()
                    else:
                        salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id, SfoAlarmLog.alarm_result == '0')).order_by(SfoAlarmLog.add_time.desc()).first()
                        if salh:
                            salh.alarm_result = '1'
                            db.session.add(salh)
                            db.session.commit()
                    # 服务异常
                    if util.is_json(node.node_role):
                        roles = json.loads(node.node_role, encoding='UTF-8')
                        srvstat = db.session.query(SfoNodeService).filter(
                            SfoNodeService.host_name == node.node_host_name).order_by(
                            SfoNodeService.add_time.desc()).first()
                        db.session.expunge_all()
                        dev_id = "service-data-{}".format(str(node.node_host_name))
                        if srvstat and util.datediff_seconds(srvstat.add_time, nowtime) < 180:
                            salh = db.session.query(SfoAlarmLog).filter(
                                and_(SfoAlarmLog.alarm_device == dev_id, SfoAlarmLog.alarm_result == '0')).order_by(
                                SfoAlarmLog.add_time.desc()).first()
                            if salh:
                                salh.alarm_result = '1'
                                db.session.add(salh)
                                db.session.commit()
                            if roles.has_key('Proxy-Server'):
                                if roles['Proxy-Server'] == 'YES':
                                    if hasattr(srvstat, 'srv_proxy'):
                                        dev_id = "proxy-service-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_proxy).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "proxy-service-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'proxy service'
                                            sal.alarm_message = 'the proxy service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id,SfoAlarmLog.alarm_result == '0')).order_by(SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                            if roles.has_key('Account-Server'):
                                if roles['Account-Server'] == 'YES':
                                    if hasattr(srvstat, 'srv_account'):
                                        dev_id = "account-service-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_account).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "account-service-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'account service'
                                            sal.alarm_message = 'the account service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id,SfoAlarmLog.alarm_result == '0')).order_by(SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                                    if hasattr(srvstat, 'srv_account_auditor'):
                                        dev_id = "account-auditor-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_account_auditor).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "account-auditor-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'account auditor'
                                            sal.alarm_message = 'the account auditor service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id,SfoAlarmLog.alarm_result == '0')).order_by(SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                                    if hasattr(srvstat, 'srv_account_reaper'):
                                        dev_id = "account-reaper-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_account_reaper).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "account-reaper-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'account reaper'
                                            sal.alarm_message = 'the account reaper service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id,SfoAlarmLog.alarm_result == '0')).order_by( SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                                    if hasattr(srvstat, 'srv_account_replicator'):
                                        dev_id = "account-replicator-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_account_replicator).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "account-replicator-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'account replicator'
                                            sal.alarm_message = 'the account replicator service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter( and_(SfoAlarmLog.alarm_device == dev_id, SfoAlarmLog.alarm_result == '0')).order_by( SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                            if roles.has_key('Container-Server'):
                                if roles['Container-Server'] == 'YES':
                                    if hasattr(srvstat, 'srv_container'):
                                        dev_id = "container-service-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_container).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "container-service-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'container service'
                                            sal.alarm_message = 'the container service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id, SfoAlarmLog.alarm_result == '0')).order_by( SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                                    if hasattr(srvstat, 'srv_container_auditor'):
                                        dev_id = "container-auditor-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_container_auditor).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "container-auditor-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'container auditor'
                                            sal.alarm_message = 'the container auditor service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id,SfoAlarmLog.alarm_result == '0')).order_by(SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                                    if hasattr(srvstat, 'srv_container_replicator'):
                                        dev_id = "container-replicator-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_container_replicator).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "container-replicator-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'container replicator'
                                            sal.alarm_message = 'the container replicator service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id,SfoAlarmLog.alarm_result == '0')).order_by(SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                                    if hasattr(srvstat, 'srv_container_updater'):
                                        dev_id = "container-updater-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_container_updater).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "container-updater-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'container updater'
                                            sal.alarm_message = 'the container updater service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id,SfoAlarmLog.alarm_result == '0')).order_by(SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                            if roles.has_key('Object-Server'):
                                if roles['Object-Server'] == 'YES':
                                    if hasattr(srvstat, 'srv_object'):
                                        dev_id = "object-service-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_object).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "object-service-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'object service'
                                            sal.alarm_message = 'the object service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(
                                                and_(SfoAlarmLog.alarm_device == dev_id,
                                                     SfoAlarmLog.alarm_result == '0')).order_by(
                                                SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                                    if hasattr(srvstat, 'srv_object_auditor'):
                                        dev_id = "object-auditor-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_object_auditor).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "object-auditor-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'object auditor'
                                            sal.alarm_message = 'the object auditor service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                                                         time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(
                                                and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                     SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(
                                                and_(SfoAlarmLog.alarm_device == dev_id,
                                                     SfoAlarmLog.alarm_result == '0')).order_by(
                                                SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                                    if hasattr(srvstat, 'srv_object_replicator'):
                                        dev_id = "object-replicator-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_object_replicator).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "object-replicator-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'object replicator'
                                            sal.alarm_message = 'the object replicator service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                                                         time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(
                                                and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                     SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(
                                                and_(SfoAlarmLog.alarm_device == dev_id,
                                                     SfoAlarmLog.alarm_result == '0')).order_by(
                                                SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                                    if hasattr(srvstat, 'srv_object_updater'):
                                        dev_id = "object-updater-{}".format(str(node.node_host_name))
                                        if str(srvstat.srv_object_updater).strip().upper() != 'RUNNING':
                                            sal = SfoAlarmLog()
                                            sal.guid = str(uuid.uuid1())
                                            sal.alarm_device = "object-updater-{}".format(str(node.node_host_name))
                                            sal.alarm_type = 'software'
                                            sal.hostname = node.node_host_name
                                            sal.device_name = 'object updater'
                                            sal.alarm_message = 'the object updater service was stopped'
                                            sal.alarm_level = 'critical'
                                            sal.alarm_result = '0'
                                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S',
                                                                         time.localtime(time.time()))
                                            db.session.query(SfoAlarmLog).filter(
                                                and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                     SfoAlarmLog.alarm_result == '0')).delete()
                                            db.session.add(sal)
                                            db.session.commit()
                                        else:
                                            salh = db.session.query(SfoAlarmLog).filter(
                                                and_(SfoAlarmLog.alarm_device == dev_id,
                                                     SfoAlarmLog.alarm_result == '0')).order_by(
                                                SfoAlarmLog.add_time.desc()).first()
                                            if salh:
                                                salh.alarm_result = '1'
                                                db.session.add(salh)
                                                db.session.commit()
                        else:
                            sal = SfoAlarmLog()
                            sal.guid = str(uuid.uuid1())
                            sal.alarm_device = "service-data-{}".format(str(node.node_host_name))
                            sal.alarm_type = 'software'
                            sal.hostname = node.node_host_name
                            sal.device_name = 'node service data'
                            sal.alarm_message = 'the node was not upload service status data more than 180 seconds'
                            sal.alarm_level = 'critical'
                            sal.alarm_result = '0'
                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                                      SfoAlarmLog.alarm_result == '0')).delete()
                            db.session.add(sal)
                            db.session.commit()
                    # 目标文件md5值
                    if roles and (roles['Proxy-Server'] == 'YES' or roles['Account-Server'] == 'YES' or roles[
                        'Container-Server'] == 'YES' or roles['Object-Server'] == 'YES'):
                        host_file = db.session.query(SfoHostRing).filter(
                            SfoHostRing.host_name == node.node_host_name).order_by(SfoHostRing.add_time.desc()).first()
                        db.session.expunge_all()
                        if host_file and util.datediff_seconds(host_file.add_time, nowtime) < 3600:
                            dev_id = "file-md5-{}".format(str(node.node_host_name))
                            salh = db.session.query(SfoAlarmLog).filter(
                                and_(SfoAlarmLog.alarm_device == dev_id, SfoAlarmLog.alarm_result == '0')).order_by(
                                SfoAlarmLog.add_time.desc()).first()
                            if salh:
                                salh.alarm_result = '1'
                                db.session.add(salh)
                                db.session.commit()
                            if host_file.extend and util.is_json(host_file.extend):
                                file_md5 = json.loads(host_file.extend, encoding="UTF-8")
                                if file_md5.has_key('passwdmd5'):
                                    dev_id = "passwd-md5-{}".format(str(node.node_host_name))
                                    if str(file_md5['passwdmd5']).strip() != self.get_target_md5(cluster.cluster_name,
                                                                                                 'swift_passwd_md5'):
                                        sal = SfoAlarmLog()
                                        sal.guid = str(uuid.uuid1())
                                        sal.alarm_device = "passwd-md5-{}".format(str(node.node_host_name))
                                        sal.alarm_type = 'software'
                                        sal.hostname = node.node_host_name
                                        sal.device_name = 'passwd md5'
                                        sal.alarm_message = 'this node`s md5 value ({}) of passwd file is different from the target value({})'.format(
                                            str(file_md5['passwdmd5']).strip(),
                                            self.get_target_md5(cluster.cluster_name, 'swift_passwd_md5'))
                                        sal.alarm_level = 'critical'
                                        sal.alarm_result = '0'
                                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                 SfoAlarmLog.alarm_result == '0')).delete()
                                        db.session.add(sal)
                                        db.session.commit()
                                    else:
                                        salh = db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == dev_id,
                                                 SfoAlarmLog.alarm_result == '0')).order_by(
                                            SfoAlarmLog.add_time.desc()).first()
                                        if salh:
                                            salh.alarm_result = '1'
                                            db.session.add(salh)
                                            db.session.commit()
                                else:
                                    pass
                            if host_file.rings_md5 and util.is_json(host_file.rings_md5):
                                file_md5 = json.loads(host_file.rings_md5, encoding="UTF-8")
                                if file_md5.has_key('swift.conf'):
                                    dev_id = "swift-conf-{}".format(str(node.node_host_name))
                                    if str(file_md5['swift.conf']).strip() != self.get_target_md5(cluster.cluster_name,
                                                                                                  'swift_conf_md5'):
                                        sal = SfoAlarmLog()
                                        sal.guid = str(uuid.uuid1())
                                        sal.alarm_device = "swift-conf-{}".format(str(node.node_host_name))
                                        sal.alarm_type = 'software'
                                        sal.hostname = node.node_host_name
                                        sal.device_name = 'swift.conf md5'
                                        sal.alarm_message = 'this node`s md5 value({}) of swift.conf is different from the target value({})'.format(
                                            str(file_md5['swift.conf']).strip(),
                                            self.get_target_md5(cluster.cluster_name, 'swift_conf_md5'))
                                        sal.alarm_level = 'critical'
                                        sal.alarm_result = '0'
                                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                 SfoAlarmLog.alarm_result == '0')).delete()
                                        db.session.add(sal)
                                        db.session.commit()
                                    else:
                                        salh = db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == dev_id,
                                                 SfoAlarmLog.alarm_result == '0')).order_by(
                                            SfoAlarmLog.add_time.desc()).first()
                                        if salh:
                                            salh.alarm_result = '1'
                                            db.session.add(salh)
                                            db.session.commit()
                                else:
                                    sal = SfoAlarmLog()
                                    sal.guid = str(uuid.uuid1())
                                    sal.alarm_device = "swift-conf-{}".format(str(node.node_host_name))
                                    sal.alarm_type = 'software'
                                    sal.hostname = node.node_host_name
                                    sal.device_name = 'swift.conf exception'
                                    sal.alarm_message = 'this node`s md5 info is {}'.format(str(host_file.rings_md5))
                                    sal.alarm_level = 'critical'
                                    sal.alarm_result = '0'
                                    sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                    db.session.query(SfoAlarmLog).filter(
                                        and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                             SfoAlarmLog.alarm_result == '0')).delete()
                                    db.session.add(sal)
                                    db.session.commit()
                                if file_md5.has_key('account.ring.gz'):
                                    dev_id = "account-ring-{}".format(str(node.node_host_name))
                                    if str(file_md5['account.ring.gz']).strip() != self.get_target_md5(
                                            cluster.cluster_name, 'swift_account_ring_md5'):
                                        sal = SfoAlarmLog()
                                        sal.guid = str(uuid.uuid1())
                                        sal.alarm_device = "account-ring-{}".format(str(node.node_host_name))
                                        sal.alarm_type = 'software'
                                        sal.hostname = node.node_host_name
                                        sal.device_name = 'account ring md5'
                                        sal.alarm_message = 'this node`s md5 value({}) of account.ring.gz is different from the target value({})'.format(
                                            str(file_md5['account.ring.gz']).strip(),
                                            self.get_target_md5(cluster.cluster_name, 'swift_account_ring_md5'))
                                        sal.alarm_level = 'critical'
                                        sal.alarm_result = '0'
                                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                 SfoAlarmLog.alarm_result == '0')).delete()
                                        db.session.add(sal)
                                        db.session.commit()
                                    else:
                                        salh = db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == dev_id,
                                                 SfoAlarmLog.alarm_result == '0')).order_by(
                                            SfoAlarmLog.add_time.desc()).first()
                                        if salh:
                                            salh.alarm_result = '1'
                                            db.session.add(salh)
                                            db.session.commit()
                                else:
                                    sal = SfoAlarmLog()
                                    sal.guid = str(uuid.uuid1())
                                    sal.alarm_device = "account-ring-{}".format(str(node.node_host_name))
                                    sal.alarm_type = 'software'
                                    sal.hostname = node.node_host_name
                                    sal.device_name = 'account ring exception'
                                    sal.alarm_message = 'this node`s md5 info is {}'.format(str(host_file.rings_md5))
                                    sal.alarm_level = 'critical'
                                    sal.alarm_result = '0'
                                    sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                    db.session.query(SfoAlarmLog).filter(
                                        and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                             SfoAlarmLog.alarm_result == '0')).delete()
                                    db.session.add(sal)
                                    db.session.commit()
                                if file_md5.has_key('container.ring.gz'):
                                    dev_id = "container-ring-{}".format(str(node.node_host_name))
                                    if str(file_md5['container.ring.gz']).strip() != self.get_target_md5(
                                            cluster.cluster_name, 'swift_container_ring_md5'):
                                        sal = SfoAlarmLog()
                                        sal.guid = str(uuid.uuid1())
                                        sal.alarm_device = "container-ring-{}".format(str(node.node_host_name))
                                        sal.alarm_type = 'software'
                                        sal.hostname = node.node_host_name
                                        sal.device_name = 'container ring md5'
                                        sal.alarm_message = 'this node`s md5 value({}) of container.ring.gz is different from the target value({})'.format(
                                            str(file_md5['container.ring.gz']).strip(),
                                            self.get_target_md5(cluster.cluster_name, 'swift_container_ring_md5'))
                                        sal.alarm_level = 'critical'
                                        sal.alarm_result = '0'
                                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                 SfoAlarmLog.alarm_result == '0')).delete()
                                        db.session.add(sal)
                                        db.session.commit()
                                    else:
                                        salh = db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == dev_id,
                                                 SfoAlarmLog.alarm_result == '0')).order_by(
                                            SfoAlarmLog.add_time.desc()).first()
                                        if salh:
                                            salh.alarm_result = '1'
                                            db.session.add(salh)
                                            db.session.commit()
                                else:
                                    sal = SfoAlarmLog()
                                    sal.guid = str(uuid.uuid1())
                                    sal.alarm_device = "container-ring-{}".format(str(node.node_host_name))
                                    sal.alarm_type = 'software'
                                    sal.hostname = node.node_host_name
                                    sal.device_name = 'container ring exception'
                                    sal.alarm_message = 'this node`s md5 info is {}'.format(str(host_file.rings_md5))
                                    sal.alarm_level = 'critical'
                                    sal.alarm_result = '0'
                                    sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                    db.session.query(SfoAlarmLog).filter(
                                        and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                             SfoAlarmLog.alarm_result == '0')).delete()
                                    db.session.add(sal)
                                    db.session.commit()
                                if file_md5.has_key('object.ring.gz'):
                                    dev_id = "object-ring-{}".format(str(node.node_host_name))
                                    if str(file_md5['object.ring.gz']).strip() != self.get_target_md5(
                                            cluster.cluster_name, 'swift_object_ring_md5'):
                                        sal = SfoAlarmLog()
                                        sal.guid = str(uuid.uuid1())
                                        sal.alarm_device = "object-ring-{}".format(str(node.node_host_name))
                                        sal.alarm_type = 'software'
                                        sal.hostname = node.node_host_name
                                        sal.device_name = 'object ring md5'
                                        sal.alarm_message = 'this node`s md5 value({}) of object.ring.gz is different from the target value({})'.format(
                                            str(file_md5['object.ring.gz']).strip(),
                                            self.get_target_md5(cluster.cluster_name, 'swift_object_ring_md5'))
                                        sal.alarm_level = 'critical'
                                        sal.alarm_result = '0'
                                        sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                        db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                 SfoAlarmLog.alarm_result == '0')).delete()
                                        db.session.add(sal)
                                        db.session.commit()
                                    else:
                                        salh = db.session.query(SfoAlarmLog).filter(
                                            and_(SfoAlarmLog.alarm_device == dev_id,
                                                 SfoAlarmLog.alarm_result == '0')).order_by(
                                            SfoAlarmLog.add_time.desc()).first()
                                        if salh:
                                            salh.alarm_result = '1'
                                            db.session.add(salh)
                                            db.session.commit()
                                else:
                                    sal = SfoAlarmLog()
                                    sal.guid = str(uuid.uuid1())
                                    sal.alarm_device = "object-ring-{}".format(str(node.node_host_name))
                                    sal.alarm_type = 'software'
                                    sal.hostname = node.node_host_name
                                    sal.device_name = 'object ring exception'
                                    sal.alarm_message = 'this node`s md5 info is {}'.format(str(host_file.rings_md5))
                                    sal.alarm_level = 'critical'
                                    sal.alarm_result = '0'
                                    sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                    db.session.query(SfoAlarmLog).filter(
                                        and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                             SfoAlarmLog.alarm_result == '0')).delete()
                                    db.session.add(sal)
                                    db.session.commit()
                            else:
                                pass
                        else:
                            sal = SfoAlarmLog()
                            sal.guid = str(uuid.uuid1())
                            sal.alarm_device = "file-md5-{}".format(str(node.node_host_name))
                            sal.alarm_type = 'software'
                            sal.hostname = node.node_host_name
                            sal.device_name = 'file md5'
                            sal.alarm_message = 'this node`s host ring info is not upload last time'
                            sal.alarm_level = 'critical'
                            sal.alarm_result = '0'
                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                                      SfoAlarmLog.alarm_result == '0')).delete()
                            db.session.add(sal)
                            db.session.commit()
                    # 故障磁盘
                    nodeperform = db.session.query(SfoNodePerform).filter(
                        SfoNodePerform.host_name == node.node_host_name).order_by(
                        SfoNodePerform.add_time.desc()).first()
                    db.session.expunge_all()
                    if nodeperform and util.datediff_seconds(nodeperform.add_time, nowtime) < 300:
                        if util.is_json(nodeperform.stg_diskusage):
                            dev_id = "disk-mount-{}".format(str(node.node_host_name))
                            salh = db.session.query(SfoAlarmLog).filter(
                                and_(SfoAlarmLog.alarm_device == dev_id, SfoAlarmLog.alarm_result == '0')).order_by(
                                SfoAlarmLog.add_time.desc()).first()
                            if salh:
                                salh.alarm_result = '1'
                                db.session.add(salh)
                                db.session.commit()
                            diskstats = json.loads(nodeperform.stg_diskusage, encoding='UTF-8')
                            for stat in diskstats:
                                dev_id = "disk-mount-{}:{}".format(str(node.node_host_name), str(stat['device']))
                                if str(stat['mounted']).strip().upper() != 'TRUE':
                                    sal = SfoAlarmLog()
                                    sal.guid = str(uuid.uuid1())
                                    sal.alarm_device = "disk-mount-{}:{}".format(str(node.node_host_name),
                                                                                 str(stat['device']))
                                    sal.alarm_type = 'software'
                                    sal.hostname = node.node_host_name
                                    sal.device_name = 'disk mount'
                                    sal.alarm_message = 'this node`s disk is not mounted'
                                    sal.alarm_level = 'critical'
                                    sal.alarm_result = '0'
                                    sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                    db.session.query(SfoAlarmLog).filter(
                                        and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                             SfoAlarmLog.alarm_result == '0')).delete()
                                    db.session.add(sal)
                                    db.session.commit()
                                else:
                                    salh = db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == dev_id,
                                                                                     SfoAlarmLog.alarm_result == '0')).order_by(
                                        SfoAlarmLog.add_time.desc()).first()
                                    if salh:
                                        salh.alarm_result = '1'
                                        db.session.add(salh)
                                        db.session.commit()
                        else:
                            sal = SfoAlarmLog()
                            sal.guid = str(uuid.uuid1())
                            sal.alarm_device = "disk-mount-{}".format(str(node.node_host_name))
                            sal.alarm_type = 'software'
                            sal.hostname = node.node_host_name
                            sal.device_name = 'disk mount'
                            sal.alarm_message = 'this node`s disk data format is not correct'
                            sal.alarm_level = 'critical'
                            sal.alarm_result = '0'
                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device,
                                                                      SfoAlarmLog.alarm_result == '0')).delete()
                            db.session.add(sal)
                            db.session.commit()
                    else:
                        if not roles.has_key('Proxy-Server') or not roles.has_key(
                                'Account-Server') or not roles.has_key('Container-Server') or not roles.has_key(
                                'Object-Server'):
                            pass
                        elif (roles['Proxy-Server'] == 'YES' or roles['Proxy-Server'] == 'NO') and roles[
                            'Account-Server'] == 'NO' and roles['Container-Server'] == 'NO' and roles[
                            'Object-Server'] == 'NO':
                            pass
                        else:
                            sal = SfoAlarmLog()
                            sal.guid = str(uuid.uuid1())
                            sal.alarm_device = "disk-mount-{}".format(str(node.node_host_name))
                            sal.alarm_type = 'software'
                            sal.hostname = node.node_host_name
                            sal.device_name = 'disk mount'
                            sal.alarm_message = 'this node`s disk recon data is not upload more than 300 seconds'
                            sal.alarm_level = 'critical'
                            sal.alarm_result = '0'
                            sal.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            db.session.query(SfoAlarmLog).filter(and_(SfoAlarmLog.alarm_device == sal.alarm_device, SfoAlarmLog.alarm_result == '0')).delete()
                            db.session.add(sal)
                            db.session.commit()
            # 清除告警信息
            alarms = db.session.query(SfoAlarmLog).filter(SfoAlarmLog.alarm_result == '0').all()
            db.session.expunge_all()
            if alarms and len(alarms) > 0:
                nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                for alarm in alarms:
                    # 如果告警信息15分钟还没更新，表示不再出现，遂清除
                    if alarm and util.datediff_seconds(alarm.add_time, nowtime) > 900:
                        alarm.alarm_result = '1'
                        db.session.add(alarm)
                db.session.commit()
        except Exception as ex:

            logger.info("monitoring_alarm function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()

    def keep_pids_alive(self):
        '''
        确保所有后台消费进程运行，如果死掉，自动重启一个
        :return:
        '''
        try:
            cdd = ConsumeData2Db()
            for i in range(len(pids)):
                id = pids[i]
                if not psutil.pid_exists(id):
                    prc = multiprocessing.Process(target=cdd.consume_data)
                    prc.start()
                    pids[i] = prc.pid
                    logger.info("pid {} is stopped and new process id {} is started in keep_pids_alive function".format(str(id),str(prc.pid)))
        except Exception as ex:
            logger.info("keep_pids_alive function excute exception:" + str(ex) + ';the pids is ' + str(pids))

# schdule tasks
def get_cluster_info_schl():
    '''
    起进程定时执行集群数据统筹
    （起进程避免主进程的schedule因等待函数执行完成而卡住）
    :return:
    '''
    try:
        cdd = ConsumeData2Db()
        multiprocessing.Process(target=cdd.get_cluster_info).start()
    except Exception as ex:
        logger.info("get_cluster_info_schl function excute exception:" + str(ex))


def expire_data_rows_schl():
    '''
    起进程定时执行过期数据删除
    （起进程避免主进程的schedule因等待函数执行完成而卡住）
    :return:
    '''
    try:
        cdd = ConsumeData2Db()
        multiprocessing.Process(target=cdd.expire_data_rows).start()
    except Exception as ex:
        logger.info("expire_data_rows_schl function excute exception:" + str(ex))


def keep_pids_alive_schl():
    '''
    起线程定时执行消费进程检查，如果死掉自动起一个新的
    （起线程避免主进程的schedule因等待函数执行完成而卡住）
    :return:
    '''
    try:
        bst = BackStageTask()
        threading.Thread(target=bst.keep_pids_alive).start()
    except Exception as ex:
        logger.info("keep_pids_alive_schl function excute exception:" + str(ex))


def daily_inspection_schl():
    '''
    起进程定时执行日常巡检
    （起进程避免主进程的schedule因等待函数执行完成而卡住）
    :return:
    '''
    try:
        bst = BackStageTask()
        multiprocessing.Process(target=bst.daily_inspection).start()
    except Exception as ex:
        logger.info("daily_inspection_schl function excute exception:" + str(ex))


def monitoring_alarm_schl():
    '''
    起进程处理监控告警项
    （起进程避免主进程的schedule因等待函数执行完成而卡住）
    :return:
    '''
    try:
        bst = BackStageTask()
        multiprocessing.Process(target=bst.monitoring_alarm).start()
    except Exception as ex:
        logger.info("monitoring_alarm_schl function excute exception:" + str(ex))

def data_archive_5min_schl():
    '''
    起进程进行5分钟数据归档
    （起进程避免主进程的schedule因等待函数执行完成而卡住）
    :return:
    '''
    try:
        cdd = ConsumeData2Db()
        multiprocessing.Process(target=cdd.data_archive_5min).start()
    except Exception as ex:
        logger.info("data_archive_5min_schl function excute exception:" + str(ex))


def data_archive_hour_schl():
    '''
    起进程进行1小时数据归档
    （起进程避免主进程的schedule因等待函数执行完成而卡住）
    :return:
    '''
    try:
        cdd = ConsumeData2Db()
        multiprocessing.Process(target=cdd.data_archive_hours).start()
    except Exception as ex:
        logger.info("data_archive_hour_schl function excute exception:" + str(ex))


def data_archive_day_schl():
    '''
    起进程进行天数据归档
    （起进程避免主进程的schedule因等待函数执行完成而卡住）
    :return:
    '''
    try:
        cdd = ConsumeData2Db()
        multiprocessing.Process(target=cdd.data_archive_days).start()
    except Exception as ex:
        logger.info("data_archive_day_schl function excute exception:" + str(ex))


class Data2Db(Agent):
    def __init__(self, pidfile):
        Agent.__init__(self, pidfile)

    def run(self):
        try:
            sys.stdout.flush()
            cdd = ConsumeData2Db()
            # 多进程模式
            pro = {}
            #这里起的进程数跟kafka的分区数和本程序部署的节点数相关，所有节点上的进程数之和要小于等于kafka topic分区数
            if int(config.process_workers) > 1:
                for i in range(1, int(config.process_workers)):
                    pro[i * 10 + 1] = multiprocessing.Process(target=cdd.consume_data)
                    pro[i * 10 + 1].start()
                    pids.append(pro[i * 10 + 1].pid)
                    logger.info('the pid of consume_data is %s' % (str(pro[i * 10 + 1].pid)))
                    pro[i * 10 + 2] = multiprocessing.Process(target=cdd.consume_statsd_data)
                    pro[i * 10 + 2].start()
                    pids.append(pro[i * 10 + 2].pid)
                    logger.info('the pid of consume_statsd_data is %s' % (str(pro[i * 10 + 2].pid)))
            else:
                multiprocessing.Process(target=cdd.consume_data).start()
                multiprocessing.Process(target=cdd.consume_statsd_data).start()
            # schdule
            schedule.every(config.host_refresh).seconds.do(get_cluster_info_schl)
            schedule.every(600).seconds.do(expire_data_rows_schl)
            schedule.every(config.host_refresh).seconds.do(keep_pids_alive_schl)
            schedule.every(8).hours.do(daily_inspection_schl)
            schedule.every(180).seconds.do(monitoring_alarm_schl)
            schedule.every(5).minutes.do(data_archive_5min_schl)
            schedule.every(1).hours.do(data_archive_hour_schl)
            schedule.every(12).hours.do(data_archive_day_schl)
            #os.wait()
            while True:
                schedule.run_pending()
                time.sleep(1)
        except Exception as ex:
            logger.info("Data2Db agent run function excute exception:" + str(ex))


if __name__ == '__main__':
    try:
        util.ensure_dir(config.data_agent_pfile)
        util.ensure_dir(config.agent_log_fname)
        dbagent = Data2Db(config.data_agent_pfile)
        if len(sys.argv) == 2:
            if 'start' == sys.argv[1]:
                dbagent.start()
            elif 'stop' == sys.argv[1]:
                dbagent.stop()
            elif 'status' == sys.argv[1]:
                dbagent.status()
            elif 'restart' == sys.argv[1]:
                dbagent.restart()
            else:
                print("Unknown command")
                sys.exit(2)
        else:
            print("usage: %s" % (sys.argv[1],))
            sys.exit(2)
    except Exception as ex:
        logger.info("Data2Db agent run exception:" + str(ex))
