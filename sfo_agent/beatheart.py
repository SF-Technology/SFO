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

from sfo_agent.kafka_producer import ProduceKafkaInfo
from sfo_common.agent import Agent
from sfo_common.import_common import *


def beat_heart():
    '''
    发送心跳数据
    :return:数据生成到kafka中
    '''
    kfk = ProduceKafkaInfo()
    try:
        isok = True
        heart = {}
        heart['guid'] = str(uuid.uuid1())
        heart['data_model'] = 'BeatHeart'
        heart['cluster_name'] = config.swift_cluster_name
        heart['hostname'] = socket.getfqdn()
        heart['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        data = json.dumps(heart, encoding="UTF-8", ensure_ascii=True)
        #检测到所有网关是否联通，全部连通才发送心跳
        gates = util.exct_cmd("route -n |awk '{print $2}'|grep -v '0.0.0.0'|sed -n '3,$p'")
        for gate in gates:
            isok = isok and util.check_ip_alive(gate)
        if isok:
            kfk.produce_kafka_info(config.kafka_sys_topic,data)
        else:
            pass
    except Exception as ex:
        logger.exception("sys beatheart function excute exception:" + str(ex))

def get_beat_heart_schl():
    '''
    起线程定时执行心跳数据发送
    :return:
    '''
    try:
        threading.Thread(target=beat_heart).start()
    except Exception as ex:
        logger.exception("get_beat_heart_schl function excute exception:" + str(ex))

class BeatHeartAgnet(Agent):
    def __init__(self, pidfile):
        Agent.__init__(self, pidfile)

    def run(self):
        '''
        重写守护进程的run函数，实现定时发送心跳功能
        :return:
        '''
        try:
            sys.stdout.flush()
            sys.stderr.flush()
            hostname = socket.getfqdn()
            hostip = socket.gethostbyname(hostname)
            logger.info("hostname is {}, ip is {}".format(hostname, hostip))
            schedule.every(config.heart_refresh).seconds.do(get_beat_heart_schl)
            schedule.run_all(0)
            while True:
                schedule.run_pending()
                time.sleep(0.1)
        except Exception as ex:
            logger.exception("BeatHeartAgnet run function run exception:" + str(ex))