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

class ProduceKafkaInfo(object):
    '''
    Kafka数据生产类
    '''
    def __init__(self):
        self.random_size = 1000000

    def produce_kafka_info(self, topic,data):
        '''
        将data数据生产到kafka指定的主题中
        :param data:
        :return:
        '''
        try:
            if not topic:
                raise IOError,'the param topic can not be None'
            if not data:
                raise IOError,'the param data can not be None'
            if topic and data:
                p_key = util.randomint(1, self.random_size)
                pclient = KafkaClient(zookeeper_hosts=config.zookeeper_server,socket_timeout_ms=1000*5)
                if pclient.topics.has_key(topic):
                    tp = pclient.topics[topic]
                    pid = tp.partitions
                    pkey = p_key % len(pid)
                    with tp.get_producer(partitioner=lambda pid, key: pid[pkey]) as producer:
                        producer.produce(message=data,partition_key=b'partition_key_{}'.format(str(pkey)))
                        producer.stop()
        except Exception as ex:
            logger.exception("produce_kafka_info function excute exception:%s,the topic is %s,the data is %s" % (str(ex),str(topic),str(data)))