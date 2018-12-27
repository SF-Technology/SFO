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
import ConfigParser

CUR_PATH = os.path.abspath(__file__)   #当前文件的绝对路径
CUR_DIR = os.path.dirname(CUR_PATH)     #当前文件所在的目录
CUR_PARE = os.path.dirname(CUR_DIR)     #当前文件所在的目录的父目录
CONFIG_PATH = CUR_PARE + "/sfo.conf"

config = ConfigParser.ConfigParser()


class Config(object):
    def __init__(self):
        config.read(CONFIG_PATH)
        try:
            #colony section config
            if config.has_section("cluster"):
                if config.has_option("cluster", "swift_cluster_name"):
                    self.swift_cluster_name = config.get('cluster','swift_cluster_name')
                else:
                    self.swift_cluster_name = "default"
                if config.has_option("cluster", "ip"):
                    self.ip = config.get('cluster', 'ip')
                else:
                    self.ip = "127.0.0.1"
                if config.has_option("cluster", "port"):
                    self.port = int(config.get('cluster', 'port'))
                else:
                    self.port = 41717
                if config.has_option("cluster", "proxy_port"):
                    self.proxy_port = int(config.get('cluster', 'proxy_port'))
                else:
                    self.proxy_port = 8080
                if config.has_option("cluster", "account_port"):
                    self.account_port = int(config.get('cluster', 'account_port'))
                else:
                    self.account_port = 6012
                if config.has_option("cluster", "container_port"):
                    self.container_port = int(config.get('cluster', 'container_port'))
                else:
                    self.container_port = 6011
                if config.has_option("cluster", "object_port"):
                    self.object_port = int(config.get('cluster', 'object_port'))
                else:
                    self.object_port = 6010
                if config.has_option("cluster", "sock_cmd_port"):
                    self.sock_cmd_port = int(config.get('cluster', 'sock_cmd_port'))
                else:
                    self.sock_cmd_port = 7201
                if config.has_option("cluster", "sock_file_port"):
                    self.sock_file_port = int(config.get('cluster', 'sock_file_port'))
                else:
                    self.sock_file_port = 7202
                if config.has_option("cluster", "host_ip_prefix"):
                    self.host_ip_prefix = config.get('cluster', 'host_ip_prefix')
                else:
                    self.host_ip_prefix = "127.0.0"
                if config.has_option("cluster", "node_ip_prefix"):
                    self.node_ip_prefix = config.get('cluster', 'node_ip_prefix')
                else:
                    self.node_ip_prefix = "192.168"
                if config.has_option("cluster", "statsD_ip"):
                    self.statsD_ip = config.get('cluster', 'statsD_ip')
                else:
                    self.statsD_ip = "192.168"
                if config.has_option("cluster", "temp_file"):
                    self.temp_file = config.get('cluster', 'temp_file')
                else:
                    self.temp_file = "/tmp/sfo/"
                if config.has_option("cluster", "sfo_server_temp_file"):
                    self.sfo_server_temp_file = config.get('cluster', 'sfo_server_temp_file')
                else:
                    self.sfo_server_temp_file = "/tmp/sfo/sfo_temp/"
                if config.has_option("cluster", "elk_index_name"):
                    self.elk_index_name = config.get('cluster', 'elk_index_name')
                else:
                    self.elk_index_name = "default"
                if config.has_option("cluster", "elk_server_url"):
                    self.elk_server_url = config.get('cluster', 'elk_server_url')
                else:
                    self.elk_server_url = "http://127.0.0.1:9200"
                if config.has_option("cluster", "process_workers"):
                    self.process_workers = int(config.get('cluster', 'process_workers'))
                else:
                    self.process_workers = 1
                if config.has_option("cluster", "thread_workers"):
                    self.thread_workers = int(config.get('cluster', 'thread_workers'))
                else:
                    self.thread_workers = 5
            else:
                self.swift_cluster_name = "default"
                self.ip = "127.0.0.1"
                self.port = 41717
                self.proxy_port = 8080
                self.account_port = 6012
                self.container_port = 6011
                self.object_port = 6010
                self.sock_cmd_port = 7201
                self.sock_file_port = 7202
                self.host_ip_prefix = "127.0.0"
                self.node_ip_prefix = "192.168"
                self.statsD_ip = "192.168"
                self.temp_file = "/tmp/sfo/"
                self.sfo_server_temp_file = "/tmp/sfo/sfo_temp/"
                self.elk_index_name = "default"
                self.elk_server_url = "http://127.0.0.1:9200"
                self.process_workers = 1
                self.thread_workers = 5
            # swift section config
            if config.has_section("swift"):
                if config.has_option("swift", "swift_auth_url"):
                    self.swift_auth_url = config.get('swift', 'swift_auth_url')
                else:
                    self.swift_auth_url = "http://127.0.0.1:8080/auth/v1.0/"
                if config.has_option("swift", "swift_auth_version"):
                    self.swift_auth_version = config.get('swift', 'swift_auth_version')
                else:
                    self.swift_auth_version = 3
                if config.has_option("swift", "storage_url"):
                    self.storage_url = config.get('swift', 'storage_url')
                else:
                    self.storage_url = "http://127.0.0.1:8080/v1/"
                if config.has_option("swift", "swauth_url"):
                    self.swauth_url = config.get('swift', 'swauth_url')
                else:
                    self.swauth_url = "http://127.0.0.1:8080/auth/v2"
                if config.has_option("swift", "swift_user"):
                    self.swift_user = config.get('swift', 'swift_user')
                else:
                    self.swift_user = "admin"
                if config.has_option("swift", "swift_password"):
                    self.swift_password = config.get('swift', 'swift_password')
                else:
                    self.swift_password = "admin"
            #kafka section config
            if config.has_section("kafka"):
                if config.has_option("kafka", "kafka_sys_topic"):
                    self.kafka_sys_topic = config.get('kafka', 'kafka_sys_topic')
                else:
                    self.kafka_sys_topic = "sfo_cluster_info"
                if config.has_option("kafka", "kafka_sys_group"):
                    self.kafka_sys_group = config.get('kafka', 'kafka_sys_group')
                else:
                    self.kafka_sys_group = "sfo_consumer_group"
                if config.has_option("kafka", "kafka_statd_topic"):
                    self.kafka_statd_topic = config.get('kafka', 'kafka_statd_topic')
                else:
                    self.kafka_statd_topic = "sfo_statsd_info"
                if config.has_option("kafka", "zookeeper_server"):
                    self.zookeeper_server = config.get('kafka', 'zookeeper_server')
                else:
                    self.zookeeper_server = "127.0.0.1:2181"
            else:
                self.kafka_sys_topic = "sfo_cluster_info"
                self.kafka_sys_group = "sfo_consumer_group"
                self.kafka_statd_topic = "sfo_statsd_info"
                self.zookeeper_server = "127.0.0.1:2181"
            # mysql database section config
            if config.has_section("mysqldb"):
                if config.has_option("mysqldb", "mysql_host"):
                    self.mysql_host = config.get('mysqldb', 'mysql_host')
                else:
                    self.mysql_host = "localhost"
                if config.has_option("mysqldb", "mysql_port"):
                    self.mysql_port = config.get('mysqldb', 'mysql_port')
                else:
                    self.mysql_port = 3306
                if config.has_option("mysqldb", "mysql_dbname"):
                    self.mysql_dbname = config.get('mysqldb', 'mysql_dbname')
                else:
                    self.mysql_dbname = "sfo"
                if config.has_option("mysqldb", "mysql_user"):
                    self.mysql_user = config.get('mysqldb', 'mysql_user')
                else:
                    self.mysql_user = "root"
                if config.has_option("mysqldb", "mysql_passwd"):
                    self.mysql_passwd = config.get('mysqldb', 'mysql_passwd')
                else:
                    self.mysql_passwd = ""
            else:
                self.mysql_host = "localhost"
                self.mysql_port = 3306
                self.mysql_dbname = "sfo"
                self.mysql_user = "root"
                self.mysql_passwd = ""
            # refresh section config
            if config.has_section("refreshs"):
                if config.has_option("refreshs", "host_refresh"):
                    self.host_refresh = int(config.get('refreshs', 'host_refresh'))
                else:
                    self.host_refresh = 60
                if config.has_option("refreshs", "node_refresh"):
                    self.node_refresh = int(config.get('refreshs', 'node_refresh'))
                else:
                    self.node_refresh = 60
                if config.has_option("refreshs", "mem_refresh"):
                    self.mem_refresh = int(config.get('refreshs', 'mem_refresh'))
                else:
                    self.mem_refresh = 60
                if config.has_option("refreshs", "cpu_refresh"):
                    self.cpu_refresh = int(config.get('refreshs', 'cpu_refresh'))
                else:
                    self.cpu_refresh = 60
                if config.has_option("refreshs", "disk_refresh"):
                    self.disk_refresh = int(config.get('refreshs', 'disk_refresh'))
                else:
                    self.disk_refresh = 60
                if config.has_option("refreshs", "net_refresh"):
                    self.net_refresh = int(config.get('refreshs', 'net_refresh'))
                else:
                    self.net_refresh = 60
                if config.has_option("refreshs", "rep_refresh"):
                    self.rep_refresh = int(config.get('refreshs', 'rep_refresh'))
                else:
                    self.rep_refresh = 600
                if config.has_option("refreshs", "heart_refresh"):
                    self.heart_refresh = int(config.get('refreshs', 'heart_refresh'))
                else:
                    self.heart_refresh = 10
                if config.has_option("refreshs", "mon_refresh"):
                    self.mon_refresh = int(config.get('refreshs', 'mon_refresh'))
                else:
                    self.mon_refresh = 60
            else:
                self.host_refresh = 60
                self.node_refresh = 60
                self.mem_refresh = 60
                self.cpu_refresh = 60
                self.disk_refresh = 60
                self.net_refresh = 60
                self.rep_refresh = 600
                self.heart_refresh = 10
                self.mon_refresh = 60
            # agent section config
            if config.has_section("agents"):
                if config.has_option("agents", "sys_agent_pfile"):
                    self.sys_agent_pfile = config.get('agents', 'sys_agent_pfile')
                else:
                    self.sys_agent_pfile = "/var/run/sfo/sysagent.pid"
                if config.has_option("agents", "swift_agent_pfile"):
                    self.swift_agent_pfile = config.get('agents', 'swift_agent_pfile')
                else:
                    self.swift_agent_pfile = "/var/run/sfo/swiftagent.pid"
                if config.has_option("agents", "data_agent_pfile"):
                    self.data_agent_pfile = config.get('agents', 'data_agent_pfile')
                else:
                    self.data_agent_pfile = "/var/run/sfo/datagent.pid"
                if config.has_option("agents", "server_agent_pfile"):
                    self.server_agent_pfile = config.get('agents', 'server_agent_pfile')
                else:
                    self.server_agent_pfile = "/var/run/sfo/serveragent.pid"
                if config.has_option("agents", "heart_agent_pfile"):
                    self.heart_agent_pfile = config.get('agents', 'heart_agent_pfile')
                else:
                    self.heart_agent_pfile = "/var/run/sfo/beatheart.pid"
                if config.has_option("agents", "elklog_agent_pfile"):
                    self.elklog_agent_pfile = config.get('agents', 'elklog_agent_pfile')
                else:
                    self.elklog_agent_pfile = "/var/run/sfo/elklogagent.pid"
            else:
                self.sys_agent_pfile = "/var/run/sfo/sysagent.pid"
                self.swift_agent_pfile = "/var/run/sfo/swiftagent.pid"
                self.data_agent_pfile = "/var/run/sfo/datagent.pid"
                self.server_agent_pfile = "/var/run/sfo/serveragent.pid"
                self.heart_agent_pfile = "/var/run/sfo/beatheart.pid"
                self.elklog_agent_pfile = "/var/run/sfo/elklogagent.pid"
            # log section config, the following code can not move forward
            self.logging_conf = CUR_PARE + config.get('log', 'conf')
            config.read(self.logging_conf)
            self.agent_log_fname = eval(config.get('handler_agentHandler', 'args').replace(')(', '),('))[0]
            self.client_log_fname = eval(config.get('handler_serverHandler', 'args').replace(')(', '),('))[0]
        except Exception as ex:
            print(ex)
            sys.exit(2)
