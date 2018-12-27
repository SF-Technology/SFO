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

from sfo_common.import_common import *
from sfo_agent.cluster_agent_unit import ClusterUnitAgnet
from sfo_agent.sys_agent_unit import SysUnitAgnet
from sfo_agent.beatheart import BeatHeartAgnet
from sfo_agent.cluster_server_client import ServerAgent
util.ensure_dir('/var/log/sfo/')


'''
agent程序入口
使用自带的虚环境运行
/XXX/XXX/python /XXX/XXX/sfo_agent.py all start
'''

def main():
    util.ensure_dir(config.sys_agent_pfile)
    util.ensure_dir(config.agent_log_fname)
    sysagent = SysUnitAgnet(config.sys_agent_pfile)
    swiftagent = ClusterUnitAgnet(config.swift_agent_pfile)
    server = ServerAgent(config.server_agent_pfile)
    heart = BeatHeartAgnet(config.heart_agent_pfile)
    if len(sys.argv) == 3:
        if 'sys' == sys.argv[1]:
            if 'start' == sys.argv[2]:
                sysagent.start()
            elif 'stop' == sys.argv[2]:
                sysagent.stop()
            elif 'status' == sys.argv[2]:
                sysagent.status()
            elif 'restart' == sys.argv[2]:
                sysagent.restart()
            else:
                print("Unknown command")
                sys.exit(2)
        elif 'swift' == sys.argv[1]:
            if 'start' == sys.argv[2]:
                swiftagent.start()
            elif 'stop' == sys.argv[2]:
                swiftagent.stop()
            elif 'status' == sys.argv[2]:
                swiftagent.status()
            elif 'restart' == sys.argv[2]:
                swiftagent.restart()
            else:
                print("Unknown command")
                sys.exit(2)
        elif 'server' == sys.argv[1]:
            if 'start' == sys.argv[2]:
                server.start()
            elif 'stop' == sys.argv[2]:
                server.stop()
            elif 'status' == sys.argv[2]:
                server.status()
            elif 'restart' == sys.argv[2]:
                server.restart()
            else:
                print("Unknown command")
                sys.exit(2)
        elif 'heart' == sys.argv[1]:
            if 'start' == sys.argv[2]:
                heart.start()
            elif 'stop' == sys.argv[2]:
                heart.stop()
            elif 'status' == sys.argv[2]:
                heart.status()
            elif 'restart' == sys.argv[2]:
                heart.restart()
            else:
                print("Unknown command")
                sys.exit(2)
        elif 'all' == sys.argv[1]:
            if 'start' == sys.argv[2]:
                tsy = threading.Thread(target=sysagent.start)
                tsw = threading.Thread(target=swiftagent.start)
                tsr = threading.Thread(target=server.start)
                tht = threading.Thread(target=heart.start)
                for t in [tsy, tsw, tsr, tht]:
                    t.start()
            elif 'stop' == sys.argv[2]:
                sysagent.stop()
                swiftagent.stop()
                server.stop()
                heart.stop()
            elif 'status' == sys.argv[2]:
                tsy = threading.Thread(target=sysagent.status)
                tsw = threading.Thread(target=swiftagent.status)
                tsr = threading.Thread(target=server.status)
                tht = threading.Thread(target=heart.status)
                for t in [tsy, tsw, tsr, tht]:
                    t.start()
            elif 'restart' == sys.argv[2]:
                tsy = threading.Thread(target=sysagent.restart)
                tsw = threading.Thread(target=swiftagent.restart)
                tsr = threading.Thread(target=server.restart)
                tht = threading.Thread(target=heart.restart)
                for t in [tsy, tsw, tsr, tht]:
                    t.start()
            else:
                print("Unknown command")
                sys.exit(2)
        else:
            print("Unknown command")
            sys.exit(2)
    else:
        print("usage: %s %s start|stop|restart|status" % (sys.argv[0], 'sys|swift|task|all'))
        sys.exit(2)


if __name__ == '__main__':
    main()