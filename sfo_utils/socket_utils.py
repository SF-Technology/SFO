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
import errno
import socket


class LocalProcessSocketServer:

    def __init__(self, host, port, buffers=1024):
        self.soc_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffers = buffers
        self.soc_server.bind((host, port))
        self.soc_server.listen(10)


class LocalProcessSocketClient:

    def __init__(self, host, port, buffers=1024):
        self.soc_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.buffers = buffers
        self.soc_server.connect((host, port))

    def send(self, data):
        if data:
            try:
                self.soc_server.send(data)
            except Exception, error:
                if error.errno == errno.ECONNRESET:
                    pass
                elif error.errno == errno.EWOULDBLOCK:
                    pass
                else:
                    print error