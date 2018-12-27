#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import socket
import logging.config
from sfo_common.config_parser import Config
from sfo_server.models import SfoCofigureMethod
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir))
import socket
from sfo_server.models import SfoClusterNodesMethod, SfoCofigureMethod

def getLogger(name=''):
    """
    返回日志对象 Logger
    :param name: 配置内的key
    :return: Logger
    """
    config = Config()
    logging.config.fileConfig(config.logging_conf)
    logger = logging.getLogger(name) if name else logging
    return logger


access_logger = getLogger('access')
# access_logger = logging
script_path = SfoCofigureMethod.query_value_from_con_key('script_path')
SCRIPT_PATH = script_path.config_value if script_path else '/app/sfo-agent/scripts'
SCRIPT_PATH = SCRIPT_PATH.rstrip('/')
PROXY_HOST_IP = SfoCofigureMethod.query_value_from_con_key('proxy_host_ip')
PROXY_HOST_IP = PROXY_HOST_IP.config_value if PROXY_HOST_IP else socket.gethostbyname(socket.gethostname())