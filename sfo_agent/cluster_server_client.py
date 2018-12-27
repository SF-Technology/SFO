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

from sfo_common.agent import Agent
from sfo_common.import_common import *
logger = logging.getLogger("server")

class ClusterCommandHandler(asyncore.dispatcher_with_send):
    '''
    命令处理类
    '''
    def handle_read(self):
        '''
        接收socket发送过来的命令数据
        :return:
        '''
        data = self.recv(1024)
        self.out_buffer += data

    def writable(self):
        return len(self.out_buffer) > 0

    def handle_write(self):
        '''
        执行命令并返回结果
        :return:返回命令执行结果
        '''
        try:
            if len(self.out_buffer) > 0:
                if len(self.out_buffer) > 1024:
                    excute_cmd = ''
                    while len(self.out_buffer) > 0:
                        cmdstr = self.out_buffer[:1024]
                        if util.is_json(cmdstr):
                            param = json.loads(cmdstr, encoding='utf-8')
                            excute_cmd += param['cmd']
                        self.out_buffer = self.out_buffer[1024:]
                    logger.info('you want to excute command {}'.format(str(excute_cmd)))
                    result = util.excute_command(excute_cmd)
                    if len(result) > 512:
                        while 1:
                            rec = result[:512]
                            result = result[512:]
                            if not result:
                                if len(rec) > 0:
                                    self.send(bytes(rec))
                                    logger.info(rec)
                                break
                            self.send(bytes(rec))
                            logger.info(rec)
                    else:
                        rec = result[:512]
                        self.send(bytes(rec))
                        logger.info(rec)
                else:
                    if util.is_json(self.out_buffer):
                        bsize = len(self.out_buffer)
                        param = json.loads(self.out_buffer, encoding='utf-8')
                        self.out_buffer = self.out_buffer[bsize:]
                        if param.has_key('cmd'):
                            logger.info('you want to excute command {}'.format(str(param['cmd'])))
                            result = util.excute_command(param['cmd'])
                            if len(result) > 512:
                                while 1:
                                    rec = result[:512]
                                    result = result[512:]
                                    if not result:
                                        if len(rec) > 0:
                                            self.send(bytes(rec))
                                            logger.info(rec)
                                        break
                                    self.send(bytes(rec))
                                    logger.info(rec)
                            else:
                                rec = result[:512]
                                self.send(bytes(rec))
                                logger.info(rec)
                        else:
                            self.send('Error params')
                            logger.info('Error params')
        except Exception as ex:
            logger.exception('caomman server send result exception:'.format(str(ex)))
        finally:
            self.handle_close()


# 处理命令的服务器
class ClusterCommandServer(asyncore.dispatcher):
    '''
    处理命令的socket server
    '''
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        port = config.sock_cmd_port
        self.bind(('0.0.0.0', port))
        self.listen(5)

    def handle_accept(self):
        '''
        接收socket 连接
        :return:
        '''
        pair = self.accept()
        if pair is not None:
            conn, addr = pair
            logger.info('Incoming connection from %s' % repr(addr))
            handler = ClusterCommandHandler(conn)

class ClusterFileHandler(asyncore.dispatcher_with_send):
    '''
    文件传输处理类
    '''
    def handle_read(self):
        '''
        接收传输的文件数据
        :return:
        '''
        while 1:
            fileinfo_size = struct.calcsize('>128sl')
            buf = self.recv(fileinfo_size)
            if buf:
                filename, filesize = struct.unpack('>128sl', buf)
                fn = filename.strip('\00')
                util.ensure_dir(config.temp_file)
                new_filename = os.path.join(config.temp_file, fn)
                if os.path.exists(new_filename):
                    os.remove(new_filename)
                logger.info('file new name is {0}, filesize is {1} Bytes'.format(new_filename, filesize))
                recvd_size = 0  # 定义已接收文件的大小
                fp = open(new_filename, 'wb')

                while not recvd_size == filesize:
                    try:
                        if filesize - recvd_size > 1024:
                            data = self.recv(1024)
                            recvd_size += len(data)
                        else:
                            data = self.recv(filesize - recvd_size)
                            recvd_size = filesize
                    except IOError,error:
                        if error.errno == errno.EWOULDBLOCK:
                            pass
                    else:
                        fp.write(data)
                fp.close()
                self.out_buffer = fn
            break

    def handle_write(self):
        '''
        发送文件传输结果
        :return:
        '''
        try:
            res = {}
            if len(self.out_buffer) > 0:
                res['file'] = self.out_buffer
                self.out_buffer = ''
                res['status'] = 'OK'
                res['result'] = 'File receive compeled'
                rec = json.dumps(res, encoding='utf-8', ensure_ascii=True)
                self.send(rec)
                logger.info(rec)
        except socket.error as e:
            self.handle_close()
            raise e
        finally:
            self.handle_close()


# 处理传输文件的服务器
class ClusterFileServer(asyncore.dispatcher):
    '''
    处理文件的socket server
    '''
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        port = config.sock_file_port
        self.bind(('0.0.0.0', port))
        self.listen(5)

    def handle_accept(self):
        '''
        接收文件传输socket 连接
        :return:
        '''
        pair = self.accept()
        if pair is not None:
            conn, addr = pair
            logger.info('Incoming connection from %s' % repr(addr))
            handler = ClusterFileHandler(conn)


class ClusterClient(asyncore.dispatcher):
    '''
    socket client
    '''
    def __init__(self, host='127.0.0.1', port=9999, message=None, filepath=None):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.message = message
        self.filepath = filepath
        self.buffer = '__wait__'
        self.content = ''
        self.connect((self.host, self.port))

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        '''
        接收socket server发送过来的数据
        :return:
        '''
        try:
            data = self.recv(512)
            if len(data) > 0 and len(data) < 512:
                self.buffer += data
                self.handle_close()
            else:
                self.buffer += data
        except IOError, error:
            if error.errno == errno.EWOULDBLOCK:
                pass

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        '''
        发送数据到连接的socket server
        :return:
        '''
        if self.message:
            cmds = {}
            sent_size = 1014  # 拼接后json化会加上10个字符
            if len(self.message[:sent_size]) > 0:
                cmds['cmd'] = self.message[:sent_size]
                cmdstr = json.dumps(cmds, encoding='utf-8', ensure_ascii=True)
                sent = self.send(cmdstr)
                self.message = self.message[sent_size:]
                # 确保writable为True
                self.buffer = self.message[sent_size:]
        # 传输文件
        if self.filepath:
            while True:
                if os.path.isfile(self.filepath):
                    # 定义定义文件信息。128s表示文件名为128bytes长，l表示一个int或log文件类型，在此为文件大小
                    fileinfo_size = struct.calcsize('>128sl')
                    # 定义文件头信息，包含文件名和文件大小
                    fhead = struct.pack('>128sl', str(os.path.basename(self.filepath)),os.stat(self.filepath).st_size)
                    self.send(fhead)
                    logger.info('client filepath: {0}'.format(self.filepath))

                    with open(self.filepath, 'rb') as fp:
                        while 1:
                            data = fp.read(1024)
                            if not data:
                                logger.info('{0} file send over...'.format(self.filepath))
                                self.filepath = None
                                self.buffer = ''
                                break
                            self.send(data)
                break
        if self.buffer:
            if self.buffer == '__wait__':
                self.buffer = ''
            else:
                pass

def start_comman_server():
    '''
    启动命令执行server
    :return:
    '''
    server = ClusterCommandServer()
    asyncore.loop()

def start_file_server():
    '''
    启动文件传输server
    :return:
    '''
    server = ClusterFileServer()
    asyncore.loop()

def handler(signum):
    logger.info("Signal handler called with signal, {}. Set the internal flag to true for Event.".format(signum))
    evt.set()

class ServerAgent(Agent):
    def __init__(self, pidfile):
        Agent.__init__(self, pidfile)

    def run(self):
        '''
        重写run函数，启动server服务
        :return:
        '''
        signal.signal(signal.SIGTERM, handler)
        server1 = multiprocessing.Process(target=start_comman_server)
        server1.start()
        logger.info('the pid of start_comman_server is %s'%(str(server1.pid)))
        server2 = multiprocessing.Process(target=start_file_server)
        server2.start()
        logger.info('the pid of start_file_server is %s' % (str(server2.pid)))
        while not evt.isSet():
            evt.wait(600)
        logger.info("ServerAgent stoped")

if __name__ == '__main__':
    agent = ServerAgent(config.server_agnet_pfile)
    try:
        if len(sys.argv) == 3:
            if 'server' == sys.argv[1]:
                if 'start' == sys.argv[2]:
                    agent.start()
                if 'stop' == sys.argv[2]:
                    agent.stop()
            elif 'client' == sys.argv[1]:
                if 'start' == sys.argv[2]:
                    client = ClusterClient(host='192.168.1.1', port=config.sock_cmd_port, message='pkill swift')
                    #client = ClusterClient(host='192.168.1.1', port=config.sock_file_port, filepath='/tmp/123/1.txt')
                    asyncore.loop()
                    print client.buffer
            else:
                print("Unknown command")
                sys.exit(2)
        else:
            print("usage: %s" % (sys.argv[0],))
            sys.exit(2)
    except Exception as ex:
        logger.info("cluster server client run exception:" + str(ex))
