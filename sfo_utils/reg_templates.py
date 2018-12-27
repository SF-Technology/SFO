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

"""Module for parsing the output of info"""

from sfo_utils.util_tool import CommandParser

REGEX_TEMPLATE = r'\n%s\:([\ \t])+(?P<%s>.*)'
class CPUInfoParser(CommandParser):
    ITEM_SEPERATOR = "\n\n"
    ITEM_REGEXS = [
        REGEX_TEMPLATE % (r'Model\ name', 'cpu_model'),
        REGEX_TEMPLATE % (r'Socket\(s\)', 'cpu_sockets'),
        REGEX_TEMPLATE % (r'Core\(s\)\ per\ socket', 'cpu_cores'),
        REGEX_TEMPLATE % (r'CPU\(s\)', 'cpu_processors'),
        REGEX_TEMPLATE % (r'CPU\ MHz', 'cpu_frequency'),
    ]

class CpuName(CommandParser):
    ITEM_REGEXS = [
        r'(.)*\ (?P<cpu_id>cpu[0-9]+)',
    ]

class EthernetParser(CommandParser):
    ITEM_REGEXS = [
        #r'(.)*\ (?P<net>eth[0-9]+)',
        r'(.)*\ (?P<net>(((bond)|(eth))[0-9]+))\:',
        r'(.)*link/ether\ (?P<mac>([0-9a-fA-F]{2})(([/\s:][0-9a-fA-F]{2}){5}))',
        r'(.)*inet\ (?P<ipaddr>(\d{1,3}.){3}\d{1,3})',
        r'(.)*Ethernet\ controller\:(?P<controller>.*)',
    ]

class IPaddrParser(CommandParser):
    ITEM_REGEXS = [
        r'[\s\S]*inet\ (?P<ipaddr>(\d{1,3}.){3}\d{1,3})\/',
    ]

class BusinfoParser(CommandParser):
    ITEM_REGEXS = [
        r'\nbus-info:[\ \t]*(?P<businfo>.*)\n',
    ]

class SpeedParser(CommandParser):
    ITEM_REGEXS = [
        r'[\s\S]*Speed:(?P<speed>.*)\n',
    ]

class DiskParser(CommandParser):
    ITEM_REGEXS = [
        #r'Disk\ \/(?P<disk>.*)\:',
        r'Number\ of\ DISK\ GROUPS\:(?P<disk_number>.*)\n',
        r'\nSize([\ \t])+\:(?P<disk_useful_size>.*)\n',
        r'PD\ Type\:(?P<disk_type>.*)\n',
        r'Device\ Speed\:(?P<disk_rw_rate>.*)\n',
        r'Raw Size:(?P<disk_capacity>.*)\[',
        r'WWN:(?P<disk_wwn>.*)\n',
    ]

class DiskGroupParser(CommandParser):
    ITEM_REGEXS = [
        r'RAID\ Level[\ \t]+\:[\ \t]+Primary-(?P<raid_type>[0-9]+)',
        r'\nSize([\ \t])+\:(?P<disk_size>.*)\n',
        r'Number\ Of\ Drives[\ \t]+:[\ \t]+(?P<disk_num>[0-9]+)\n',
        r'Device\ Speed\:(?P<disk_rw_rate>.*)\n',
        r'Raw\ Size:(?P<disk_capacity>.*)\[',
        r'PD\ Type:(?P<disk_type>.*)\n',
    ]

class DiskNameParser(CommandParser):
    ITEM_REGEXS = [
        r'\/dev\/(?P<disk_name>sd.*)\:',
    ]

class DiskUuidParser(CommandParser):
    ITEM_REGEXS = [
        r'\/dev\/.*UUID\=\"(?P<disk_uuid>.*)\"\ ',
    ]

class NodeServiceParser(CommandParser):
    ITEM_REGEXS = [
        r'(.)*swift-proxy-server(?P<srv_proxy>.*)\n',
        r'(.)*swift-account-server(?P<srv_account>.*)\n',
        r'(.)*swift-account-auditor(?P<srv_account_auditor>.*)\n',
        r'(.)*swift-account-reaper(?P<srv_account_reaper>.*)\n',
        r'(.)*swift-account-replicator(?P<srv_account_replicator>.*)\n',
        r'(.)*swift-container-server(?P<srv_container>.*)\n',
        r'(.)*swift-container-auditor(?P<srv_container_auditor>.*)\n',
        r'(.)*swift-container-replicator(?P<srv_container_replicator>.*)\n',
        r'(.)*swift-container-updater(?P<srv_container_updater>.*)\n',
        r'(.)*swift-container-sync(?P<srv_container_sync>.*)\n',
        r'(.)*swift-container-reconciler(?P<srv_container_reconciler>.*)\n',
        r'(.)*swift-object-server(?P<srv_object>.*)\n',
        r'(.)*swift-object-auditor(?P<srv_object_auditor>.*)\n',
        r'(.)*swift-object-replicator(?P<srv_object_replicator>.*)\n',
        r'(.)*swift-object-updater(?P<srv_object_updater>.*)\n',
        r'(.)*swift-object-expirer(?P<srv_object_expirer>.*)\n',
        r'(.)*swift-object-reconstructor(?P<srv_object_reconstructor>.*)\n',
    ]

class DmidecodeMemory(CommandParser):
    ITEM_REGEXS = [
        #memory info
        r'Physical\ Memory\ Array[\s\S]*Maximum\ Capacity:\ (?P<mem_total>.*)',
        r'Physical\ Memory\ Array[\s\S]*Number\ Of\ Devices:\ (?P<mem_number>.*)',
        r'(.)*Size:\ (?P<mem_single_size>.*)',
        r'(.)*Speed:\ (?P<mem_frequency>.*)',
    ]

class DmidecodeBios(CommandParser):
    ITEM_REGEXS = [
        #bios info
        r'BIOS\ Information[\s\S]*Version:\ (?P<mf_bios_version>.*)\n',
        r'BIOS\ Information[\s\S]*Release\ Date:\ (?P<mf_bios_date>.*)\n',
    ]

class DmidecodeSystem(CommandParser):
    ITEM_REGEXS = [
        #system info
        r'System\ Information\n[\ \t]Manufacturer:\ (?P<mf_name>.*)\n',
        r'System\ Information[\s\S]*Product\ Name:\ (?P<mf_model>.*)\n',
        r'System\ Information[\s\S]*Serial\ Number:\ (?P<mf_serial_number>.*)\n',
    ]

LABEL_REGEX = r'[\w+\ \.\,\:\+\&\-\/\[\]\(\)]+'
CODE_REGEX = r'[0-9a-fA-F]{4}'
BUSID_REGEX = r'[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-9a-fA-F]'
class LspciNNMMParser(CommandParser):
    """Parser object for the output of lspci -nnmm"""
    ITEM_REGEXS = [
        r'(?P<pci_device_bus_id>(' + BUSID_REGEX + r'))\ "(?P<pci_device_class_name>' + LABEL_REGEX + r')\ \[(?P<pci_device_class>' + CODE_REGEX + r')\]"' \
        + r'\ "(?P<pci_vendor_name>' + LABEL_REGEX + r')\ \[(?P<pci_vendor_id>' + CODE_REGEX + r')\]"\ "(?P<pci_device_name>' + LABEL_REGEX + r')\ \[(?P<pci_device_id>' + CODE_REGEX + r')\]"' \
        + r'\ .*\"((?P<pci_subvendor_name>' + LABEL_REGEX + r')\ \[(?P<pci_subvendor_id>' + CODE_REGEX + r')\])*"\ "((?P<pci_subdevice_name>' + LABEL_REGEX + r')\ \[(?P<pci_subdevice_id>' + CODE_REGEX + r')\])*',
    ]
    ITEM_SEPERATOR = "\n"

class LspciVVParser(CommandParser):
    """Parser object for the output of lspci -vv"""
    ITEM_REGEXS = [
        r'(?P<pci_device_bus_id>(' + BUSID_REGEX + r'))\ (?P<pci_device_class_name>' + LABEL_REGEX + r'):\ (?P<pci_device_string>(.*))\n',
        r'Product\ Name:\ (?P<pci_device_vpd_product_name>(.)*)\n',
        r'Subsystem:\ (?P<pci_device_sub_string>(.)*)\n',
    ]
    ITEM_SEPERATOR = "\n\n"
    MUST_HAVE_FIELDS = [
        'pci_device_bus_id',
        'pci_device_class_name',
        'pci_device_string',
    ]

class LspciNParser(CommandParser):
    """Parser object for the output of lspci -n"""
    #ff:0d.1 0880: 8086:0ee3 (rev 04)
    ITEM_REGEXS = [
        r'(?P<pci_device_bus_id>(' + BUSID_REGEX + r'))\ (?P<pci_device_class>' + CODE_REGEX + r'):\ (?P<pci_vendor_id>' + CODE_REGEX + r'):(?P<pci_device_id>' + CODE_REGEX + r')',
    ]
    ITEM_SEPERATOR = "\n"

    MUST_HAVE_FIELDS = [
        'pci_device_bus_id',
        'pci_device_id',
        'pci_vendor_id',
        'pci_device_class',
    ]
class RingParser(CommandParser):
    ITEM_REGEXS = [
        #ring info
        r'[\s\S]*(?P<partitions>[0-9]+).*partitions,',
        r'[\s\S]*partitions,(?P<replicas>.*)replicas,',
        r'[\s\S]*replicas,(?P<regions>.*)regions,',
        r'[\s\S]*regions,(?P<zones>.*)zones,',
        r'[\s\S]*zones,(?P<devices>.*)devices\,',
        r'[\s\S]*devices,(?P<balance>.*)balance,',
        r'[\s\S]*balance,(?P<dispersion>.*)dispersion\n',
    ]

class PCIDevice(object):
    NONE_VALUE = 'unknown'
    def __init__(self, record):
        self.rec = record

    def lookup_value(self, k):
        if k in self.rec:
            return self.rec[k]
        else:
            return None

    def _fmt(self, value, wrap=None):
        if not value:
            return self.NONE_VALUE
        else:
            if wrap:
                return "%s%s%s" % (wrap, value, wrap)
            else:
                return value

    def get_device_name(self):
        wrap = None
        name = self.lookup_value('pci_device_name')

        # Fall back to using pci_device_string if it exists.
        if not name:
            name = self.lookup_value('pci_device_string')
            wrap = '-'

        if name == 'Device':
            # If the input has come from lspci, this is the value for
            # not being able to find a key in the pciids db.
            return '[Device %s]' % self.get_device_id()
        else:
            return self._fmt(name, wrap)


    def get_device_id(self):
        return self._fmt(self.lookup_value('pci_device_id'))

    def get_vendor_name(self):
        return self._fmt(self.lookup_value('pci_vendor_name'))

    def get_vendor_id(self):
        return self._fmt(self.lookup_value('pci_vendor_id'))

    def get_subdevice_name(self):
        name = self.lookup_value('pci_subdevice_name')
        wrap = None

        # Fall back to using pci_device_string if it exists.
        if not name:
            name = self.lookup_value('pci_device_sub_string')
            wrap = '-'

        if name == 'Device':
            # If the input has come from lspci, this is the value for
            # not being able to find a key in the pciids db.
            return '[Device %s]' % self.get_subdevice_id()
        else:
            return self._fmt(name, wrap)

    def get_subdevice_id(self):
        return self._fmt(self.lookup_value('pci_subdevice_id'))

    def get_subvendor_name(self):
        return self._fmt(self.lookup_value('pci_subvendor_name'))

    def get_subvendor_id(self):
        return self._fmt(self.lookup_value('pci_subvendor_id'))

    def get_pci_id(self):
        return "%s:%s %s:%s" % (
            self._fmt(self.lookup_value('pci_vendor_id')),
            self._fmt(self.lookup_value('pci_device_id')),
            self._fmt(self.lookup_value('pci_subvendor_id')),
            self._fmt(self.lookup_value('pci_subdevice_id')),
        )

    def get_pci_class(self):
        return self._fmt(self.lookup_value('pci_device_class'))

    def is_subdevice(self):
        return self.lookup_value('pci_subvendor_id') and self.lookup_value('pci_subdevice_id') or self.lookup_value('pci_device_sub_string')

    def get_info(self):

        if self.is_subdevice():
            return "%s %s (%s %s)" % (self.get_subvendor_name(), self.get_subdevice_name(), self.get_vendor_name(), self.get_device_name())
        else:
            return "%s %s" % (self.get_vendor_name(), self.get_device_name())

    def get_rec(self):
        rec = {}
        rec['vendor_name'] = self.get_vendor_name()
        rec['device_name'] = self.get_device_name()
        rec['vendor_id'] = self.get_vendor_id()
        rec['device_id'] = self.get_device_id()
        rec['class'] = self.get_pci_class()
        rec['subvendor_name'] = self.get_subvendor_name()
        rec['subdevice_name'] = self.get_subdevice_name()
        rec['subvendor_id'] = self.get_subvendor_id()
        rec['subdevice_id'] = self.get_subdevice_id()

        return rec

class OsStat(CommandParser):
    ITEM_REGEXS = [
        #os stat info
        r'[\s\S]*COMMAND[\s\S]*up\ (?P<host_runtime>.*[0-9]{2}\:[0-9]{2}),',
        r'[\s\S]*COMMAND[\s\S]*load\ average\:\ (?P<host_average_load>(([0-9]+\.[0-9]{2,}\,[\ \t]+){2}[0-9]+\.[0-9]{2,}))',
        r'[\s\S]*COMMAND[\s\S]*[0-9]{2}:[0-9]{2}\,[\ \t]+(?P<host_login_users>.*)users',
        r'[\s\S]*COMMAND[\s\S]*top\ -\ (?P<host_time>.*)[\ \t]+up',
        r'[\s\S]*COMMAND[\s\S]*Tasks\:[\ \t]+(?P<thread_total>.*)total',
        r'[\s\S]*COMMAND[\s\S]*total\,[\ \t]+(?P<thread_running>.*)running',
        r'[\s\S]*COMMAND[\s\S]*running\,[\ \t]+(?P<thread_sleeping>.*)sleeping',
        r'[\s\S]*COMMAND[\s\S]*sleeping\,[\ \t]+(?P<thread_stoped>.*)stopped',
        r'[\s\S]*COMMAND[\s\S]*stopped\,[\ \t]+(?P<thread_zombie>.*)zombie',
        r'[\s\S]*COMMAND[\s\S]*\%Cpu\(s\)\:[\ \t]+(?P<cpu_us>.*)us',
        r'[\s\S]*COMMAND[\s\S]*us\,[\ \t]+(?P<cpu_sy>.*)sy',
        r'[\s\S]*COMMAND[\s\S]*sy\,[\ \t]+(?P<cpu_ni>.*)ni',
        r'[\s\S]*COMMAND[\s\S]*ni\,[\ \t]+(?P<cpu_id>.*)id',
        r'[\s\S]*COMMAND[\s\S]*id\,[\ \t]+(?P<cpu_wa>.*)wa',
        r'[\s\S]*COMMAND[\s\S]*wa\,[\ \t]+(?P<cpu_hi>.*)hi',
        r'[\s\S]*COMMAND[\s\S]*hi\,[\ \t]+(?P<cpu_si>.*)si',
        r'[\s\S]*COMMAND[\s\S]*si\,[\ \t]+(?P<cpu_st>.*)st',
        r'[\s\S]*COMMAND[\s\S]*KiB\ Mem\ \:[\ \t]+(?P<mem_total>.*)total',
        r'[\s\S]*COMMAND[\s\S]*KiB\ Mem\ \:.*total\,[\ \t]+(?P<mem_free>.*)free',
        r'[\s\S]*COMMAND[\s\S]*KiB\ Mem\ \:.*free\,[\ \t]+(?P<mem_used>.*)used',
        r'[\s\S]*COMMAND[\s\S]*KiB\ Mem\ \:.*used\,[\ \t]+(?P<mem_buffers>.*)buff',
        r'[\s\S]*COMMAND[\s\S]*KiB\ Swap\:[\ \t]+(?P<swap_total>.*)total',
        r'[\s\S]*COMMAND[\s\S]*KiB\ Swap\:.*total\,[\ \t]+(?P<swap_free>.*)free',
        r'[\s\S]*COMMAND[\s\S]*KiB\ Swap\:.*free\,[\ \t]+(?P<swap_used>.*)used',
        r'[\s\S]*COMMAND[\s\S]*KiB\ Swap\:.*used\,[\ \t]+(?P<swap_cached>.*)avail',
    ]


