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

import os
import shutil
from flask import request
from sfo_server import manager_class
from sfo_server.models import SfoClusterNodesMethod
from flask_restful import Resource
from sfo_server.resource.common import used_time
from configparser import NoSectionError, ConfigParser
from collections import OrderedDict
from sfo_server import access_logger
from sfo_server.decorate import login_required, permission_required
from sfo_common.config_parser import Config


global_config = Config()


def cluster_swift_config_logic(hostname, filename=None):
    """
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    host = SfoClusterNodesMethod.query_host_by_host_name(hostname)
    if not host:
        raise ValueError('not Node hostname is %s' % hostname)
    if filename:
        node_man = manager_class.NodeManager(host.node_inet_ip)
        content = node_man.swift_config.read_config(config_path=os.path.dirname(filename),
                                                    config_file=os.path.basename(filename))
        config = ConfigParser()
        config.read_string(content)
        config_dict = OrderedDict()
        try:
            if config.defaults():
                default_config = config.defaults()
                config_dict[config.default_section] = default_config
            for section, option in config.items():
                if config.has_section(section):
                    section_copy = config._sections[section].copy()
                    config_dict[section] = section_copy
        except NoSectionError, error:
            access_logger.error('get exception %s from swift config' % str(error))
        status = 200
        message = 'OK'
        data = {"config": config_dict}
    else:
        filenames = []
        node_man = manager_class.NodeManager(host.node_inet_ip)
        etc_swift_conf = node_man.swift_config.list_dir()
        etc_swift_conf_files = map(lambda x: '/etc/swift/%s' % x,
                                   filter(lambda x: x.endswith('.conf'), etc_swift_conf.split('\n')))
        filenames.extend(etc_swift_conf_files)
        server_conf_list = filter(lambda x: x.endswith('-server'), etc_swift_conf.split('\n'))
        for server_dir in server_conf_list:
            server_swift_conf_list = node_man.swift_config.list_dir(config_path='/etc/swift/%s' % server_dir)
            filter_conf_file = filter(lambda x: x.endswith('.conf'), server_swift_conf_list.split('\n'))
            confs = map(lambda x: '/etc/swift/%s/%s' % (server_dir, x), filter_conf_file)
            filenames.extend(confs)

        rsync_conf = node_man.swift_config.list_dir(config_path='/etc')
        rsync_conf_files = map(lambda x: '/etc/%s' % x,
                               filter(lambda x: x.startswith('rsync') and x.endswith('.conf')
                                      and not x.startswith('rsyncd'),
                                      rsync_conf.split('\n')))

        filenames.extend(rsync_conf_files)
        status = 200
        message = 'OK'
        data = filenames
    resp.update({"status": status, "message": message, "data": data})
    return resp, status


def update_swift_config_logic(hostname, filename, **sections):
    """
    更新配置文件逻辑
    :param hostname:
    :param filename:
    :param sections:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    host = SfoClusterNodesMethod.query_host_by_host_name(hostname)
    if not host:
        raise ValueError('not Node hostname is %s' % hostname)
    node_man = manager_class.NodeManager(host.node_inet_ip)
    content = node_man.swift_config.read_config(config_path=os.path.dirname(filename),
                                                config_file=os.path.basename(filename))
    config = ConfigParser()
    config.read_string(content)
    for section in sections:
        if section.upper() == 'DEFAULT':
            for key, value in sections[section].items():
                if config.defaults().has_key(key):
                    config.defaults()[key] = value
                else:
                    config.defaults().setdefault(key, value)
        else:
            if config.has_section(section):
                for key, value in sections[section].items():
                    config.set(section=section, option=key, value=value)
            else:
                config.add_section(section)
                for key, value in sections[section].items():
                    config.set(section=section, option=key, value=value)
    if not os.path.exists('%s/%s/' % (global_config.sfo_server_temp_file, host.node_inet_ip)):
        os.makedirs('%s/%s/' % (global_config.sfo_server_temp_file, host.node_inet_ip))
    else:
        if os.path.exists('%s/%s/%s' % (global_config.sfo_server_temp_file, host.node_inet_ip, filename)):
            shutil.copy('%s/%s/%s' % (global_config.sfo_server_temp_file, host.node_inet_ip, filename),
                        '%s/%s/%s.bak' % (global_config.sfo_server_temp_file, host.node_inet_ip, filename))
    with open('%s/%s/%s' % (global_config.sfo_server_temp_file, host.node_inet_ip, filename), mode='w+') as fp:
        config.write(fp=fp)
    content = node_man.swift_config.write_config(os.path.basename(filename))
    copy_content = node_man.swift_config.copy(old_path='/tmp/sfo',
                                              config_path=os.path.dirname(filename),
                                              config_file=os.path.basename(filename))
    if content == 'Send File Success' and copy_content == 'Excute Cmd Success':
        status = 200
        message = 'OK'
    else:
        status = 500
        message = 'Update Config Fail %s %s' % (content, copy_content)
    resp.update({"status": status, "message": message})
    return resp, status


class SwiftConfigAPI(Resource):

    """
    swift配置 相关api
    response :
        { 'status': 200/404 , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]
    resource = (SfoClusterNodesMethod,)

    @used_time
    @login_required
    @permission_required(*resource)
    def get(self):
        hostname = request.args.get('hostname', '')
        filename = request.args.get('filename', '')
        try:
            resp, status = cluster_swift_config_logic(hostname, filename)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {"status": status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {"status": status, "message": message}, status

    @login_required
    @permission_required(*resource)
    def put(self):
        try:
            config_json = request.json
            hostname = config_json.get('hostname')
            filename = config_json.get('filename')
            sections = config_json.get('sections')
            resp, status = update_swift_config_logic(hostname, filename, **sections)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {"status": status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {"status": status, "message": message}, status