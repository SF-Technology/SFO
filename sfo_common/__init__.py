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
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sfo_common.config_parser import *


config = Config()
sfo_datahandler = Flask(__name__)
sfo_datahandler.config['SECRET_KEY'] ='=QSXFGHSgdnghiodhgwoernRGHH='
sfo_datahandler.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8'% (config.mysql_user,config.mysql_passwd,config.mysql_host,config.mysql_port,config.mysql_dbname)
sfo_datahandler.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']=False #设置这一项是每次请求结束后都会自动提交数据库中的变动
sfo_datahandler.config['SQLALCHEMY_POOL_RECYCLE']=5 # 如果出现连接失败的情况,会在建立连接5秒后回收连接对象,保证下次连接时,不会因为上一次连接对象仍然存在而导致执行SQL不成功
sfo_datahandler.config['SQLALCHEMY_POOL_SIZE']= 20 # 最大连接数
sfo_datahandler.config['SQLALCHEMY_MAX_OVERFLOW']= 20 # 最大连接数
db = SQLAlchemy(sfo_datahandler) #实例化


