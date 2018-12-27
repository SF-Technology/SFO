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

from sfo_common import db


class SfoCluster(db.Model):
    __tablename__ = 'sfo_cluster'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=False, unique=True)
    creater = db.Column(db.String(128), nullable=False)
    cluster_stat = db.Column(db.String(128))
    extend = db.Column(db.Text)
    add_time = db.Column(db.String(128))

    def __repr__(self):
        return '<SfoCluster %s>' % self.cluster_name


class SfoClusterInfo(db.Model):
    __tablename__ = 'sfo_cluster_info'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=False)
    proxy_num = db.Column(db.String(128), nullable=True)
    storage_num = db.Column(db.String(256), nullable=True)
    disk_num = db.Column(db.String(128), nullable=True)
    capacity_total = db.Column(db.String(128), nullable=True)
    band_width = db.Column(db.String(128), nullable=True)
    cluster_iops = db.Column(db.String(128), nullable=True)
    account_num = db.Column(db.String(128), nullable=True)
    container_num = db.Column(db.String(128), nullable=True)
    object_num = db.Column(db.String(128), nullable=True)
    uri_total = db.Column(db.String(128), nullable=True)
    uri_success_num = db.Column(db.String(128), nullable=True)
    uri_fail_num = db.Column(db.String(128), nullable=True)
    uri_response_time = db.Column(db.String(128), nullable=True)
    auditor_queue = db.Column(db.String(1024), nullable=True)
    replicate_num = db.Column(db.String(1024), nullable=True)
    update_num = db.Column(db.String(1024), nullable=True)
    sync_num = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoClusterInfo %s>' % self.cluster_name

class SfoClusterInfo_hour(db.Model):
    __tablename__ = 'sfo_cluster_info_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=False)
    proxy_num = db.Column(db.String(128), nullable=True)
    storage_num = db.Column(db.String(256), nullable=True)
    disk_num = db.Column(db.String(128), nullable=True)
    capacity_total = db.Column(db.String(128), nullable=True)
    band_width = db.Column(db.String(128), nullable=True)
    cluster_iops = db.Column(db.String(128), nullable=True)
    account_num = db.Column(db.String(128), nullable=True)
    container_num = db.Column(db.String(128), nullable=True)
    object_num = db.Column(db.String(128), nullable=True)
    uri_total = db.Column(db.String(128), nullable=True)
    uri_success_num = db.Column(db.String(128), nullable=True)
    uri_fail_num = db.Column(db.String(128), nullable=True)
    uri_response_time = db.Column(db.String(128), nullable=True)
    auditor_queue = db.Column(db.String(1024), nullable=True)
    replicate_num = db.Column(db.String(1024), nullable=True)
    update_num = db.Column(db.String(1024), nullable=True)
    sync_num = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoClusterInfo_hour %s>' % self.cluster_name

class SfoClusterInfo_day(db.Model):
    __tablename__ = 'sfo_cluster_info_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=False)
    proxy_num = db.Column(db.String(128), nullable=True)
    storage_num = db.Column(db.String(256), nullable=True)
    disk_num = db.Column(db.String(128), nullable=True)
    capacity_total = db.Column(db.String(128), nullable=True)
    band_width = db.Column(db.String(128), nullable=True)
    cluster_iops = db.Column(db.String(128), nullable=True)
    account_num = db.Column(db.String(128), nullable=True)
    container_num = db.Column(db.String(128), nullable=True)
    object_num = db.Column(db.String(128), nullable=True)
    uri_total = db.Column(db.String(128), nullable=True)
    uri_success_num = db.Column(db.String(128), nullable=True)
    uri_fail_num = db.Column(db.String(128), nullable=True)
    uri_response_time = db.Column(db.String(128), nullable=True)
    auditor_queue = db.Column(db.String(1024), nullable=True)
    replicate_num = db.Column(db.String(1024), nullable=True)
    update_num = db.Column(db.String(1024), nullable=True)
    sync_num = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoClusterInfo_day %s>' % self.cluster_name


class SfoClusterNodes(db.Model):
    __tablename__ = 'sfo_cluster_node'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    node_host_name = db.Column(db.String(128), nullable=True)
    node_inet_ip = db.Column(db.String(128), nullable=True)
    node_replicate_ip = db.Column(db.String(128), nullable=True)
    node_role = db.Column(db.String(128), nullable=True)
    node_stat = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoClusterNode %s>' % self.node_host_name


class SfoClusterSrvs(db.Model):
    __tablename__ = 'sfo_cluster_srv'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=False)
    node_host_name = db.Column(db.String(128), nullable=False)
    service_name = db.Column(db.String(128), nullable=False)
    is_rely_software = db.Column(db.String(128))
    srv_stat = db.Column(db.String(128), default='1')
    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoClusterSrvs %s -- %s >' % (self.node_host_name,self.service_name)


class SfoClusterAccounts(db.Model):
    __tablename__ = 'sfo_cluster_accounts'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    account_name = db.Column(db.String(128), nullable=True)
    account_passwd = db.Column(db.String(128), nullable=True)
    system_code = db.Column(db.String(128), nullable=True)
    system_name = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoClusterAccounts %s>' % self.cluster_name


class SfoDiskPerform(db.Model):
    __tablename__ = 'sfo_disk_perform_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    disk_uuid = db.Column(db.String(1024), nullable=False)
    disk_name = db.Column(db.String(1024), nullable=True)
    disk_total = db.Column(db.String(128), nullable=True)
    disk_used = db.Column(db.String(1024), nullable=True)
    disk_free = db.Column(db.String(1024), nullable=True)
    disk_percent = db.Column(db.String(1024), nullable=True)
    read_count = db.Column(db.String(1024), nullable=True)
    write_count = db.Column(db.String(1024), nullable=True)
    read_bytes = db.Column(db.String(1024), nullable=True)
    write_bytes = db.Column(db.String(1024), nullable=True)
    read_time = db.Column(db.String(1024), nullable=True)
    write_time = db.Column(db.String(1024), nullable=True)
    read_merged_count = db.Column(db.String(1024), nullable=True)
    write_merged_count = db.Column(db.String(1024), nullable=True)
    busy_time = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoDiskPerform %s>' % self.guid

class SfoDiskPerform_5min(db.Model):
    __tablename__ = 'sfo_disk_perform_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    disk_uuid = db.Column(db.String(1024), nullable=False)
    disk_name = db.Column(db.String(1024), nullable=True)
    disk_total = db.Column(db.String(128), nullable=True)
    disk_used = db.Column(db.String(1024), nullable=True)
    disk_free = db.Column(db.String(1024), nullable=True)
    disk_percent = db.Column(db.String(1024), nullable=True)
    read_count = db.Column(db.String(1024), nullable=True)
    write_count = db.Column(db.String(1024), nullable=True)
    read_bytes = db.Column(db.String(1024), nullable=True)
    write_bytes = db.Column(db.String(1024), nullable=True)
    read_time = db.Column(db.String(1024), nullable=True)
    write_time = db.Column(db.String(1024), nullable=True)
    read_merged_count = db.Column(db.String(1024), nullable=True)
    write_merged_count = db.Column(db.String(1024), nullable=True)
    busy_time = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoDiskPerform_5min %s>' % self.guid

class SfoDiskPerform_hour(db.Model):
    __tablename__ = 'sfo_disk_perform_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    disk_uuid = db.Column(db.String(1024), nullable=False)
    disk_name = db.Column(db.String(1024), nullable=True)
    disk_total = db.Column(db.String(128), nullable=True)
    disk_used = db.Column(db.String(1024), nullable=True)
    disk_free = db.Column(db.String(1024), nullable=True)
    disk_percent = db.Column(db.String(1024), nullable=True)
    read_count = db.Column(db.String(1024), nullable=True)
    write_count = db.Column(db.String(1024), nullable=True)
    read_bytes = db.Column(db.String(1024), nullable=True)
    write_bytes = db.Column(db.String(1024), nullable=True)
    read_time = db.Column(db.String(1024), nullable=True)
    write_time = db.Column(db.String(1024), nullable=True)
    read_merged_count = db.Column(db.String(1024), nullable=True)
    write_merged_count = db.Column(db.String(1024), nullable=True)
    busy_time = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoDiskPerform_hour %s>' % self.guid

class SfoDiskPerform_day(db.Model):
    __tablename__ = 'sfo_disk_perform_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    disk_uuid = db.Column(db.String(1024), nullable=False)
    disk_name = db.Column(db.String(1024), nullable=True)
    disk_total = db.Column(db.String(128), nullable=True)
    disk_used = db.Column(db.String(1024), nullable=True)
    disk_free = db.Column(db.String(1024), nullable=True)
    disk_percent = db.Column(db.String(1024), nullable=True)
    read_count = db.Column(db.String(1024), nullable=True)
    write_count = db.Column(db.String(1024), nullable=True)
    read_bytes = db.Column(db.String(1024), nullable=True)
    write_bytes = db.Column(db.String(1024), nullable=True)
    read_time = db.Column(db.String(1024), nullable=True)
    write_time = db.Column(db.String(1024), nullable=True)
    read_merged_count = db.Column(db.String(1024), nullable=True)
    write_merged_count = db.Column(db.String(1024), nullable=True)
    busy_time = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoDiskPerform_day %s>' % self.guid


class SfoDiskPerformHistory(db.Model):
    __tablename__ = 'sfo_disk_perform_data_his'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    disk_uuid = db.Column(db.String(1024), nullable=False)
    disk_name = db.Column(db.String(1024), nullable=True)
    disk_total = db.Column(db.String(128), nullable=True)
    disk_used = db.Column(db.String(1024), nullable=True)
    disk_free = db.Column(db.String(1024), nullable=True)
    disk_percent = db.Column(db.String(1024), nullable=True)
    read_count = db.Column(db.String(1024), nullable=True)
    write_count = db.Column(db.String(1024), nullable=True)
    read_bytes = db.Column(db.String(1024), nullable=True)
    write_bytes = db.Column(db.String(1024), nullable=True)
    read_time = db.Column(db.String(1024), nullable=True)
    write_time = db.Column(db.String(1024), nullable=True)
    read_merged_count = db.Column(db.String(1024), nullable=True)
    write_merged_count = db.Column(db.String(1024), nullable=True)
    busy_time = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoDiskPerformHistory %s>' % self.disk_uuid


class SfoHostInfo(db.Model):
    __tablename__ = 'sfo_host_info'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=False)
    mf_name = db.Column(db.String(128), nullable=True)
    mf_model = db.Column(db.String(128), nullable=True)
    mf_bios_version = db.Column(db.String(128), nullable=True)
    mf_bios_date = db.Column(db.String(128), nullable=True)
    mf_serial_number = db.Column(db.String(128), nullable=True)
    os_version = db.Column(db.String(128), nullable=True)
    os_kernel_version = db.Column(db.String(128), nullable=True)
    cpu_model = db.Column(db.String(1024), nullable=True)
    cpu_sockets = db.Column(db.String(128), nullable=True)
    cpu_cores = db.Column(db.String(128), nullable=True)
    cpu_processors = db.Column(db.String(1024), nullable=True)
    cpu_frequency = db.Column(db.String(1024), nullable=True)
    mem_total = db.Column(db.String(128), nullable=True)
    mem_number = db.Column(db.String(128), nullable=True)
    mem_single_size = db.Column(db.String(128), nullable=True)
    mem_frequency = db.Column(db.String(1024), nullable=True)
    net_model = db.Column(db.Text(2048), nullable=True)
    net_number = db.Column(db.String(128), nullable=True)
    net_speed = db.Column(db.String(1024), nullable=True)
    net_mac_address = db.Column(db.String(1024), nullable=True)
    net_ip_address = db.Column(db.String(1024), nullable=True)
    disk_type = db.Column(db.String(1024), nullable=True)
    disk_number = db.Column(db.String(128), nullable=True)
    disk_rpm_speed = db.Column(db.String(1024), nullable=True)
    disk_capacity = db.Column(db.String(1024), nullable=True)
    disk_useful_size = db.Column(db.String(1024), nullable=True)
    disk_rw_rate = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoHostInfo %s>' % self.host_name


class SfoNodePerform(db.Model):
    __tablename__ = 'sfo_node_perform_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    node_role = db.Column(db.String(128), nullable=True)
    swift_version = db.Column(db.String(128), nullable=True)
    node_time = db.Column(db.String(128), nullable=True)
    async_pending = db.Column(db.String(128), nullable=True)
    node_sockstat = db.Column(db.String(1024), nullable=True)
    stg_diskusage = db.Column(db.Text(0), nullable=True)
    drive_audit_errors = db.Column(db.String(1024), nullable=True)
    node_ringmd5 = db.Column(db.String(1024), nullable=True)
    swiftconfmd5 = db.Column(db.String(128), nullable=True)
    quarantined_count = db.Column(db.String(1024), nullable=True)
    account_replication = db.Column(db.String(1024), nullable=True)
    container_replication = db.Column(db.String(1024), nullable=True)
    object_replication = db.Column(db.Text(1024), nullable=True)
    account_auditor = db.Column(db.String(1024), nullable=True)
    container_auditor = db.Column(db.String(1024), nullable=True)
    object_auditor = db.Column(db.String(1024), nullable=True)
    account_updater = db.Column(db.String(1024), nullable=True)
    container_updater = db.Column(db.String(1024), nullable=True)
    object_updater = db.Column(db.Text(1024), nullable=True)
    object_expirer = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodePerform %s>' % self.host_name

class SfoNodePerform_5min(db.Model):
    __tablename__ = 'sfo_node_perform_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    node_role = db.Column(db.String(128), nullable=True)
    swift_version = db.Column(db.String(128), nullable=True)
    node_time = db.Column(db.String(128), nullable=True)
    async_pending = db.Column(db.String(128), nullable=True)
    node_sockstat = db.Column(db.String(1024), nullable=True)
    stg_diskusage = db.Column(db.Text(0), nullable=True)
    drive_audit_errors = db.Column(db.String(1024), nullable=True)
    node_ringmd5 = db.Column(db.String(1024), nullable=True)
    swiftconfmd5 = db.Column(db.String(128), nullable=True)
    quarantined_count = db.Column(db.String(1024), nullable=True)
    account_replication = db.Column(db.String(1024), nullable=True)
    container_replication = db.Column(db.String(1024), nullable=True)
    object_replication = db.Column(db.Text(1024), nullable=True)
    account_auditor = db.Column(db.String(1024), nullable=True)
    container_auditor = db.Column(db.String(1024), nullable=True)
    object_auditor = db.Column(db.String(1024), nullable=True)
    account_updater = db.Column(db.String(1024), nullable=True)
    container_updater = db.Column(db.String(1024), nullable=True)
    object_updater = db.Column(db.Text(1024), nullable=True)
    object_expirer = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodePerform_5min %s>' % self.host_name

class SfoNodePerform_hour(db.Model):
    __tablename__ = 'sfo_node_perform_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    node_role = db.Column(db.String(128), nullable=True)
    swift_version = db.Column(db.String(128), nullable=True)
    node_time = db.Column(db.String(128), nullable=True)
    async_pending = db.Column(db.String(128), nullable=True)
    node_sockstat = db.Column(db.String(1024), nullable=True)
    stg_diskusage = db.Column(db.Text(0), nullable=True)
    drive_audit_errors = db.Column(db.String(1024), nullable=True)
    node_ringmd5 = db.Column(db.String(1024), nullable=True)
    swiftconfmd5 = db.Column(db.String(128), nullable=True)
    quarantined_count = db.Column(db.String(1024), nullable=True)
    account_replication = db.Column(db.String(1024), nullable=True)
    container_replication = db.Column(db.String(1024), nullable=True)
    object_replication = db.Column(db.Text(1024), nullable=True)
    account_auditor = db.Column(db.String(1024), nullable=True)
    container_auditor = db.Column(db.String(1024), nullable=True)
    object_auditor = db.Column(db.String(1024), nullable=True)
    account_updater = db.Column(db.String(1024), nullable=True)
    container_updater = db.Column(db.String(1024), nullable=True)
    object_updater = db.Column(db.Text(1024), nullable=True)
    object_expirer = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodePerform_hour %s>' % self.host_name

class SfoNodePerform_day(db.Model):
    __tablename__ = 'sfo_node_perform_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    node_role = db.Column(db.String(128), nullable=True)
    swift_version = db.Column(db.String(128), nullable=True)
    node_time = db.Column(db.String(128), nullable=True)
    async_pending = db.Column(db.String(128), nullable=True)
    node_sockstat = db.Column(db.String(1024), nullable=True)
    stg_diskusage = db.Column(db.Text(0), nullable=True)
    drive_audit_errors = db.Column(db.String(1024), nullable=True)
    node_ringmd5 = db.Column(db.String(1024), nullable=True)
    swiftconfmd5 = db.Column(db.String(128), nullable=True)
    quarantined_count = db.Column(db.String(1024), nullable=True)
    account_replication = db.Column(db.String(1024), nullable=True)
    container_replication = db.Column(db.String(1024), nullable=True)
    object_replication = db.Column(db.Text(1024), nullable=True)
    account_auditor = db.Column(db.String(1024), nullable=True)
    container_auditor = db.Column(db.String(1024), nullable=True)
    object_auditor = db.Column(db.String(1024), nullable=True)
    account_updater = db.Column(db.String(1024), nullable=True)
    container_updater = db.Column(db.String(1024), nullable=True)
    object_updater = db.Column(db.Text(1024), nullable=True)
    object_expirer = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodePerform_day %s>' % self.host_name

class SfoNodePerformHistory(db.Model):
    __tablename__ = 'sfo_node_perform_data_his'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    node_role = db.Column(db.String(128), nullable=True)
    swift_version = db.Column(db.String(128), nullable=True)
    node_time = db.Column(db.String(128), nullable=True)
    async_pending = db.Column(db.String(128), nullable=True)
    node_sockstat = db.Column(db.String(1024), nullable=True)
    stg_diskusage = db.Column(db.String(1024), nullable=True)
    drive_audit_errors = db.Column(db.String(1024), nullable=True)
    node_ringmd5 = db.Column(db.String(1024), nullable=True)
    swiftconfmd5 = db.Column(db.String(128), nullable=True)
    quarantined_count = db.Column(db.String(1024), nullable=True)
    account_replication = db.Column(db.String(1024), nullable=True)
    container_replication = db.Column(db.String(1024), nullable=True)
    object_replication = db.Column(db.Text(1024), nullable=True)
    account_auditor = db.Column(db.String(1024), nullable=True)
    container_auditor = db.Column(db.String(1024), nullable=True)
    object_auditor = db.Column(db.String(1024), nullable=True)
    account_updater = db.Column(db.String(1024), nullable=True)
    container_updater = db.Column(db.String(1024), nullable=True)
    object_updater = db.Column(db.Text(1024), nullable=True)
    object_expirer = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodePerformHistory %s>' % self.host_name


class SfoNodeService(db.Model):
    __tablename__ = 'sfo_node_srvstat_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    srv_proxy = db.Column(db.String(128), nullable=True)
    srv_account = db.Column(db.String(128), nullable=True)
    srv_account_auditor = db.Column(db.String(128), nullable=True)
    srv_account_reaper = db.Column(db.String(128), nullable=True)
    srv_account_replicator = db.Column(db.String(128), nullable=True)
    srv_container = db.Column(db.String(128), nullable=True)
    srv_container_auditor = db.Column(db.String(128), nullable=True)
    srv_container_replicator = db.Column(db.String(128), nullable=True)
    srv_container_updater = db.Column(db.String(128), nullable=True)
    srv_container_sync = db.Column(db.String(128), nullable=True)
    srv_container_reconciler = db.Column(db.String(128), nullable=True)
    srv_object = db.Column(db.String(128), nullable=True)
    srv_object_auditor = db.Column(db.String(128), nullable=True)
    srv_object_replicator = db.Column(db.String(128), nullable=True)
    srv_object_updater = db.Column(db.String(128), nullable=True)
    srv_object_expirer = db.Column(db.String(128), nullable=True)
    srv_object_reconstructor = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeService %s>' % self.host_name

class SfoNodeService_5min(db.Model):
    __tablename__ = 'sfo_node_srvstat_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    srv_proxy = db.Column(db.String(128), nullable=True)
    srv_account = db.Column(db.String(128), nullable=True)
    srv_account_auditor = db.Column(db.String(128), nullable=True)
    srv_account_reaper = db.Column(db.String(128), nullable=True)
    srv_account_replicator = db.Column(db.String(128), nullable=True)
    srv_container = db.Column(db.String(128), nullable=True)
    srv_container_auditor = db.Column(db.String(128), nullable=True)
    srv_container_replicator = db.Column(db.String(128), nullable=True)
    srv_container_updater = db.Column(db.String(128), nullable=True)
    srv_container_sync = db.Column(db.String(128), nullable=True)
    srv_container_reconciler = db.Column(db.String(128), nullable=True)
    srv_object = db.Column(db.String(128), nullable=True)
    srv_object_auditor = db.Column(db.String(128), nullable=True)
    srv_object_replicator = db.Column(db.String(128), nullable=True)
    srv_object_updater = db.Column(db.String(128), nullable=True)
    srv_object_expirer = db.Column(db.String(128), nullable=True)
    srv_object_reconstructor = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeService_5min %s>' % self.host_name

class SfoNodeService_hour(db.Model):
    __tablename__ = 'sfo_node_srvstat_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    srv_proxy = db.Column(db.String(128), nullable=True)
    srv_account = db.Column(db.String(128), nullable=True)
    srv_account_auditor = db.Column(db.String(128), nullable=True)
    srv_account_reaper = db.Column(db.String(128), nullable=True)
    srv_account_replicator = db.Column(db.String(128), nullable=True)
    srv_container = db.Column(db.String(128), nullable=True)
    srv_container_auditor = db.Column(db.String(128), nullable=True)
    srv_container_replicator = db.Column(db.String(128), nullable=True)
    srv_container_updater = db.Column(db.String(128), nullable=True)
    srv_container_sync = db.Column(db.String(128), nullable=True)
    srv_container_reconciler = db.Column(db.String(128), nullable=True)
    srv_object = db.Column(db.String(128), nullable=True)
    srv_object_auditor = db.Column(db.String(128), nullable=True)
    srv_object_replicator = db.Column(db.String(128), nullable=True)
    srv_object_updater = db.Column(db.String(128), nullable=True)
    srv_object_expirer = db.Column(db.String(128), nullable=True)
    srv_object_reconstructor = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeService_hour %s>' % self.host_name

class SfoNodeService_day(db.Model):
    __tablename__ = 'sfo_node_srvstat_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    srv_proxy = db.Column(db.String(128), nullable=True)
    srv_account = db.Column(db.String(128), nullable=True)
    srv_account_auditor = db.Column(db.String(128), nullable=True)
    srv_account_reaper = db.Column(db.String(128), nullable=True)
    srv_account_replicator = db.Column(db.String(128), nullable=True)
    srv_container = db.Column(db.String(128), nullable=True)
    srv_container_auditor = db.Column(db.String(128), nullable=True)
    srv_container_replicator = db.Column(db.String(128), nullable=True)
    srv_container_updater = db.Column(db.String(128), nullable=True)
    srv_container_sync = db.Column(db.String(128), nullable=True)
    srv_container_reconciler = db.Column(db.String(128), nullable=True)
    srv_object = db.Column(db.String(128), nullable=True)
    srv_object_auditor = db.Column(db.String(128), nullable=True)
    srv_object_replicator = db.Column(db.String(128), nullable=True)
    srv_object_updater = db.Column(db.String(128), nullable=True)
    srv_object_expirer = db.Column(db.String(128), nullable=True)
    srv_object_reconstructor = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeService_day %s>' % self.host_name

class SfoNodeServiceHistory(db.Model):
    __tablename__ = 'sfo_node_srvstat_data_his'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    srv_proxy = db.Column(db.String(128), nullable=True)
    srv_account = db.Column(db.String(128), nullable=True)
    srv_account_auditor = db.Column(db.String(128), nullable=True)
    srv_account_reaper = db.Column(db.String(128), nullable=True)
    srv_account_replicator = db.Column(db.String(128), nullable=True)
    srv_container = db.Column(db.String(128), nullable=True)
    srv_container_auditor = db.Column(db.String(128), nullable=True)
    srv_container_replicator = db.Column(db.String(128), nullable=True)
    srv_container_updater = db.Column(db.String(128), nullable=True)
    srv_container_sync = db.Column(db.String(128), nullable=True)
    srv_container_reconciler = db.Column(db.String(128), nullable=True)
    srv_object = db.Column(db.String(128), nullable=True)
    srv_object_auditor = db.Column(db.String(128), nullable=True)
    srv_object_replicator = db.Column(db.String(128), nullable=True)
    srv_object_updater = db.Column(db.String(128), nullable=True)
    srv_object_expirer = db.Column(db.String(128), nullable=True)
    srv_object_reconstructor = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeServiceHistory %s>' % self.host_name


class SfoNodeStat(db.Model):
    __tablename__ = 'sfo_node_stat_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    host_runtime = db.Column(db.String(128), nullable=True)
    host_average_load = db.Column(db.String(128), nullable=True)
    host_login_users = db.Column(db.String(128), nullable=True)
    host_time = db.Column(db.String(128), nullable=True)
    thread_total = db.Column(db.String(128), nullable=True)
    thread_running = db.Column(db.String(128), nullable=True)
    thread_sleeping = db.Column(db.String(128), nullable=True)
    thread_stoped = db.Column(db.String(128), nullable=True)
    thread_zombie = db.Column(db.String(128), nullable=True)
    cpu_us = db.Column(db.String(128), nullable=True)
    cpu_sy = db.Column(db.String(128), nullable=True)
    cpu_ni = db.Column(db.String(128), nullable=True)
    cpu_id = db.Column(db.String(128), nullable=True)
    cpu_wa = db.Column(db.String(128), nullable=True)
    cpu_hi = db.Column(db.String(128), nullable=True)
    cpu_si = db.Column(db.String(128), nullable=True)
    cpu_st = db.Column(db.String(128), nullable=True)
    cpu_core_used = db.Column(db.String(1024), nullable=True)
    cpu_core_frq = db.Column(db.String(1024), nullable=True)
    mem_total = db.Column(db.String(128), nullable=True)
    mem_used = db.Column(db.String(128), nullable=True)
    mem_free = db.Column(db.String(128), nullable=True)
    mem_buffers = db.Column(db.String(128), nullable=True)
    swap_total = db.Column(db.String(128), nullable=True)
    swap_used = db.Column(db.String(128), nullable=True)
    swap_free = db.Column(db.String(128), nullable=True)
    swap_cached = db.Column(db.String(128), nullable=True)
    net_uesd = db.Column(db.String(1024), nullable=True)
    net_send_packages = db.Column(db.String(1024), nullable=True)
    net_recv_packages = db.Column(db.String(1024), nullable=True)
    net_send_bytes = db.Column(db.String(1024), nullable=True)
    net_recv_bytes = db.Column(db.String(1024), nullable=True)
    net_in_err = db.Column(db.String(1024), nullable=True)
    net_out_err = db.Column(db.String(1024), nullable=True)
    net_in_drop = db.Column(db.String(1024), nullable=True)
    net_out_drop = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeStat %s>' % self.host_name

class SfoNodeStat_5min(db.Model):
    __tablename__ = 'sfo_node_stat_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    host_runtime = db.Column(db.String(128), nullable=True)
    host_average_load = db.Column(db.String(128), nullable=True)
    host_login_users = db.Column(db.String(128), nullable=True)
    host_time = db.Column(db.String(128), nullable=True)
    thread_total = db.Column(db.String(128), nullable=True)
    thread_running = db.Column(db.String(128), nullable=True)
    thread_sleeping = db.Column(db.String(128), nullable=True)
    thread_stoped = db.Column(db.String(128), nullable=True)
    thread_zombie = db.Column(db.String(128), nullable=True)
    cpu_us = db.Column(db.String(128), nullable=True)
    cpu_sy = db.Column(db.String(128), nullable=True)
    cpu_ni = db.Column(db.String(128), nullable=True)
    cpu_id = db.Column(db.String(128), nullable=True)
    cpu_wa = db.Column(db.String(128), nullable=True)
    cpu_hi = db.Column(db.String(128), nullable=True)
    cpu_si = db.Column(db.String(128), nullable=True)
    cpu_st = db.Column(db.String(128), nullable=True)
    cpu_core_used = db.Column(db.String(1024), nullable=True)
    cpu_core_frq = db.Column(db.String(1024), nullable=True)
    mem_total = db.Column(db.String(128), nullable=True)
    mem_used = db.Column(db.String(128), nullable=True)
    mem_free = db.Column(db.String(128), nullable=True)
    mem_buffers = db.Column(db.String(128), nullable=True)
    swap_total = db.Column(db.String(128), nullable=True)
    swap_used = db.Column(db.String(128), nullable=True)
    swap_free = db.Column(db.String(128), nullable=True)
    swap_cached = db.Column(db.String(128), nullable=True)
    net_uesd = db.Column(db.String(1024), nullable=True)
    net_send_packages = db.Column(db.String(1024), nullable=True)
    net_recv_packages = db.Column(db.String(1024), nullable=True)
    net_send_bytes = db.Column(db.String(1024), nullable=True)
    net_recv_bytes = db.Column(db.String(1024), nullable=True)
    net_in_err = db.Column(db.String(1024), nullable=True)
    net_out_err = db.Column(db.String(1024), nullable=True)
    net_in_drop = db.Column(db.String(1024), nullable=True)
    net_out_drop = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeStat_5min %s>' % self.host_name

class SfoNodeStat_hour(db.Model):
    __tablename__ = 'sfo_node_stat_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    host_runtime = db.Column(db.String(128), nullable=True)
    host_average_load = db.Column(db.String(128), nullable=True)
    host_login_users = db.Column(db.String(128), nullable=True)
    host_time = db.Column(db.String(128), nullable=True)
    thread_total = db.Column(db.String(128), nullable=True)
    thread_running = db.Column(db.String(128), nullable=True)
    thread_sleeping = db.Column(db.String(128), nullable=True)
    thread_stoped = db.Column(db.String(128), nullable=True)
    thread_zombie = db.Column(db.String(128), nullable=True)
    cpu_us = db.Column(db.String(128), nullable=True)
    cpu_sy = db.Column(db.String(128), nullable=True)
    cpu_ni = db.Column(db.String(128), nullable=True)
    cpu_id = db.Column(db.String(128), nullable=True)
    cpu_wa = db.Column(db.String(128), nullable=True)
    cpu_hi = db.Column(db.String(128), nullable=True)
    cpu_si = db.Column(db.String(128), nullable=True)
    cpu_st = db.Column(db.String(128), nullable=True)
    cpu_core_used = db.Column(db.String(1024), nullable=True)
    cpu_core_frq = db.Column(db.String(1024), nullable=True)
    mem_total = db.Column(db.String(128), nullable=True)
    mem_used = db.Column(db.String(128), nullable=True)
    mem_free = db.Column(db.String(128), nullable=True)
    mem_buffers = db.Column(db.String(128), nullable=True)
    swap_total = db.Column(db.String(128), nullable=True)
    swap_used = db.Column(db.String(128), nullable=True)
    swap_free = db.Column(db.String(128), nullable=True)
    swap_cached = db.Column(db.String(128), nullable=True)
    net_uesd = db.Column(db.String(1024), nullable=True)
    net_send_packages = db.Column(db.String(1024), nullable=True)
    net_recv_packages = db.Column(db.String(1024), nullable=True)
    net_send_bytes = db.Column(db.String(1024), nullable=True)
    net_recv_bytes = db.Column(db.String(1024), nullable=True)
    net_in_err = db.Column(db.String(1024), nullable=True)
    net_out_err = db.Column(db.String(1024), nullable=True)
    net_in_drop = db.Column(db.String(1024), nullable=True)
    net_out_drop = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeStat_hour %s>' % self.host_name

class SfoNodeStat_day(db.Model):
    __tablename__ = 'sfo_node_stat_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    host_runtime = db.Column(db.String(128), nullable=True)
    host_average_load = db.Column(db.String(128), nullable=True)
    host_login_users = db.Column(db.String(128), nullable=True)
    host_time = db.Column(db.String(128), nullable=True)
    thread_total = db.Column(db.String(128), nullable=True)
    thread_running = db.Column(db.String(128), nullable=True)
    thread_sleeping = db.Column(db.String(128), nullable=True)
    thread_stoped = db.Column(db.String(128), nullable=True)
    thread_zombie = db.Column(db.String(128), nullable=True)
    cpu_us = db.Column(db.String(128), nullable=True)
    cpu_sy = db.Column(db.String(128), nullable=True)
    cpu_ni = db.Column(db.String(128), nullable=True)
    cpu_id = db.Column(db.String(128), nullable=True)
    cpu_wa = db.Column(db.String(128), nullable=True)
    cpu_hi = db.Column(db.String(128), nullable=True)
    cpu_si = db.Column(db.String(128), nullable=True)
    cpu_st = db.Column(db.String(128), nullable=True)
    cpu_core_used = db.Column(db.String(1024), nullable=True)
    cpu_core_frq = db.Column(db.String(1024), nullable=True)
    mem_total = db.Column(db.String(128), nullable=True)
    mem_used = db.Column(db.String(128), nullable=True)
    mem_free = db.Column(db.String(128), nullable=True)
    mem_buffers = db.Column(db.String(128), nullable=True)
    swap_total = db.Column(db.String(128), nullable=True)
    swap_used = db.Column(db.String(128), nullable=True)
    swap_free = db.Column(db.String(128), nullable=True)
    swap_cached = db.Column(db.String(128), nullable=True)
    net_uesd = db.Column(db.String(1024), nullable=True)
    net_send_packages = db.Column(db.String(1024), nullable=True)
    net_recv_packages = db.Column(db.String(1024), nullable=True)
    net_send_bytes = db.Column(db.String(1024), nullable=True)
    net_recv_bytes = db.Column(db.String(1024), nullable=True)
    net_in_err = db.Column(db.String(1024), nullable=True)
    net_out_err = db.Column(db.String(1024), nullable=True)
    net_in_drop = db.Column(db.String(1024), nullable=True)
    net_out_drop = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeStat_day %s>' % self.host_name

class SfoNodeStatHistory(db.Model):
    __tablename__ = 'sfo_node_stat_data_his'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=True)
    host_runtime = db.Column(db.String(128), nullable=True)
    host_average_load = db.Column(db.String(128), nullable=True)
    host_login_users = db.Column(db.String(128), nullable=True)
    host_time = db.Column(db.String(128), nullable=True)
    thread_total = db.Column(db.String(128), nullable=True)
    thread_running = db.Column(db.String(128), nullable=True)
    thread_sleeping = db.Column(db.String(128), nullable=True)
    thread_stoped = db.Column(db.String(128), nullable=True)
    thread_zombie = db.Column(db.String(128), nullable=True)
    cpu_us = db.Column(db.String(128), nullable=True)
    cpu_sy = db.Column(db.String(128), nullable=True)
    cpu_ni = db.Column(db.String(128), nullable=True)
    cpu_id = db.Column(db.String(128), nullable=True)
    cpu_wa = db.Column(db.String(128), nullable=True)
    cpu_hi = db.Column(db.String(128), nullable=True)
    cpu_si = db.Column(db.String(128), nullable=True)
    cpu_st = db.Column(db.String(128), nullable=True)
    cpu_core_used = db.Column(db.String(1024), nullable=True)
    cpu_core_frq = db.Column(db.String(1024), nullable=True)
    mem_total = db.Column(db.String(128), nullable=True)
    mem_used = db.Column(db.String(128), nullable=True)
    mem_free = db.Column(db.String(128), nullable=True)
    mem_buffers = db.Column(db.String(128), nullable=True)
    swap_total = db.Column(db.String(128), nullable=True)
    swap_used = db.Column(db.String(128), nullable=True)
    swap_free = db.Column(db.String(128), nullable=True)
    swap_cached = db.Column(db.String(128), nullable=True)
    net_uesd = db.Column(db.String(1024), nullable=True)
    net_send_packages = db.Column(db.String(1024), nullable=True)
    net_recv_packages = db.Column(db.String(1024), nullable=True)
    net_send_bytes = db.Column(db.String(1024), nullable=True)
    net_recv_bytes = db.Column(db.String(1024), nullable=True)
    net_in_err = db.Column(db.String(1024), nullable=True)
    net_out_err = db.Column(db.String(1024), nullable=True)
    net_in_drop = db.Column(db.String(1024), nullable=True)
    net_out_drop = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoNodeStatHistory %s>' % self.host_name

class SfoAccountStatsD(db.Model):
    __tablename__ = 'sfo_account_statsd_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_passes = db.Column(db.String(128), nullable=True)
    auditor_failures = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    reaper_errors = db.Column(db.String(128), nullable=True)
    reaper_timing = db.Column(db.Text, nullable=True)
    reaper_return_codes = db.Column(db.String(128), nullable=True)
    reaper_ctn_failures = db.Column(db.String(128), nullable=True)
    reaper_ctn_deleted = db.Column(db.String(128), nullable=True)
    reaper_ctn_remaining = db.Column(db.String(128), nullable=True)
    reaper_ctn_psb_remaining = db.Column(db.String(128), nullable=True)
    reaper_obj_failures = db.Column(db.String(128), nullable=True)
    reaper_obj_deleted = db.Column(db.String(128), nullable=True)
    reaper_obj_remaining = db.Column(db.String(128), nullable=True)
    reaper_obj_psb_remaining = db.Column(db.String(128), nullable=True)

    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)

    replicator_diffs = db.Column(db.String(128), nullable=True)
    replicator_diff_caps = db.Column(db.String(128), nullable=True)
    replicator_no_changes = db.Column(db.String(128), nullable=True)
    replicator_hashmatches = db.Column(db.String(128), nullable=True)
    replicator_rsyncs = db.Column(db.String(128), nullable=True)
    replicator_remote_merges = db.Column(db.String(128), nullable=True)
    replicator_attempts = db.Column(db.String(128), nullable=True)
    replicator_failures = db.Column(db.String(128), nullable=True)
    replicator_removes = db.Column(db.String(1024), nullable=True)
    replicator_successes = db.Column(db.String(128), nullable=True)
    replicator_timing = db.Column(db.Text, nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoAccountStatsD %s>' % self.host_name

class SfoAccountStatsD_5min(db.Model):
    __tablename__ = 'sfo_account_statsd_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_passes = db.Column(db.String(128), nullable=True)
    auditor_failures = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    reaper_errors = db.Column(db.String(128), nullable=True)
    reaper_timing = db.Column(db.Text, nullable=True)
    reaper_return_codes = db.Column(db.String(128), nullable=True)
    reaper_ctn_failures = db.Column(db.String(128), nullable=True)
    reaper_ctn_deleted = db.Column(db.String(128), nullable=True)
    reaper_ctn_remaining = db.Column(db.String(128), nullable=True)
    reaper_ctn_psb_remaining = db.Column(db.String(128), nullable=True)
    reaper_obj_failures = db.Column(db.String(128), nullable=True)
    reaper_obj_deleted = db.Column(db.String(128), nullable=True)
    reaper_obj_remaining = db.Column(db.String(128), nullable=True)
    reaper_obj_psb_remaining = db.Column(db.String(128), nullable=True)

    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)

    replicator_diffs = db.Column(db.String(128), nullable=True)
    replicator_diff_caps = db.Column(db.String(128), nullable=True)
    replicator_no_changes = db.Column(db.String(128), nullable=True)
    replicator_hashmatches = db.Column(db.String(128), nullable=True)
    replicator_rsyncs = db.Column(db.String(128), nullable=True)
    replicator_remote_merges = db.Column(db.String(128), nullable=True)
    replicator_attempts = db.Column(db.String(128), nullable=True)
    replicator_failures = db.Column(db.String(128), nullable=True)
    replicator_removes = db.Column(db.String(1024), nullable=True)
    replicator_successes = db.Column(db.String(128), nullable=True)
    replicator_timing = db.Column(db.Text, nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoAccountStatsD_5min %s>' % self.host_name

class SfoAccountStatsD_hour(db.Model):
    __tablename__ = 'sfo_account_statsd_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_passes = db.Column(db.String(128), nullable=True)
    auditor_failures = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    reaper_errors = db.Column(db.String(128), nullable=True)
    reaper_timing = db.Column(db.Text, nullable=True)
    reaper_return_codes = db.Column(db.String(128), nullable=True)
    reaper_ctn_failures = db.Column(db.String(128), nullable=True)
    reaper_ctn_deleted = db.Column(db.String(128), nullable=True)
    reaper_ctn_remaining = db.Column(db.String(128), nullable=True)
    reaper_ctn_psb_remaining = db.Column(db.String(128), nullable=True)
    reaper_obj_failures = db.Column(db.String(128), nullable=True)
    reaper_obj_deleted = db.Column(db.String(128), nullable=True)
    reaper_obj_remaining = db.Column(db.String(128), nullable=True)
    reaper_obj_psb_remaining = db.Column(db.String(128), nullable=True)

    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)

    replicator_diffs = db.Column(db.String(128), nullable=True)
    replicator_diff_caps = db.Column(db.String(128), nullable=True)
    replicator_no_changes = db.Column(db.String(128), nullable=True)
    replicator_hashmatches = db.Column(db.String(128), nullable=True)
    replicator_rsyncs = db.Column(db.String(128), nullable=True)
    replicator_remote_merges = db.Column(db.String(128), nullable=True)
    replicator_attempts = db.Column(db.String(128), nullable=True)
    replicator_failures = db.Column(db.String(128), nullable=True)
    replicator_removes = db.Column(db.String(1024), nullable=True)
    replicator_successes = db.Column(db.String(128), nullable=True)
    replicator_timing = db.Column(db.Text, nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoAccountStatsD_hour %s>' % self.host_name

class SfoAccountStatsD_day(db.Model):
    __tablename__ = 'sfo_account_statsd_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_passes = db.Column(db.String(128), nullable=True)
    auditor_failures = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    reaper_errors = db.Column(db.String(128), nullable=True)
    reaper_timing = db.Column(db.Text, nullable=True)
    reaper_return_codes = db.Column(db.String(128), nullable=True)
    reaper_ctn_failures = db.Column(db.String(128), nullable=True)
    reaper_ctn_deleted = db.Column(db.String(128), nullable=True)
    reaper_ctn_remaining = db.Column(db.String(128), nullable=True)
    reaper_ctn_psb_remaining = db.Column(db.String(128), nullable=True)
    reaper_obj_failures = db.Column(db.String(128), nullable=True)
    reaper_obj_deleted = db.Column(db.String(128), nullable=True)
    reaper_obj_remaining = db.Column(db.String(128), nullable=True)
    reaper_obj_psb_remaining = db.Column(db.String(128), nullable=True)

    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)

    replicator_diffs = db.Column(db.String(128), nullable=True)
    replicator_diff_caps = db.Column(db.String(128), nullable=True)
    replicator_no_changes = db.Column(db.String(128), nullable=True)
    replicator_hashmatches = db.Column(db.String(128), nullable=True)
    replicator_rsyncs = db.Column(db.String(128), nullable=True)
    replicator_remote_merges = db.Column(db.String(128), nullable=True)
    replicator_attempts = db.Column(db.String(128), nullable=True)
    replicator_failures = db.Column(db.String(128), nullable=True)
    replicator_removes = db.Column(db.String(1024), nullable=True)
    replicator_successes = db.Column(db.String(128), nullable=True)
    replicator_timing = db.Column(db.Text, nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoAccountStatsD_day %s>' % self.host_name

class SfoContainerStatsD(db.Model):
    __tablename__ = 'sfo_container_statsd_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_passes = db.Column(db.String(128), nullable=True)
    auditor_failures = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    replicator_diffs = db.Column(db.String(128), nullable=True)
    replicator_diff_caps = db.Column(db.String(128), nullable=True)
    replicator_no_changes = db.Column(db.String(128), nullable=True)
    replicator_hashmatches = db.Column(db.String(128), nullable=True)
    replicator_rsyncs = db.Column(db.String(128), nullable=True)
    replicator_remote_merges = db.Column(db.String(128), nullable=True)
    replicator_attempts = db.Column(db.String(128), nullable=True)
    replicator_failures = db.Column(db.String(128), nullable=True)
    replicator_removes = db.Column(db.String(1024), nullable=True)
    replicator_successes = db.Column(db.String(128), nullable=True)
    replicator_timing = db.Column(db.Text, nullable=True)

    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)

    sync_skips = db.Column(db.String(128), nullable=True)
    sync_failures = db.Column(db.String(128), nullable=True)
    sync_syncs = db.Column(db.String(128), nullable=True)
    sync_deletes = db.Column(db.String(128), nullable=True)
    sync_del_timing = db.Column(db.Text, nullable=True)
    sync_puts = db.Column(db.String(128), nullable=True)
    sync_puts_timing = db.Column(db.Text, nullable=True)

    updater_successes = db.Column(db.String(128), nullable=True)
    updater_failures = db.Column(db.String(128), nullable=True)
    updater_no_changes = db.Column(db.String(128), nullable=True)
    updater_timing = db.Column(db.Text, nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoContainerStatsD %s>' % self.host_name

class SfoContainerStatsD_5min(db.Model):
    __tablename__ = 'sfo_container_statsd_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_passes = db.Column(db.String(128), nullable=True)
    auditor_failures = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    replicator_diffs = db.Column(db.String(128), nullable=True)
    replicator_diff_caps = db.Column(db.String(128), nullable=True)
    replicator_no_changes = db.Column(db.String(128), nullable=True)
    replicator_hashmatches = db.Column(db.String(128), nullable=True)
    replicator_rsyncs = db.Column(db.String(128), nullable=True)
    replicator_remote_merges = db.Column(db.String(128), nullable=True)
    replicator_attempts = db.Column(db.String(128), nullable=True)
    replicator_failures = db.Column(db.String(128), nullable=True)
    replicator_removes = db.Column(db.String(1024), nullable=True)
    replicator_successes = db.Column(db.String(128), nullable=True)
    replicator_timing = db.Column(db.Text, nullable=True)

    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)

    sync_skips = db.Column(db.String(128), nullable=True)
    sync_failures = db.Column(db.String(128), nullable=True)
    sync_syncs = db.Column(db.String(128), nullable=True)
    sync_deletes = db.Column(db.String(128), nullable=True)
    sync_del_timing = db.Column(db.Text, nullable=True)
    sync_puts = db.Column(db.String(128), nullable=True)
    sync_puts_timing = db.Column(db.Text, nullable=True)

    updater_successes = db.Column(db.String(128), nullable=True)
    updater_failures = db.Column(db.String(128), nullable=True)
    updater_no_changes = db.Column(db.String(128), nullable=True)
    updater_timing = db.Column(db.Text, nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoContainerStatsD_5min %s>' % self.host_name

class SfoContainerStatsD_hour(db.Model):
    __tablename__ = 'sfo_container_statsd_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_passes = db.Column(db.String(128), nullable=True)
    auditor_failures = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    replicator_diffs = db.Column(db.String(128), nullable=True)
    replicator_diff_caps = db.Column(db.String(128), nullable=True)
    replicator_no_changes = db.Column(db.String(128), nullable=True)
    replicator_hashmatches = db.Column(db.String(128), nullable=True)
    replicator_rsyncs = db.Column(db.String(128), nullable=True)
    replicator_remote_merges = db.Column(db.String(128), nullable=True)
    replicator_attempts = db.Column(db.String(128), nullable=True)
    replicator_failures = db.Column(db.String(128), nullable=True)
    replicator_removes = db.Column(db.String(1024), nullable=True)
    replicator_successes = db.Column(db.String(128), nullable=True)
    replicator_timing = db.Column(db.Text, nullable=True)

    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)

    sync_skips = db.Column(db.String(128), nullable=True)
    sync_failures = db.Column(db.String(128), nullable=True)
    sync_syncs = db.Column(db.String(128), nullable=True)
    sync_deletes = db.Column(db.String(128), nullable=True)
    sync_del_timing = db.Column(db.Text, nullable=True)
    sync_puts = db.Column(db.String(128), nullable=True)
    sync_puts_timing = db.Column(db.Text, nullable=True)

    updater_successes = db.Column(db.String(128), nullable=True)
    updater_failures = db.Column(db.String(128), nullable=True)
    updater_no_changes = db.Column(db.String(128), nullable=True)
    updater_timing = db.Column(db.Text, nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoContainerStatsD_hour %s>' % self.host_name

class SfoContainerStatsD_day(db.Model):
    __tablename__ = 'sfo_container_statsd_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_passes = db.Column(db.String(128), nullable=True)
    auditor_failures = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    replicator_diffs = db.Column(db.String(128), nullable=True)
    replicator_diff_caps = db.Column(db.String(128), nullable=True)
    replicator_no_changes = db.Column(db.String(128), nullable=True)
    replicator_hashmatches = db.Column(db.String(128), nullable=True)
    replicator_rsyncs = db.Column(db.String(128), nullable=True)
    replicator_remote_merges = db.Column(db.String(128), nullable=True)
    replicator_attempts = db.Column(db.String(128), nullable=True)
    replicator_failures = db.Column(db.String(128), nullable=True)
    replicator_removes = db.Column(db.String(1024), nullable=True)
    replicator_successes = db.Column(db.String(128), nullable=True)
    replicator_timing = db.Column(db.Text, nullable=True)

    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)

    sync_skips = db.Column(db.String(128), nullable=True)
    sync_failures = db.Column(db.String(128), nullable=True)
    sync_syncs = db.Column(db.String(128), nullable=True)
    sync_deletes = db.Column(db.String(128), nullable=True)
    sync_del_timing = db.Column(db.Text, nullable=True)
    sync_puts = db.Column(db.String(128), nullable=True)
    sync_puts_timing = db.Column(db.Text, nullable=True)

    updater_successes = db.Column(db.String(128), nullable=True)
    updater_failures = db.Column(db.String(128), nullable=True)
    updater_no_changes = db.Column(db.String(128), nullable=True)
    updater_timing = db.Column(db.Text, nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoContainerStatsD_day %s>' % self.host_name

class SfoObjectStatsD(db.Model):
    __tablename__ = 'sfo_object_statsd_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_quarantines = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    expirer_objects = db.Column(db.String(128), nullable=True)
    expirer_errors = db.Column(db.String(128), nullable=True)
    expirer_timing = db.Column(db.Text, nullable=True)

    reconstructor_part_del_count = db.Column(db.String(128), nullable=True)
    reconstructor_part_del_timing = db.Column(db.Text, nullable=True)
    reconstructor_part_update_count = db.Column(db.String(128), nullable=True)
    reconstructor_part_update_timing = db.Column(db.Text, nullable=True)
    reconstructor_suffix_hashes = db.Column(db.String(128), nullable=True)
    reconstructor_suffix_syncs = db.Column(db.String(128), nullable=True)

    replicator_part_del_count = db.Column(db.String(128), nullable=True)
    replicator_part_del_timing = db.Column(db.Text, nullable=True)
    replicator_part_update_count = db.Column(db.String(128), nullable=True)
    replicator_part_update_timing = db.Column(db.Text, nullable=True)
    replicator_suffix_hashes = db.Column(db.String(128), nullable=True)
    replicator_suffix_syncs = db.Column(db.String(128), nullable=True)

    req_quarantines = db.Column(db.String(128), nullable=True)
    req_async_pendings = db.Column(db.String(128), nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timeouts = db.Column(db.String(128), nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_put_dev_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)

    updater_errors = db.Column(db.String(128), nullable=True)
    updater_timing = db.Column(db.String(128), nullable=True)
    updater_quarantines = db.Column(db.String(128), nullable=True)
    updater_successes = db.Column(db.String(128), nullable=True)
    updater_failures = db.Column(db.String(128), nullable=True)
    updater_unlinks = db.Column(db.String(128), nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoObjectStatsD %s>' % self.host_name

class SfoObjectStatsD_5min(db.Model):
    __tablename__ = 'sfo_object_statsd_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_quarantines = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    expirer_objects = db.Column(db.String(128), nullable=True)
    expirer_errors = db.Column(db.String(128), nullable=True)
    expirer_timing = db.Column(db.Text, nullable=True)

    reconstructor_part_del_count = db.Column(db.String(128), nullable=True)
    reconstructor_part_del_timing = db.Column(db.Text, nullable=True)
    reconstructor_part_update_count = db.Column(db.String(128), nullable=True)
    reconstructor_part_update_timing = db.Column(db.Text, nullable=True)
    reconstructor_suffix_hashes = db.Column(db.String(128), nullable=True)
    reconstructor_suffix_syncs = db.Column(db.String(128), nullable=True)

    replicator_part_del_count = db.Column(db.String(128), nullable=True)
    replicator_part_del_timing = db.Column(db.Text, nullable=True)
    replicator_part_update_count = db.Column(db.String(128), nullable=True)
    replicator_part_update_timing = db.Column(db.Text, nullable=True)
    replicator_suffix_hashes = db.Column(db.String(128), nullable=True)
    replicator_suffix_syncs = db.Column(db.String(128), nullable=True)

    req_quarantines = db.Column(db.String(128), nullable=True)
    req_async_pendings = db.Column(db.String(128), nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timeouts = db.Column(db.String(128), nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_put_dev_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)

    updater_errors = db.Column(db.String(128), nullable=True)
    updater_timing = db.Column(db.String(128), nullable=True)
    updater_quarantines = db.Column(db.String(128), nullable=True)
    updater_successes = db.Column(db.String(128), nullable=True)
    updater_failures = db.Column(db.String(128), nullable=True)
    updater_unlinks = db.Column(db.String(128), nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoObjectStatsD_5min %s>' % self.host_name

class SfoObjectStatsD_hour(db.Model):
    __tablename__ = 'sfo_object_statsd_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_quarantines = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    expirer_objects = db.Column(db.String(128), nullable=True)
    expirer_errors = db.Column(db.String(128), nullable=True)
    expirer_timing = db.Column(db.Text, nullable=True)

    reconstructor_part_del_count = db.Column(db.String(128), nullable=True)
    reconstructor_part_del_timing = db.Column(db.Text, nullable=True)
    reconstructor_part_update_count = db.Column(db.String(128), nullable=True)
    reconstructor_part_update_timing = db.Column(db.Text, nullable=True)
    reconstructor_suffix_hashes = db.Column(db.String(128), nullable=True)
    reconstructor_suffix_syncs = db.Column(db.String(128), nullable=True)

    replicator_part_del_count = db.Column(db.String(128), nullable=True)
    replicator_part_del_timing = db.Column(db.Text, nullable=True)
    replicator_part_update_count = db.Column(db.String(128), nullable=True)
    replicator_part_update_timing = db.Column(db.Text, nullable=True)
    replicator_suffix_hashes = db.Column(db.String(128), nullable=True)
    replicator_suffix_syncs = db.Column(db.String(128), nullable=True)

    req_quarantines = db.Column(db.String(128), nullable=True)
    req_async_pendings = db.Column(db.String(128), nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timeouts = db.Column(db.String(128), nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_put_dev_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)

    updater_errors = db.Column(db.String(128), nullable=True)
    updater_timing = db.Column(db.String(128), nullable=True)
    updater_quarantines = db.Column(db.String(128), nullable=True)
    updater_successes = db.Column(db.String(128), nullable=True)
    updater_failures = db.Column(db.String(128), nullable=True)
    updater_unlinks = db.Column(db.String(128), nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoObjectStatsD_hour %s>' % self.host_name

class SfoObjectStatsD_day(db.Model):
    __tablename__ = 'sfo_object_statsd_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    auditor_quarantines = db.Column(db.String(128), nullable=True)
    auditor_errors = db.Column(db.String(128), nullable=True)
    auditor_timing = db.Column(db.Text, nullable=True)

    expirer_objects = db.Column(db.String(128), nullable=True)
    expirer_errors = db.Column(db.String(128), nullable=True)
    expirer_timing = db.Column(db.Text, nullable=True)

    reconstructor_part_del_count = db.Column(db.String(128), nullable=True)
    reconstructor_part_del_timing = db.Column(db.Text, nullable=True)
    reconstructor_part_update_count = db.Column(db.String(128), nullable=True)
    reconstructor_part_update_timing = db.Column(db.Text, nullable=True)
    reconstructor_suffix_hashes = db.Column(db.String(128), nullable=True)
    reconstructor_suffix_syncs = db.Column(db.String(128), nullable=True)

    replicator_part_del_count = db.Column(db.String(128), nullable=True)
    replicator_part_del_timing = db.Column(db.Text, nullable=True)
    replicator_part_update_count = db.Column(db.String(128), nullable=True)
    replicator_part_update_timing = db.Column(db.Text, nullable=True)
    replicator_suffix_hashes = db.Column(db.String(128), nullable=True)
    replicator_suffix_syncs = db.Column(db.String(128), nullable=True)

    req_quarantines = db.Column(db.String(128), nullable=True)
    req_async_pendings = db.Column(db.String(128), nullable=True)
    req_post_err_timing = db.Column(db.Text, nullable=True)
    req_post_timing = db.Column(db.Text, nullable=True)
    req_put_err_timing = db.Column(db.Text, nullable=True)
    req_put_timeouts = db.Column(db.String(128), nullable=True)
    req_put_timing = db.Column(db.Text, nullable=True)
    req_put_dev_timing = db.Column(db.Text, nullable=True)
    req_get_err_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_head_err_timing = db.Column(db.Text, nullable=True)
    req_head_timing = db.Column(db.Text, nullable=True)
    req_del_err_timing = db.Column(db.Text, nullable=True)
    req_del_timing = db.Column(db.Text, nullable=True)
    req_rep_err_timing = db.Column(db.Text, nullable=True)
    req_rep_timing = db.Column(db.Text, nullable=True)

    updater_errors = db.Column(db.String(128), nullable=True)
    updater_timing = db.Column(db.String(128), nullable=True)
    updater_quarantines = db.Column(db.String(128), nullable=True)
    updater_successes = db.Column(db.String(128), nullable=True)
    updater_failures = db.Column(db.String(128), nullable=True)
    updater_unlinks = db.Column(db.String(128), nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoObjectStatsD_day %s>' % self.host_name


class SfoProxyStatsD(db.Model):
    __tablename__ = 'sfo_proxy_statsd_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    req_errors = db.Column(db.String(128), nullable=True)
    req_handoff_count = db.Column(db.String(128), nullable=True)
    req_handoff_all_count = db.Column(db.String(128), nullable=True)
    req_client_timeouts = db.Column(db.String(128), nullable=True)
    req_client_disconnects = db.Column(db.String(128), nullable=True)
    req_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_xfer = db.Column(db.String(128), nullable=True)
    req_obj_policy_timing = db.Column(db.Text, nullable=True)
    req_obj_policy_get_timing = db.Column(db.Text, nullable=True)
    req_obj_policy_xfer = db.Column(db.String(128), nullable=True)
    req_auth_unauthorized = db.Column(db.String(128), nullable=True)
    req_auth_forbidden = db.Column(db.String(128), nullable=True)
    req_auth_token_denied = db.Column(db.String(128), nullable=True)
    req_auth_errors = db.Column(db.String(128), nullable=True)

    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoProxyStatsD %s>' % self.host_name

class SfoProxyStatsD_5min(db.Model):
    __tablename__ = 'sfo_proxy_statsd_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    req_errors = db.Column(db.String(128), nullable=True)
    req_handoff_count = db.Column(db.String(128), nullable=True)
    req_handoff_all_count = db.Column(db.String(128), nullable=True)
    req_client_timeouts = db.Column(db.String(128), nullable=True)
    req_client_disconnects = db.Column(db.String(128), nullable=True)
    req_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_xfer = db.Column(db.String(128), nullable=True)
    req_obj_policy_timing = db.Column(db.Text, nullable=True)
    req_obj_policy_get_timing = db.Column(db.Text, nullable=True)
    req_obj_policy_xfer = db.Column(db.String(128), nullable=True)
    req_auth_unauthorized = db.Column(db.String(128), nullable=True)
    req_auth_forbidden = db.Column(db.String(128), nullable=True)
    req_auth_token_denied = db.Column(db.String(128), nullable=True)
    req_auth_errors = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoProxyStatsD_5min %s>' % self.host_name

class SfoProxyStatsD_hour(db.Model):
    __tablename__ = 'sfo_proxy_statsd_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    req_errors = db.Column(db.String(128), nullable=True)
    req_handoff_count = db.Column(db.String(128), nullable=True)
    req_handoff_all_count = db.Column(db.String(128), nullable=True)
    req_client_timeouts = db.Column(db.String(128), nullable=True)
    req_client_disconnects = db.Column(db.String(128), nullable=True)
    req_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_xfer = db.Column(db.String(128), nullable=True)
    req_obj_policy_timing = db.Column(db.Text, nullable=True)
    req_obj_policy_get_timing = db.Column(db.Text, nullable=True)
    req_obj_policy_xfer = db.Column(db.String(128), nullable=True)
    req_auth_unauthorized = db.Column(db.String(128), nullable=True)
    req_auth_forbidden = db.Column(db.String(128), nullable=True)
    req_auth_token_denied = db.Column(db.String(128), nullable=True)
    req_auth_errors = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoProxyStatsD_hour %s>' % self.host_name

class SfoProxyStatsD_day(db.Model):
    __tablename__ = 'sfo_proxy_statsd_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    req_errors = db.Column(db.String(128), nullable=True)
    req_handoff_count = db.Column(db.String(128), nullable=True)
    req_handoff_all_count = db.Column(db.String(128), nullable=True)
    req_client_timeouts = db.Column(db.String(128), nullable=True)
    req_client_disconnects = db.Column(db.String(128), nullable=True)
    req_timing = db.Column(db.Text, nullable=True)
    req_get_timing = db.Column(db.Text, nullable=True)
    req_xfer = db.Column(db.String(128), nullable=True)
    req_obj_policy_timing = db.Column(db.Text, nullable=True)
    req_obj_policy_get_timing = db.Column(db.Text, nullable=True)
    req_obj_policy_xfer = db.Column(db.String(128), nullable=True)
    req_auth_unauthorized = db.Column(db.String(128), nullable=True)
    req_auth_forbidden = db.Column(db.String(128), nullable=True)
    req_auth_token_denied = db.Column(db.String(128), nullable=True)
    req_auth_errors = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoProxyStatsD_day %s>' % self.host_name

class SfoStatsD(db.Model):
    __tablename__ = 'sfo_statsd_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    counters = db.Column(db.Text, nullable=True)
    timers = db.Column(db.Text, nullable=True)
    gauges = db.Column(db.Text, nullable=True)
    timer_data = db.Column(db.Text, nullable=True)
    counter_rates = db.Column(db.Text, nullable=True)
    sets = db.Column(db.Text, nullable=True)
    pctThreshold = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoStatsD %s>' % self.guid

class SfoStatsD_5min(db.Model):
    __tablename__ = 'sfo_statsd_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    counters = db.Column(db.Text, nullable=True)
    timers = db.Column(db.Text, nullable=True)
    gauges = db.Column(db.Text, nullable=True)
    timer_data = db.Column(db.Text, nullable=True)
    counter_rates = db.Column(db.Text, nullable=True)
    sets = db.Column(db.Text, nullable=True)
    pctThreshold = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoStatsD_5min %s>' % self.guid

class SfoStatsD_hour(db.Model):
    __tablename__ = 'sfo_statsd_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    counters = db.Column(db.Text, nullable=True)
    timers = db.Column(db.Text, nullable=True)
    gauges = db.Column(db.Text, nullable=True)
    timer_data = db.Column(db.Text, nullable=True)
    counter_rates = db.Column(db.Text, nullable=True)
    sets = db.Column(db.Text, nullable=True)
    pctThreshold = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoStatsD_hour %s>' % self.guid

class SfoStatsD_day(db.Model):
    __tablename__ = 'sfo_statsd_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    counters = db.Column(db.Text, nullable=True)
    timers = db.Column(db.Text, nullable=True)
    gauges = db.Column(db.Text, nullable=True)
    timer_data = db.Column(db.Text, nullable=True)
    counter_rates = db.Column(db.Text, nullable=True)
    sets = db.Column(db.Text, nullable=True)
    pctThreshold = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoStatsD_day %s>' % self.guid

class SfoDispersionReport(db.Model):
    __tablename__ = 'sfo_dispersion_report_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    data_model = db.Column(db.String(128), nullable=True)
    cluster_name = db.Column(db.String(128), nullable=True)

    object_retries = db.Column(db.String(128), nullable=True)
    object_missing_two = db.Column(db.String(128), nullable=True)
    object_copies_found = db.Column(db.String(128), nullable=True)
    object_missing_one = db.Column(db.String(128), nullable=True)
    object_copies_expected = db.Column(db.String(128), nullable=True)
    object_pct_found = db.Column(db.String(128), nullable=True)
    object_overlapping = db.Column(db.String(128), nullable=True)
    object_missing_all = db.Column(db.String(128), nullable=True)

    container_retries = db.Column(db.String(128), nullable=True)
    container_missing_two = db.Column(db.String(128), nullable=True)
    container_copies_found = db.Column(db.String(128), nullable=True)
    container_missing_one = db.Column(db.String(128), nullable=True)
    container_copies_expected = db.Column(db.String(128), nullable=True)
    container_pct_found = db.Column(db.String(128), nullable=True)
    container_overlapping = db.Column(db.String(128), nullable=True)
    container_missing_all = db.Column(db.String(128), nullable=True)

    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoDispersionReport %s>' % self.guid


class SfoHostRing(db.Model):
    __tablename__ = 'sfo_host_ring'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    host_name = db.Column(db.String(128), nullable=False)
    ip_addr = db.Column(db.String(128), nullable=False)
    rings_md5 = db.Column(db.Text, nullable=False)
    ring_info = db.Column(db.Text, nullable=True)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoHostRing %s>' % self.guid


class SfoCofigure(db.Model):
    __tablename__ = 'sfo_configure_info'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    config_group = db.Column(db.String(128), nullable=True)
    config_key = db.Column(db.String(128), nullable=False)
    config_value = db.Column(db.String(1024), nullable=False)
    remark = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoCofigure %s>' % self.guid


class SfoClusterConfigure(db.Model):
    __tablename__ = 'sfo_cluster_configure_info'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    config_filename = db.Column(db.String(128), nullable=False)
    config_group = db.Column(db.String(128), nullable=True)
    config_key = db.Column(db.String(128), nullable=True)
    config_value = db.Column(db.String(1024), nullable=True)
    remark = db.Column(db.String(1024), nullable=True)
    add_time = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return '<SfoClusterConfigure %s>' % self.guid
#
class SfoAccountManager(db.Model):
    __tablename__ = 'sfo_account_manager'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    domain = db.Column(db.String(128), nullable=True)
    project_name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(128), nullable=False)
    system_user = db.Column(db.String(128), nullable=False)
    system_passwd = db.Column(db.String(128), nullable=False)
    keystone_user_id =db.Column(db.String(128), nullable=True)
    expire_time = db.Column(db.String(128), nullable=False)
    system_capacity = db.Column(db.String(128), nullable=False)
    system_used = db.Column(db.Text, nullable=True)
    account_id = db.Column(db.String(128), nullable=False)
    account_stat = db.Column(db.String(128), nullable=False)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoAccountManager %s>' % self.guid


class SfoPartitionsInfo(db.Model):

    __tablename__ = 'sfo_partitions_info'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.TEXT, nullable=True)
    update_time = db.Column(db.CHAR(20), primary_key=True)
    use_handoff_partitions = db.Column(db.TEXT, nullable=True)
    health_partitions = db.Column(db.TEXT, nullable=True)
    error_partitions = db.Column(db.TEXT, nullable=True)

    def __repr__(self):
        return '<SfoPartitionsInfo %s>' % self.update_time


class BeatHeartInfo(db.Model):
    __tablename__ = 'sfo_beatheart_info'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    data_model = db.Column(db.String(128), nullable=True)
    cluster_name = db.Column(db.String(128), nullable=True)
    hostname = db.Column(db.String(128), nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<BeatHeartInfo %s>' % self.guid

class SfoHostMonitor(db.Model):
    __tablename__ = 'sfo_host_monitor_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    data_model = db.Column(db.String(128), nullable=True)
    cluster_name = db.Column(db.String(128), nullable=True)
    host_name = db.Column(db.String(128), nullable=True)
    host_cpu_rate = db.Column(db.String(1024), nullable=True)
    host_mem_rate = db.Column(db.String(1024), nullable=True)
    host_net_rate = db.Column(db.String(1024), nullable=True)
    host_net_stat = db.Column(db.String(1024), nullable=True)
    host_disk_stat = db.Column(db.String(1024), nullable=True)
    host_file_rate = db.Column(db.Text, nullable=True)
    host_rw_file = db.Column(db.String(1024), nullable=True)
    host_ntp_time = db.Column(db.String(128), nullable=True)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoHostMonitor %s>' % self.guid

class SfoHostMonitor_5min(db.Model):
    __tablename__ = 'sfo_host_monitor_data_5min'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    data_model = db.Column(db.String(128), nullable=True)
    cluster_name = db.Column(db.String(128), nullable=True)
    host_name = db.Column(db.String(128), nullable=True)
    host_cpu_rate = db.Column(db.String(1024), nullable=True)
    host_mem_rate = db.Column(db.String(1024), nullable=True)
    host_net_rate = db.Column(db.String(1024), nullable=True)
    host_net_stat = db.Column(db.String(1024), nullable=True)
    host_disk_stat = db.Column(db.String(1024), nullable=True)
    host_file_rate = db.Column(db.Text, nullable=True)
    host_rw_file = db.Column(db.String(1024), nullable=True)
    host_ntp_time = db.Column(db.String(128), nullable=True)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoHostMonitor_5min %s>' % self.guid

class SfoHostMonitor_hour(db.Model):
    __tablename__ = 'sfo_host_monitor_data_hour'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    data_model = db.Column(db.String(128), nullable=True)
    cluster_name = db.Column(db.String(128), nullable=True)
    host_name = db.Column(db.String(128), nullable=True)
    host_cpu_rate = db.Column(db.String(1024), nullable=True)
    host_mem_rate = db.Column(db.String(1024), nullable=True)
    host_net_rate = db.Column(db.String(1024), nullable=True)
    host_net_stat = db.Column(db.String(1024), nullable=True)
    host_disk_stat = db.Column(db.String(1024), nullable=True)
    host_file_rate = db.Column(db.Text, nullable=True)
    host_rw_file = db.Column(db.String(1024), nullable=True)
    host_ntp_time = db.Column(db.String(128), nullable=True)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoHostMonitor_hour %s>' % self.guid

class SfoHostMonitor_day(db.Model):
    __tablename__ = 'sfo_host_monitor_data_day'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    data_model = db.Column(db.String(128), nullable=True)
    cluster_name = db.Column(db.String(128), nullable=True)
    host_name = db.Column(db.String(128), nullable=True)
    host_cpu_rate = db.Column(db.String(1024), nullable=True)
    host_mem_rate = db.Column(db.String(1024), nullable=True)
    host_net_rate = db.Column(db.String(1024), nullable=True)
    host_net_stat = db.Column(db.String(1024), nullable=True)
    host_disk_stat = db.Column(db.String(1024), nullable=True)
    host_file_rate = db.Column(db.Text, nullable=True)
    host_rw_file = db.Column(db.String(1024), nullable=True)
    host_ntp_time = db.Column(db.String(128), nullable=True)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoHostMonitor_day %s>' % self.guid

class SfoHostMonitorHistory(db.Model):
    __tablename__ = 'sfo_host_monitor_data_his'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    data_model = db.Column(db.String(128), nullable=True)
    cluster_name = db.Column(db.String(128), nullable=True)
    host_name = db.Column(db.String(128), nullable=True)
    host_cpu_rate = db.Column(db.String(1024), nullable=True)
    host_mem_rate = db.Column(db.String(1024), nullable=True)
    host_net_rate = db.Column(db.String(1024), nullable=True)
    host_net_stat = db.Column(db.String(1024), nullable=True)
    host_disk_stat = db.Column(db.String(1024), nullable=True)
    host_file_rate = db.Column(db.String(1024), nullable=True)
    host_rw_file = db.Column(db.String(1024), nullable=True)
    host_ntp_time = db.Column(db.String(128), nullable=True)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoHostMonitorHistory %s>' % self.guid

class SfoCheckReport(db.Model):
    __tablename__ = 'sfo_check_report_data'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    subject_name = db.Column(db.String(128), nullable=True)
    item_name = db.Column(db.String(128), nullable=True)
    check_command = db.Column(db.String(1024), nullable=True)
    check_result = db.Column(db.String(128), nullable=True)
    check_remark = db.Column(db.Text, nullable=True)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoCheckReport %s>' % self.guid

class SfoSwiftUser(db.Model):

    __tablename__ = 'sfo_swift_user'

    guid = db.Column(db.String(128), primary_key=True,  nullable=False)
    cluster_name = db.Column(db.String(128), nullable=True)
    account_id = db.Column(db.String(128), nullable=True)
    role_name = db.Column(db.String(128), nullable=True)
    system_user = db.Column(db.String(128), nullable=False)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('system_user', 'account_id', 'role_name', name='uix_user_account_role_systemuser_accountid_rolename'),
    )

    def __repr__(self):
        return '<SfoSwiftUser %s>' % self.guid


class SfoSwiftRole(db.Model):

    __tablename__ = 'sfo_swift_role'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    role_name = db.Column(db.String(128),unique=True, nullable=False)
    role_desc = db.Column(db.String(128), nullable=True)
    role_meta = db.Column(db.String(128), nullable=False)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoSwiftRole %s>' % self.guid

class SfoAlarmLog(db.Model):
    __tablename__ = 'sfo_alarm_log'

    guid = db.Column(db.String(128), primary_key=True,unique=True,nullable=False)
    alarm_device = db.Column(db.String(128), nullable=True)
    alarm_type = db.Column(db.String(128), nullable=True)
    hostname = db.Column(db.String(128), nullable=True)
    device_name = db.Column(db.String(128), nullable=True)
    alarm_message = db.Column(db.String(128))
    alarm_level = db.Column(db.String(128), nullable=True)
    alarm_result = db.Column(db.String(128))  # 0 未处理 1 已处理 2 不处理
    add_time = db.Column(db.String(128))
    update_time = db.Column(db.String(128))

    def __repr__(self):
        return '<SfoAlarmLog %s>' % self.guid

class SfoSystemInput(db.Model):
    __tablename__ = 'sfo_system_input_info'

    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    sys_code = db.Column(db.String(128), nullable=True)
    sys_id = db.Column(db.String(128), nullable=True)
    sys_key = db.Column(db.String(128), nullable=True)
    sys_token = db.Column(db.String(128), nullable=True)
    sys_stat = db.Column(db.String(128), nullable=True)
    sys_url = db.Column(db.String(1024), nullable=True)
    extend = db.Column(db.Text, nullable=True)
    add_time = db.Column(db.String(128),nullable=True)

    def __repr__(self):
        return '<SfoSystemInput %s>' % self.guid


class SfoClusterTps(db.Model):
    __tablename__ = 'sfo_cluster_tps_info'
    guid = db.Column(db.String(128), primary_key=True, unique=True, nullable=False)
    cluster_name = db.Column(db.String(128), nullable=False)
    avg_time = db.Column(db.String(128), nullable=False)
    head_time = db.Column(db.String(128), nullable=False)
    get_time = db.Column(db.String(128), nullable=False)
    put_time = db.Column(db.String(128), nullable=False)
    post_time = db.Column(db.String(128), nullable=False)
    delete_time = db.Column(db.String(128), nullable=False)
    extend = db.Column(db.Text, nullable=False)
    add_time = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return '<SfoClusterTps %s>' % self.guid
