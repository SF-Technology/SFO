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
from sfo_common.import_common import *

class ElkLog(object):
    '''
    处理ELK数据类
    '''
    def __init__(self):
        pass

    def get_elk_log_json(self):
        '''
        通过调用elasticsearch接口查询指定索引数据，计算集群的平均响应时间
        :return:
        '''
        try:
            day = time.strftime("%Y.%m.%d",time.localtime(time.time()))
            clusters = config.elk_index_name.split(',')
            if clusters:
                for cluster in clusters:
                    index_name="{}-swift-proxy-{}".format(cluster,day)
                    req_url = '{}{}/_search?pretty'.format(config.elk_server_url,index_name)
                    headers = {'content-type': "application/json"}
                    l_time = datetime.datetime.now() + datetime.timedelta(minutes=-5)
                    now_time = util.local2utc(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
                    now_time_5m = util.local2utc(l_time.strftime('%Y-%m-%d %H:%M:%S.%f'))
                    body = {
                        "query": {
                            "bool":{
                                "must":{
                                    "match_all":{}
                                },
                                "filter":{
                                    "range":{
                                        "@timestamp":{
                                            "gte":now_time_5m,
                                            "lte":now_time
                                        }
                                    }
                                }
                            }
                        },
                        "size": 10000,
                        "sort": {
                            "@timestamp": { "order": "asc" }
                        },
                        "_source": ["status", "method","client_ip","remote_ip","timestamp","request_time","@timestamp"]
                    }
                    #print req_url,body,headers
                    response = requests.post(req_url,data=json.dumps(body),headers=headers)
                    total_time = 0.0
                    head_count = 0
                    head_total_time = 0.0
                    get_count = 0
                    get_total_time = 0.0
                    put_count = 0
                    put_total_time = 0.0
                    post_count = 0
                    post_total_time = 0.0
                    delete_count = 0
                    delete_total_time = 0.0
                    if response.status_code == 200:
                        tps = SfoClusterTps()
                        res_data = json.loads(response.text,encoding='UTF-8')
                        if res_data and res_data.has_key('hits'):
                            hits = res_data['hits']
                            total = hits['total']
                            list = hits['hits']
                            if list and total > 0:
                                for obj in list:
                                    if isinstance(obj,dict) and obj.has_key('_source'):
                                        source = obj['_source']
                                        if source.has_key('request_time'):
                                            total_time += float(source['request_time'])
                                        if source.has_key('method') and str(source['method']).strip().upper()=='HEAD':
                                            head_count += 1
                                            if source.has_key('request_time'):
                                                head_total_time += float(source['request_time'])
                                        if source.has_key('method') and str(source['method']).strip().upper()=='GET':
                                            get_count += 1
                                            if source.has_key('request_time'):
                                                get_total_time += float(source['request_time'])
                                        if source.has_key('method') and str(source['method']).strip().upper()=='PUT':
                                            put_count += 1
                                            if source.has_key('request_time'):
                                                put_total_time += float(source['request_time'])
                                        if source.has_key('method') and str(source['method']).strip().upper()=='POST':
                                            post_count += 1
                                            if source.has_key('request_time'):
                                                post_total_time += float(source['request_time'])
                                        if source.has_key('method') and str(source['method']).strip().upper()=='DELETE':
                                            delete_count += 1
                                            if source.has_key('request_time'):
                                                delete_total_time += float(source['request_time'])
                                tps.guid = str(uuid.uuid1())
                                tps.cluster_name = cluster
                                if total > 0:
                                    tps.avg_time = '%.2f'%(total_time/total*1000)
                                else:
                                    tps.avg_time = 0
                                if head_count > 0:
                                    tps.head_time = '%.2f'%(head_total_time/head_count*1000)
                                else:
                                    tps.head_time = 0
                                if get_count > 0:
                                    tps.get_time = '%.2f'%(get_total_time/get_count*1000)
                                else:
                                    tps.get_time = 0
                                if put_count > 0:
                                    tps.put_time = '%.2f'%(put_total_time/put_count*1000)
                                else:
                                    tps.put_time = 0
                                if post_count > 0:
                                    tps.post_time = '%.2f'%(post_total_time/post_count*1000)
                                else:
                                    tps.post_time = 0
                                if delete_count > 0:
                                    tps.delete_time = '%.2f'%(delete_total_time/delete_count*1000)
                                else:
                                    tps.delete_time = 0
                                tps.add_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                db.session.add(tps)
                                db.session.commit()
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
        except Exception as ex:
            logger.info("get_elk_log_json function excute exception:" + str(ex))
        finally:
            db.session.close()
            db.session.remove()

#schedule tasks
def get_elklog_json_schl():
    '''
    起线程执行日志分析
    :return:
    '''
    try:
        el = ElkLog()
        threading.Thread(target=el.get_elk_log_json).start()
    except Exception as ex:
        logger.info("get_elklog_json_schl function excute exception:" + str(ex))

class ElklogUnitAgnet(Agent):
    def __init__(self, pidfile):
        Agent.__init__(self, pidfile)

    def run(self):
        try:
            sys.stdout.flush()
            hostname = socket.getfqdn()
            hostip = socket.gethostbyname(hostname)
            logger.info("hostname is {}, ip is {}".format(hostname, hostip))
            #use schedule
            schedule.every(300).seconds.do(get_elklog_json_schl)
            while True:
                schedule.run_pending()
                time.sleep(1)
        except Exception as ex:
            logger.info("elk log agent run exception:" + str(ex))

def main():
    agent = ElklogUnitAgnet(config.elklog_agent_pfile)
    try:
        if len(sys.argv) == 3:
            if 'elklog' == sys.argv[1]:
                if 'start' == sys.argv[2]:
                    agent.start()
                if 'stop' == sys.argv[2]:
                    agent.stop()
            else:
                print("Unknown command")
                sys.exit(2)
        else:
            print("usage: %s" % (sys.argv[0],))
            sys.exit(2)
    except Exception as ex:
        logger.info("elk log process run exception:" + str(ex))

if __name__ == '__main__':
    main()