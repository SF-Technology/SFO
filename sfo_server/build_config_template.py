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
import re

import json
from collections import OrderedDict
from configparser import ConfigParser, NoSectionError
from backports.configparser import MissingSectionHeaderError
from sfo_server.models import SfoClusterConfigureMethod, db
from sfo_server import access_logger
#
_UNSET = object()

class NoCopyDefaultConfigParser(ConfigParser):

    def items(self, section=_UNSET, raw=False, vars=None):
        if section is _UNSET:
            return super(ConfigParser, self).items()
        d = {}
        try:
            d.update(self._sections[section])
        except KeyError:
            if section != self.default_section:
                raise NoSectionError(section)
        # Update with the entry specific variables
        if vars:
            for key, value in vars.items():
                d[self.optionxform(key)] = value
        value_getter = lambda option: self._interpolation.before_get(self,
            section, option, d[option], d)
        if raw:
            value_getter = lambda option: d[option]
        return [(option, value_getter(option)) for option in d.keys()]


def exist_configs_dict():
    """
    先系统存在的基本配置信息 ， 防止重复写入
    :return:
    """
    exist_config = {}
    _exist_configs = SfoClusterConfigureMethod.query.all()
    for con in _exist_configs:
        if con.config_filename not in exist_config.keys():
            exist_config[con.config_filename] = {}
            exist_config[con.config_filename][con.config_group] = {}
            if con.config_key:
                exist_config[con.config_filename][con.config_group][con.config_key] = con.config_value
        else:
            if con.config_group in exist_config[con.config_filename] and con.config_key:
                exist_config[con.config_filename][con.config_group][con.config_key] = con.config_value
            else:
                exist_config[con.config_filename][con.config_group] = {}
                if con.config_key:
                    exist_config[con.config_filename][con.config_group][con.config_key] = con.config_value
    return exist_config


def init_default_config(filename, config):
    """
    :param filename:
    :param config:
    :return:
    """
    exist_configs = exist_configs_dict()
    if config.defaults().items():
        for item in config.defaults().items():
            if config.default_section in exist_configs.get(filename, ''):
                if item[0] in exist_configs[filename].get(config.default_section, ''):
                    break
            sfo_clus_con = SfoClusterConfigureMethod.create_cluster_config(filename,
                                                                           config.default_section,
                                                                           item[0], item[1])
            db.session.add(sfo_clus_con)
    db.session.commit()


def init_config(filename, config,):
    exist_configs = exist_configs_dict()
    con_sec = config.sections()
    for sec in con_sec:
        items = config.items(sec)
        if items:
            for item in items:
                if sec in exist_configs.get(filename, ''):
                    if item[0] in exist_configs[filename].get(sec, ''):
                        break
                sfo_clus_con = SfoClusterConfigureMethod.create_cluster_config(filename,
                                                                               sec,
                                                                               item[0], item[1])
                db.session.add(sfo_clus_con)

        else:
            if sec in exist_configs.get(filename, ''):
                break
            sfo_clus_con = SfoClusterConfigureMethod.create_cluster_config(filename, sec, '', '')
            db.session.add(sfo_clus_con)
    db.session.commit()


def init_unstandard_config(filename, file_dir):
    exist_configs = exist_configs_dict()
    has_section_header = ''
    with open(os.path.join(file_dir, filename), 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            cmp = re.compile(r"\[([^\[\]]*)\]")
            result = cmp.search(line)
            if result:
                has_section_header = result.groups()[0]
            else:
                if has_section_header:
                    try:
                        key, value = line.split('=', 1)
                        value = value.strip('\n')
                        if has_section_header in exist_configs.get(filename, ''):
                            file_dict = exist_configs.get(filename, '')
                            if file_dict and key in file_dict.get(has_section_header, ''):
                                break
                        sfo_clus_con = SfoClusterConfigureMethod.create_cluster_config(filename,
                                                                                       has_section_header,
                                                                                       key, value)
                        db.session.add(sfo_clus_con)
                    except ValueError:
                        key, value = line.split(' ', 1)

                        if has_section_header in exist_configs.get(filename, ''):
                            file_dict = exist_configs.get(filename, '')
                            if file_dict and key in file_dict.get(has_section_header, ''):
                                break
                        sfo_clus_con = SfoClusterConfigureMethod.create_cluster_config(filename,
                                                                                       has_section_header,
                                                                                       key, value)
                        db.session.add(sfo_clus_con)
                else:
                    try:
                        key, value = line.split('=', 1)
                        value = value.strip('\n')

                        if has_section_header in exist_configs.get(filename, ''):
                            file_dict = exist_configs.get(filename, '')
                            if file_dict and key in file_dict.get(has_section_header, ''):
                                break
                        sfo_clus_con = SfoClusterConfigureMethod.create_cluster_config(filename,
                                                                                       '',
                                                                                       key+'=', value)
                        db.session.add(sfo_clus_con)
                    except ValueError:
                        key, value = line.split(' ', 1)
                        if has_section_header in exist_configs.get(filename, ''):
                            file_dict = exist_configs.get(filename, '')
                            if file_dict and key in file_dict.get(has_section_header, ''):
                                break
                        sfo_clus_con = SfoClusterConfigureMethod.create_cluster_config(filename,
                                                                                       '',
                                                                                       key, value)
                        db.session.add(sfo_clus_con)



def init_cluster_config(dir_file):
    for sample_path in os.listdir(dir_file):
        config_standard = NoCopyDefaultConfigParser()
        try:
            config_standard.read(os.path.join(dir_file, sample_path))
            init_default_config(sample_path, config_standard)
            init_config(sample_path, config_standard)
        except MissingSectionHeaderError:
            init_unstandard_config(sample_path, dir_file)

def create_new_config_file(build_filepath, node, **kwargs):
    will_create_files = []
    filenames = SfoClusterConfigureMethod.query_group_by_filename()
    filenames = map(lambda x: x.config_filename, filenames)
    node_role = json.loads(node.node_role)
    node_srv = map(lambda x: x.lower().split('-')[0], filter(lambda x: node_role[x] == 'YES', node_role))
    for srv in node_srv:
        create_filenames = filter(lambda x: srv in x and x.startswith(srv), filenames)
        will_create_files.extend(create_filenames)
    else:
        _conf_files = filter(
            lambda x: x.startswith('account') or x.startswith('container') or x.startswith('object') or x.startswith(
                'proxy'), filenames)
        if len(node_srv) == 1 and node_srv[0] == 'proxy':
            will_create_files.extend(set(filenames) - set(_conf_files))
            try:
                will_create_files.remove('rsyncd.conf')
            except ValueError, error:
                try:
                    will_create_files.remove('rsync.conf')
                except ValueError, error:
                    access_logger.error(str(error))
                access_logger.error(str(error))
        else:
            will_create_files.extend(set(filenames) - set(_conf_files))
    #根据角色的不同过滤发送的文件
    for file in will_create_files:
        configs = SfoClusterConfigureMethod.query_by_filename(file)
        sections = SfoClusterConfigureMethod.query_group_by_config_group(file)
        config_parser = ConfigParser()
        config_parser.default_section = 'null'
        no_section_dict = OrderedDict()
        #由于默认编辑的时候DEFAULT的section是不合法的,所以将默认的DEFAULT改成 ！DEFAULT字符串即可
        for config in configs:
            section = config.config_group
            if section:
                if not config_parser.has_section(section):
                    config_parser.add_section(section)
                if config.config_key:
                    if kwargs.get(config.config_value):
                        config_parser.set(section, config.config_key, kwargs[config.config_value])
                    else:
                        config_parser.set(section, config.config_key, config.config_value)
            else:
                if kwargs.get(config.config_value):
                    no_section_dict[config.config_key] = kwargs[config.config_value]
                else:
                    no_section_dict[config.config_key] = config.config_value
        if no_section_dict:
            with open(os.path.join(build_filepath, file), "w") as fp:
                for key, value in no_section_dict.items():
                    fp.write('%s%s\n' % (key, value))
        if config_parser.sections():
            if len(sections) != len(config_parser.sections()):
                config_parser.write(open(os.path.join(build_filepath, file), "a+"))
            else:
                config_parser.write(open(os.path.join(build_filepath, file), "w"))
    return will_create_files


def create_new_config_specify_file(filename, build_filepath, **kwargs):
    configs = SfoClusterConfigureMethod.query_by_filename(filename=filename)
    if configs:
        sections = SfoClusterConfigureMethod.query_group_by_config_group(filename)
        config_parser = ConfigParser()
        config_parser.default_section = 'null'
        no_section_dict = OrderedDict()
        # 由于默认编辑的时候DEFAULT的section是不合法的,所以将默认的DEFAULT改成 ！DEFAULT字符串即可
        for config in configs:
            section = config.config_group
            if section:
                if not config_parser.has_section(section):
                    config_parser.add_section(section)
                if config.config_key:
                    if kwargs.get(config.config_value):
                        config_parser.set(section, config.config_key, kwargs[config.config_value])
                    else:
                        config_parser.set(section, config.config_key, config.config_value)
            else:
                if kwargs.get(config.config_value):
                    no_section_dict[config.config_key] = kwargs[config.config_value]
                else:
                    no_section_dict[config.config_key] = config.config_value
        if no_section_dict:
            with open(os.path.join(build_filepath, filename), "w") as fp:
                for key, value in no_section_dict.items():
                    fp.write('%s%s\n' % (key, value))
        if config_parser.sections():
            if len(sections) != len(config_parser.sections()):
                config_parser.write(open(os.path.join(build_filepath, filename), "a+"))
            else:
                config_parser.write(open(os.path.join(build_filepath, filename), "w"))
        return True
    else:
        return None
