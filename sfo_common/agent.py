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

class Agent:
    '''
    初始化守护进程类
    '''
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null',home_dir='/', umask=022, verbose=1):
        self.pidfile = pidfile
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.home_dir = home_dir
        self.verbose = verbose  # 调试开关
        self.umask = umask
        self.daemon_alive = True

    def init_agent(self):
        '''
        守护进程初始化
        :return:
        '''
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            logger.error("fork #1 failed: {} ({})".format(e.errno, e.strerror))
            sys.stderr.write("fork #1 failed: {} ({})".format(e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir(self.home_dir)
        os.setsid()
        os.umask(self.umask)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            logger.error("fork #2 failed: {} ({})".format(e.errno, e.strerror))
            sys.stderr.write("fork #2 failed: {} ({})".format(e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        if self.stderr:
            se = file(self.stderr, 'a+', 0)
        else:
            se = so

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        def sig_handler(signum, frame):
            self.daemon_alive = False
        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        #设置0号CPU亲和
        try:
            os.system("taskset -pc 0 %s"%pid)
        except Exception,ex:
            pass
        logger.info("write pid : {} to pidfile : {}".format(pid, self.pidfile))
        pf = file(self.pidfile, 'w+')
        pf.write('%s\n' % pid)
        pf.close()

    # delete pid
    def delpid(self):
        '''
        删除pid文件
        :return:
        '''
        if os.path.exists(self.pidfile):
            self.stop()
            os.remove(self.pidfile)
        logger.info("do pid : {} os remove({})".format(str(os.getpid()), self.pidfile))

    # start agent
    def start(self):
        '''
        启动守护进程
        :return:
        '''
        # Check for a pidfile to see if the agnet already runs
        try:
            pf = file(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
        try:
            if pid:
                message = "pidfile {} already exist. agent is running."
                sys.stdout.write(message.format(self.pidfile))
                sys.exit(0)
            # Start the agent
            self.init_agent()
            self.run()
        except Exception as ex:
            logger.info(ex)


    def stop(self):
        '''
        停止守护进程
        停止时退出进程组中的所有进程
        :return:
        '''
        # stop the agent from the pidfile
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile {} does not exist. agnet is not running."
            sys.stdout.write(message.format(self.pidfile))
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
            return  # not an error in a restart

        # Try killing the agent process
        try:
            nbocc = 0
            while 1:
                logger.info("try to kill process: {}".format(str(pid)))
                os.killpg(os.getpgid(pid), signal.SIGKILL)
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                nbocc = nbocc + 1
                if nbocc % 5 == 0:
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
                    os.kill(pid, signal.SIGHUP)
        except OSError as e:
            err = str(e)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                    logger.info("pid : {} delete pidfile : {}".format(str(os.getpid()), self.pidfile))
            else:
                print(str(err))
                sys.exit(1)

    #restart agent
    def restart(self):
        '''
        守护进程重启
        :return:
        '''
        self.stop()
        self.start()

    #status check
    def status(self):
        '''
        守护进程状态查看
        :return:
        '''
        try:
            pf = open(self.pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
            sys.exit(2)
        except SystemExit:
            pid = None
            sys.exit()

        if psutil.pid_exists(pid):
            print("process is running, pid is %s" % str(pid))
            sys.exit(0)
        else:
            print("no such process running")
            sys.exit(2)

    #agent run
    def run(self):
        """
        You should override this method when you subclass agent. It will be called after the process has been
        InitAgent by start() or restart().
        """