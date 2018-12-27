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

from sfo_agent.kafka_producer import ProduceKafkaInfo
from sfo_common.agent import Agent
from sfo_common.import_common import *


#schedule tasks
def get_host_json_schl():
    '''
    起线程定时执行主机硬件信息收集
    起线程避免主进程的schedule因等待函数执行完成而卡住
    :return:
    '''
    try:
        ia = InfoAcquisition()
        threading.Thread(target=ia.get_host_json).start()
    except Exception as ex:
        logger.info("get_host_json_schl function excute exception:" + str(ex))

def get_node_json_schl():
    '''
    起线程定时执行主机状态数据收集
    起线程避免主进程的schedule因等待函数执行完成而卡住
    :return:
    '''
    try:
        ia = InfoAcquisition()
        threading.Thread(target=ia.get_node_json,args=['SfoNodeStat']).start()
    except Exception as ex:
        logger.exception("get_node_json_schl function excute exception:" + str(ex))

def get_node_disk_stat_json_schl():
    '''
    起线程定时执行disk性能数据收集
    起线程避免主进程的schedule因等待函数执行完成而卡住
    :return:
    '''
    try:
        ia = InfoAcquisition()
        threading.Thread(target=ia.get_node_disk_stat_json).start()
    except Exception as ex:
        logger.exception("get_node_disk_stat_json_schl function excute exception:" + str(ex))

def get_host_monitor_json_schl():
    '''
    起线程定时执行监控数据收集
    起线程避免主进程的schedule因等待函数执行完成而卡住
    :return:
    '''
    try:
        ia = InfoAcquisition()
        threading.Thread(target=ia.get_host_monitor_json).start()
    except Exception as ex:
        logger.exception("get_host_monitor_json_schl function excute exception:" + str(ex))

def get_ring_json_schl():
    '''
    起线程定时执行ring信息收集
    起线程避免主进程的schedule因等待函数执行完成而卡住
    :return:
    '''
    try:
        ia = InfoAcquisition()
        threading.Thread(target=ia.get_ring_json).start()
    except Exception as ex:
        logger.exception("get_ring_json_schl function excute exception:" + str(ex))

class SysUnitAgnet(Agent):
    def __init__(self, pidfile):
        Agent.__init__(self, pidfile)

    def run(self):
        '''
        重写Agent的run函数，实现守护进程的指定功能
        :return:
        '''
        try:
            sys.stdout.flush()
            hostname = socket.getfqdn()
            hostip = socket.gethostbyname(hostname)
            logger.info("hostname is {}, ip is {}".format(hostname, hostip))
            # use schedule
            schedule.every(config.host_refresh).seconds.do(get_host_json_schl)
            schedule.every(config.node_refresh).seconds.do(get_node_json_schl)
            schedule.every(config.disk_refresh).seconds.do(get_node_disk_stat_json_schl)
            schedule.every(config.mon_refresh).seconds.do(get_host_monitor_json_schl)
            schedule.every(config.host_refresh).seconds.do(get_ring_json_schl)
            schedule.run_all(0)
            while True:
                schedule.run_pending()
                time.sleep(1)
        except Exception as ex:
            logger.exception("sysunitagent was stopped by exception {}".format(str(ex)))


class HostInfo(object):
    '''
    主机硬件信息获取类
    '''
    def __init__(self):
        pass

    def get_os_info(self):
        '''
        获取操作系统版本信息
        :return:
        '''
        osinfo = {}
        try:
            osinfo['host_name'] = socket.getfqdn()
            osinfo['os_version'] = "-".join(platform.linux_distribution())
            osinfo['os_kernel_version'] = platform.release()
            return osinfo
        except Exception as ex:
            logger.exception("get_os_info function excute exception:" + str(ex))

    def get_cpu_dev_info(self):
        '''
        获取CPU的硬件信息
        :return:
        '''
        try:
            result = util.excute_command('lscpu')
            if result:
                parser = reg_templates.CPUInfoParser(result)
                return parser.parse_items()
        except Exception as ex:
            logger.exception("get_cpu_info function excute exception:" + str(ex))

    def get_mem_dev_info(self):
        '''
        获取内存的硬件信息
        :return:
        '''
        try:
            result = util.excute_command('dmidecode -t memory')
            if result:
                parser = reg_templates.DmidecodeMemory(result)
                rec = parser.parse()
                return rec
        except Exception as ex:
            logger.exception("get_mem_dev_info function excute exception:" + str(ex))

    def get_bios_dev_info(self):
        '''
        获取主机的BIOS信息
        :return:
        '''
        try:
            rec = {}
            biosdata = util.excute_command('dmidecode -t bios')
            if biosdata :
                parser = reg_templates.DmidecodeBios(biosdata)
                resbios = parser.parse()
                if resbios.has_key('mf_bios_version'):
                    rec['mf_bios_version'] = resbios['mf_bios_version']
                else:
                    rec['mf_bios_version'] = 'N/A'
                if resbios.has_key('mf_bios_date'):
                    rec['mf_bios_date'] = resbios['mf_bios_date']
                else:
                    rec['mf_bios_date'] = 'N/A'

            sysdata = util.excute_command('dmidecode -t system')
            if sysdata :
                sysparser = reg_templates.DmidecodeSystem(sysdata)
                ressys = sysparser.parse()
                if ressys.has_key('mf_name'):
                    rec['mf_name'] = ressys['mf_name']
                else:
                    rec['mf_name'] = 'N/A'
                if ressys.has_key('mf_model'):
                    rec['mf_model'] = ressys['mf_model']
                else:
                    rec['mf_model'] = 'N/A'
                if ressys.has_key('mf_serial_number'):
                    rec['mf_serial_number'] = ressys['mf_serial_number']
                else:
                    rec['mf_serial_number'] = 'N/A'

            memdata = util.excute_command('dmidecode -t memory')
            if memdata :
                memparser = reg_templates.DmidecodeMemory(memdata)
                resmem = memparser.parse()
                total = 0
                frq = []
                sngsize = []
                num = 0
                if resmem.has_key('mem_single_size'):
                    sngs = str(resmem['mem_single_size']).split(',')
                    for sng in sngs:
                        if str(sng).strip() not in sngsize:
                            if str(sng).replace('MB','').strip().isdigit():
                                sngsize.append(str(sng).strip())
                        if 'MB' in sng:
                            tmp = str(sng).replace('MB','').strip()
                            if tmp.isdigit():
                                total += int(tmp)
                                num += 1

                    rec['mem_single_size'] = ', '.join(sngsize)
                else:
                    rec['mem_single_size'] = 'N/A'
                if resmem.has_key('mem_total'):
                    rec['mem_total'] = 'Max:{}, Now:{} GB'.format(resmem['mem_total'],str(total/1024))
                else:
                    rec['mem_total'] = 'N/A'

                if resmem.has_key('mem_number'):
                    rec['mem_number'] = 'Max:{}, Now:{}'.format(resmem['mem_number'],str(num))
                else:
                    rec['mem_number'] = 'N/A'

                if resmem.has_key('mem_frequency'):
                    frqs = str(resmem['mem_frequency']).split(',')
                    for rq in frqs:
                        if str(rq).strip() not in frq:
                            if str(rq).replace('MHz','').strip().isdigit():
                                frq.append(str(rq).strip())
                    rec['mem_frequency'] = ', '.join(frq)
                else:
                    rec['mem_frequency'] = 'N/A'
            return rec
        except Exception as ex:
            logger.exception("get_bios_dev_info function excute exception:" + str(ex))

    def get_net_dev_info(self):
        '''
        获取网卡的硬件信息
        :return:
        '''
        try:
            eth = []
            res = {}
            eth_res = {}
            mac_res = {}
            ip_res = {}
            ctl_res = {}
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            nets = addrs.keys()
            for net in nets:
                if 'eth' in net or 'bond' in net:
                    eth.append(net)
                    eth_res[net] = '{}Mb/s'.format(stats[net].speed)
                    for ip_addr in addrs[net]:
                        if ip_addr[0] == 2:
                            ip_res[net] = ip_addr[1]
                        if ip_addr[0] == 17:
                            mac_res[net] = ip_addr[1]
                    if not ip_res.has_key(net):
                        ip_res[net] = 'N/A'

                    # 获取指定网卡的硬件型号
                    ethdata = util.excute_command('ethtool -i ' + net)
                    ethparser = reg_templates.BusinfoParser(ethdata)
                    ethrec = ethparser.parse()
                    if ethrec.has_key('businfo'):
                        businfo = str(ethrec['businfo']).replace('0000:', '')
                        contrinfo = util.excute_command("lspci | grep -i '" + businfo + "'")
                        ctlinfo = contrinfo.split(':')[2]
                        ctl_res[net] = ctlinfo

            res['net_speed'] = json.dumps(eth_res, encoding='utf-8', ensure_ascii=True)
            res['net_number'] = len(eth)
            res['net_mac_address'] = json.dumps(mac_res, encoding='utf-8', ensure_ascii=True)
            res['net_ip_address'] = json.dumps(ip_res, encoding='utf-8', ensure_ascii=True)
            res['net_model'] = json.dumps(ctl_res, encoding='utf-8', ensure_ascii=True)

            return res
        except Exception as ex:
            logger.exception("get_net_dev_info function excute exception:" + str(ex))

    def get_disk_dev_info(self):
        '''
        获取磁盘的硬件信息
        :return:
        '''
        try:
            rec = {}
            sysdata = util.excute_command("dmidecode -t system")
            factory = re.search('Manufacturer: .*',sysdata)
            if factory :
                fname = str(factory.group(0)).split(':')[1].strip()
                if fname.upper().strip() == "HP":
                    rec = self.get_hp_disk_dev_info()
                else:
                    rec = self.get_lsi_disk_dev_info()
            return rec
        except Exception as ex:
            logger.exception("get_disk_dev_info function excute exception:" + str(ex))

    def get_disk_names(self):
        '''
        获取主机上所有磁盘的磁盘名 （使用blkid命令，发现有些情况下部分磁盘不可见,谨慎使用）
        :return:
        '''
        try:
            result = util.excute_command('blkid')
            if result :
                parser = reg_templates.DiskNameParser(result)
                return parser.parse()
        except Exception as ex:
            logger.exception("get_disk_name function excute exception:" + str(ex))

    def get_hp_disk_dev_info(self):
        '''
        获取HP的磁盘信息
        :return:
        '''
        try:
            rec = {}
            diskary = self.get_lsscsi_disk_info()
            if diskary:
                raid_type = {}
                disk_usize = {}
                disk_capacity = {}
                disknum = 0
                diskgroup = 0
                disk_number = {}
                disk_rate = {}
                for ary in diskary:
                    if ary is None:
                        continue
                    aryid = str(ary['disk_lname']).replace('/dev/sd','').upper()
                    lcmdstr = 'hpssacli ctrl slot=0 array {} ld all show'.format(aryid)
                    pcmdstr = 'hpssacli ctrl slot=0 array {} pd all show'.format(aryid)
                    ldata = util.excute_command(lcmdstr)
                    pdata = util.excute_command(pcmdstr)
                    if ldata and 'Error' not in ldata:
                        diskgroup += 1
                        m_data = re.findall('\(.*\)',ldata)
                        if len(m_data) > 1:
                            for dt in m_data:
                                if 'OK' in dt:
                                    if len(str(dt).split(',')) > 2:
                                        raid_type[ary['disk_lname']] = str(str(dt).split(',')[1])
                                        disk_usize[ary['disk_lname']] = str(str(dt).split(',')[0]).replace('(','')

                    if pdata and 'Error' not in pdata:
                        tp = []
                        sz = []
                        mydata = re.findall('\(.*\)', pdata)
                        if len(mydata) > 1:
                            for data in mydata:
                                if 'OK' in data:
                                    disknum += 1
                                    mdata = str(data).split(',')
                                    if len(mdata) > 2:
                                        tp.append(str(mdata[1]).strip())
                                        sz.append(str(mdata[2]).strip())
                            if len(tp) > 0 and len(sz) > 0:
                                dtype = ','.join(tp)
                                dsize = ','.join(sz)
                                disk_capacity[ary['disk_lname']] = '{}-{}'.format(dsize,dtype)

                disk_number['disknum'] = disknum
                disk_number['diskgroup'] = diskgroup
                rec['disk_type'] = json.dumps(raid_type, encoding='utf-8', ensure_ascii=True)
                rec['disk_number'] = json.dumps(disk_number, encoding='utf-8', ensure_ascii=True)
                rec['disk_useful_size'] = json.dumps(disk_usize, encoding='utf-8', ensure_ascii=True)
                rec['disk_capacity'] = json.dumps(disk_capacity, encoding='utf-8', ensure_ascii=True)
                rec['disk_rw_rate'] = json.dumps(disk_rate, encoding='utf-8', ensure_ascii=True)

            return rec
        except Exception as ex:
            logger.exception("get_hp_disk_dev_info function excute exception:" + str(ex))


    def get_lsi_disk_dev_info(self):
        '''
        获取LSI厂商的磁盘信息
        :return:
        '''
        try:
            rec = {}
            diskgroups = self.get_lsscsi_disk_info()
            if diskgroups:
                raid_type = {}
                disk_usize = {}
                disk_capacity = {}
                disknum = 0
                diskgroup = 0
                disk_number = {}
                disk_rate = {}

                for group in diskgroups:
                    if str(group['disk_manufacturer']).upper().strip() == "HP":
                        raise RuntimeError('This Raid card is not supported!')
                    ids = str(group['disk_id']).split(':')
                    groupinfo = self.get_lsi_diskgroup_info(ids[0],str("DISK GROUP: {}".format(str(ids[2]))),str("DISK GROUP: {}".format(str(int(ids[2])+1))))
                    if groupinfo and str(groupinfo) <> "N/A":
                        diskgroup += 1
                        groupparser = reg_templates.DiskGroupParser(groupinfo)
                        grouprec = groupparser.parse()
                        if grouprec.has_key('raid_type'):
                            raid_type[group['disk_lname']] = "Raid {}".format(str(grouprec['raid_type']))
                        if grouprec.has_key('disk_num'):
                            disknum += int(grouprec['disk_num'])
                        if grouprec.has_key('disk_size'):
                            disk_usize[group['disk_lname']] = str(grouprec['disk_size'])
                        if grouprec.has_key('disk_capacity') and grouprec.has_key('disk_type'):
                            disk_capacity[group['disk_lname']] = "{}-{}".format(str(grouprec['disk_capacity']),str(grouprec['disk_type']))
                        if grouprec.has_key('disk_rw_rate'):
                            disk_rate[group['disk_lname']] = str(grouprec['disk_rw_rate'])
                disk_number['disknum'] = disknum
                disk_number['diskgroup'] = diskgroup
                rec['disk_type'] = json.dumps(raid_type,encoding='utf-8',ensure_ascii=True)
                rec['disk_number'] = json.dumps(disk_number,encoding='utf-8',ensure_ascii=True)
                rec['disk_useful_size'] = json.dumps(disk_usize,encoding='utf-8',ensure_ascii=True)
                rec['disk_capacity'] = json.dumps(disk_capacity,encoding='utf-8',ensure_ascii=True)
                rec['disk_rw_rate'] = json.dumps(disk_rate,encoding='utf-8',ensure_ascii=True)
            return rec
        except Exception as ex:
            logger.exception("get_lsi_disk_dev_info function excute exception:" + str(ex))


    def get_lsscsi_disk_info(self):
        '''
        获取逻辑磁盘列表，返回一个集合
        :return:
        '''
        try:
            scsirec = []
            scsidata = util.exct_cmd('lsscsi')
            for data in scsidata:
                disk = {}
                if data:
                    regex = re.compile('\s+')
                    disk['scsi_type'] = regex.split(data)[1].strip()
                    if str(disk['scsi_type']).upper() == "DISK":
                        disk_id = re.search("[:0-9]+", data)
                        if disk_id :
                            disk['disk_id'] = disk_id.group(0).strip()
                        else:
                            continue
                        disk_lname = re.search("/dev/.*", data)
                        if disk_lname :
                            disk['disk_lname'] = disk_lname.group(0).strip()
                        else:
                            disk['disk_lname'] = "-"

                        disk['disk_manufacturer'] = regex.split(data)[2].strip()

                        scsirec.append(disk)
            return scsirec
        except Exception as ex:
            raise RuntimeError("get_lsscsi_disk_info function excute exception:" + str(ex))

    def get_lsi_diskgroup_info(self,adapter='0', startline='DISK GROUP: 0', endline='DISK GROUP: 1'):
        '''
        获取LSI厂家的磁盘组信息
        :param adapter:
        :param startline:
        :param endline:
        :return:
        '''
        try:
            groupdata = util.excute_command('/opt/MegaRAID/MegaCli/MegaCli64 -CfgDsply -a '+ adapter)
            groupinfo = re.search("{}[\s\S]*{}\n".format(startline,endline), groupdata)
            if groupinfo:
                return groupinfo.group(0)
            else:
                endline = "Exit Code: 0x00"
                groupinfo = re.search("{}[\s\S]*{}".format(startline, endline), groupdata)
                if groupinfo:
                    return groupinfo.group(0)
                else:
                    return "N/A"
        except Exception as ex:
            logger.exception("get_lsi_diskgroup_info function excute exception:" + str(ex))



    def get_rings(self):
        '''
        获取/etc/swift下的ring.gz,
        :return:
        '''
        try:
            result = util.excute_command("ls /etc/swift/ |grep \"ring.gz\|swift.conf\"")
            if result :
                parser = result.split('\n')
                parser = filter(lambda x: x, parser)
                return parser
        except Exception as ex:
            logger.exception("get_rings function excute exception:" + str(ex))



    def get_ring_file_md5(self, ring_gz_name):
        '''
        根据文件名计算文件内容的md5值
        :param ring_gz_name:
        :return:
        '''
        ring_gz_name = '/etc/swift/' + ring_gz_name
        try:
            result = util.excute_command('md5sum %s'%(ring_gz_name))
            if result :
                parser = result.split(' ')
                ring_md5 = parser[0]
                return ring_md5
        except Exception as ex:
            logger.exception("get_ring_file_md5 function excute exception:" + str(ex))

    def get_cluster_ring_info(self):
        '''
        根据swift ring文件收集集群配置信息
        :return:
        '''
        try:
            ringinfo = {}
            ac_ring = {}
            cn_ring = {}
            ob_ring = {}
            process_stat = util.excute_command('ps -ef |grep python |grep swift')
            if process_stat:
                pro_parser = reg_templates.NodeServiceParser(process_stat)
                pro_res = pro_parser.parse()
                if pro_res.has_key('srv_proxy'):
                    if os.path.exists('/etc/swift/account.builder'):
                        res_ac = util.excute_command("swift-ring-builder account.builder |sed -n '2p'")
                        ac_parser = reg_templates.RingParser(res_ac)
                        tmp_res = ac_parser.parse()
                        if tmp_res:
                            for key in tmp_res.keys():
                                ac_ring[key] = str(tmp_res[key]).strip()
                        ringinfo['account'] = ac_ring
                    if os.path.exists('/etc/swift/container.builder'):
                        res_cn = util.excute_command("swift-ring-builder container.builder |sed -n '2p'")
                        cn_parser = reg_templates.RingParser(res_cn)
                        tmp_res = cn_parser.parse()
                        if tmp_res:
                            for key in tmp_res.keys():
                                cn_ring[key] = str(tmp_res[key]).strip()
                        ringinfo['container'] = cn_ring
                    if os.path.exists('/etc/swift/object.builder'):
                        res_ob = util.excute_command("swift-ring-builder object.builder |sed -n '2p'")
                        ob_parser = reg_templates.RingParser(res_ob)
                        tmp_res = ob_parser.parse()
                        if tmp_res:
                            for key in tmp_res.keys():
                                ob_ring[key] = str(tmp_res[key]).strip()
                        ringinfo['object'] = ob_ring
            if ringinfo:
                return json.dumps(ringinfo,ensure_ascii=True,encoding='utf-8')
            else:
                return None
        except Exception as ex:
            logger.exception("get_cluster_ring_info function excute exception:" + str(ex))

class NodeStat(object):
    '''
    主机运行中各种运行状态数据采集类
    '''
    def __init__(self):
        pass

    def get_sys_stat_info(self):
        '''
        获取主机的运行状态数据，主要来源于top命令
        :return:
        '''
        try:
            rec = {}
            data = util.excute_command('top -bi -n 2 -d 0.02')  # 由于取第一次top命令结果不准确，故取第二次，过滤掉第一次的结果
            parser = reg_templates.OsStat(data)
            rec = parser.parse()
            # 修正memory数据
            result = psutil.virtual_memory()
            rec['mem_total'] = str(result.total)
            rec['mem_free'] = str(result.free)
            rec['mem_used'] = str(result.used)
            rec['mem_buffers'] = str(result.buffers)
            sres = psutil.swap_memory()
            rec['swap_total'] = str(sres.total)
            rec['swap_free'] = str(sres.free)
            rec['swap_used'] = str(sres.used)
            rec['swap_cached'] = str(result.cached)
            osres = psutil.users()
            rec['host_login_users'] = len(osres)
            osruntime = psutil.boot_time()
            rec['host_runtime'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(osruntime))
            return rec
        except Exception as ex:
            logger.exception("get_sys_stat_info function excute exception:" + str(ex))

    def get_net_stat_info(self):
        '''
        获取主机每块网卡的运行数据，以字典形式返回
        :return:
        '''
        try:
            nicinfo = {}
            #res = psutil.net_io_counters(pernic=True)  # 获取每张网卡的状态数据
            res = util.net_io_counters()
            result = util.excute_command('ip a')
            parser = reg_templates.EthernetParser(result)
            rec = parser.parse()
            nets = rec['net'].split(',')
            packsent = {}
            packrecv = {}
            bytesent = {}
            byterecv = {}
            errin = {}
            errout = {}
            dropin = {}
            dropout = {}
            netused = {}
            for net in nets:
                if net :
                    tmpkey = str(net).strip()
                    if res.has_key(tmpkey):
                        bytesent[tmpkey] = str(res[tmpkey][0])
                        byterecv[tmpkey] = str(res[tmpkey][1])
                        packsent[tmpkey] = str(res[tmpkey][2])
                        packrecv[tmpkey] = str(res[tmpkey][3])

                        errin[tmpkey] = str(res[tmpkey][4])
                        errout[tmpkey] = str(res[tmpkey][5])
                        dropin[tmpkey] = str(res[tmpkey][6])
                        dropout[tmpkey] = str(res[tmpkey][7])

            nicinfo['net_uesd'] = json.dumps(netused, encoding="UTF-8", ensure_ascii=True)
            nicinfo['net_send_packages'] = json.dumps(packsent, encoding="UTF-8", ensure_ascii=True)
            nicinfo['net_recv_packages'] = json.dumps(packrecv, encoding="UTF-8", ensure_ascii=True)
            nicinfo['net_send_bytes'] = json.dumps(bytesent, encoding="UTF-8", ensure_ascii=True)
            nicinfo['net_recv_bytes'] = json.dumps(byterecv, encoding="UTF-8", ensure_ascii=True)
            nicinfo['net_in_err'] = json.dumps(errin, encoding="UTF-8", ensure_ascii=True)
            nicinfo['net_out_err'] = json.dumps(errout, encoding="UTF-8", ensure_ascii=True)
            nicinfo['net_in_drop'] = json.dumps(dropin, encoding="UTF-8", ensure_ascii=True)
            nicinfo['net_out_drop'] = json.dumps(dropout, encoding="UTF-8", ensure_ascii=True)

            return nicinfo
        except Exception as ex:
            logger.exception("get_net_stat_info function excute exception:" + str(ex))

    def get_disk_stat_info(self):
        '''
        返回磁盘的使用数据，以列表形式返回
        :return:
        '''
        try:
            host = HostInfo()
            hostdisks = []
            disks = host.get_disk_names()
            if disks:
                dn = util.excute_command("ls /dev/|grep sd").split('\n')
                iores = psutil.disk_io_counters(perdisk=True)
                partres = psutil.disk_partitions()
                for disk in dn:
                    diskinfo = {}
                    dsk = str(disk).strip()
                    ds = '/dev/' + dsk
                    tmpds = util.excute_command('blkid ' + ds)
                    if not tmpds or 'UUID=' not in tmpds:
                        continue
                    tmppar = reg_templates.DiskUuidParser(tmpds)
                    tmprec = tmppar.parse()
                    if tmprec.has_key('disk_uuid'):
                        diskinfo['disk_uuid'] = tmprec['disk_uuid']
                    else:
                        diskinfo['disk_uuid'] = 'N/A'
                    diskinfo['disk_name'] = dsk
                    mpath = '/'
                    for dev in partres:
                        if dev.device == ds:
                            mpath = dev.mountpoint
                    #unmounted disks all value is 0
                    tmpres = psutil.disk_usage(mpath)
                    if tmpres:
                        if '/srv/node' not in str(mpath).lower():
                            diskinfo['disk_total'] = 0
                        else:
                            diskinfo['disk_total'] = str(tmpres.total)
                        diskinfo['disk_used'] = str(tmpres.used)
                        diskinfo['disk_free'] = str(tmpres.free)
                        diskinfo['disk_percent'] = tmpres.percent
                    else:
                        diskinfo['disk_total'] = 0
                        diskinfo['disk_used'] = 0
                        diskinfo['disk_free'] = 0
                        diskinfo['disk_percent'] = 0
                    if iores and iores.has_key(dsk):
                        diskinfo['read_count'] = str(iores[dsk].read_count)
                        diskinfo['write_count'] = str(iores[dsk].write_count)
                        diskinfo['read_bytes'] = str(iores[dsk].read_bytes)
                        diskinfo['write_bytes'] = str(iores[dsk].write_bytes)
                        diskinfo['read_time'] = str(iores[dsk].read_time)
                        diskinfo['write_time'] = str(iores[dsk].write_time)
                        diskinfo['read_merged_count'] = str(iores[dsk].read_merged_count)
                        diskinfo['write_merged_count'] = str(iores[dsk].write_merged_count)
                        diskinfo['busy_time'] = iores[dsk].busy_time
                    else:
                        diskinfo['read_count'] = 0
                        diskinfo['write_count'] = 0
                        diskinfo['read_bytes'] = 0
                        diskinfo['write_bytes'] = 0
                        diskinfo['read_time'] = 0
                        diskinfo['write_time'] = 0
                        diskinfo['read_merged_count'] = 0
                        diskinfo['write_merged_count'] = 0
                        diskinfo['busy_time'] = 0
                    diskinfo['guid'] = str(uuid.uuid1())
                    diskinfo['data_model'] = 'SfoDiskPerform'
                    diskinfo['host_name'] = socket.getfqdn()
                    diskinfo['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    hostdisks.append(diskinfo)
            return hostdisks
        except Exception as ex:
            logger.exception("get_disk_stat_info function excute exception:" + str(ex))

    def get_cpu_freq_info(self):
        '''
        获取CPU每个核的频率并json化返回
        :return:
        '''
        res = {}
        try:
            data = util.excute_command('ls -l /sys/devices/system/cpu/')
            if data:
                parser = reg_templates.CpuName(data)
                rec = parser.parse()
                if rec and isinstance(rec,dict):
                    if rec.has_key('cpu_id'):
                        cpuids = str(rec['cpu_id']).split(',')
                        for ci in cpuids:
                            if os.path.exists('/sys/devices/system/cpu/'+ str(ci).strip() +'/cpufreq/cpuinfo_cur_freq'):
                                result = util.excute_command(r'cat /sys/devices/system/cpu/'+ str(ci).strip() +'/cpufreq/cpuinfo_cur_freq')
                                if str(result).isdigit():
                                    res[str(ci).strip()] = float(result)/1000000
                                else:
                                    res[str(ci).strip()] = 'N/A'
                            else:
                                res[str(ci).strip()] = 'N/A'
            return json.dumps(res, encoding="UTF-8", ensure_ascii=True)
        except Exception as ex:
            logger.exception("get_cpu_freq_info function excute exception:" + str(ex))

class InfoAcquisition(object):
    '''
    数据采集发送类
    '''
    def __init__(self):
        pass

    def get_host_json(self):
        '''
        采集主机的各种硬件信息：操作系统、BIOS、CPU、内存、网卡和磁盘的硬件相关信息
        :return:数据入kafka
        '''
        hostinfo = HostInfo()
        kfk = ProduceKafkaInfo()
        try:
            host = {}
            host['guid'] = str(uuid.uuid1())
            host['data_model'] = 'SfoHostInfo'
            osinfo = hostinfo.get_os_info()
            if osinfo and isinstance(osinfo,dict):
                for key in osinfo.keys():
                    host[key] = osinfo[key]
            mfinfo = hostinfo.get_bios_dev_info()
            if mfinfo and isinstance(mfinfo,dict):
                for key in mfinfo.keys():
                    host[key] = mfinfo[key]
            cpuinfo = hostinfo.get_cpu_dev_info()
            if cpuinfo[0] and isinstance(cpuinfo[0],dict):
                for key in cpuinfo[0].keys():
                    host[key] = cpuinfo[0][key]
            nicinfo = hostinfo.get_net_dev_info()
            if nicinfo and isinstance(nicinfo,dict):
                for key in nicinfo.keys():
                    host[key] = nicinfo[key]
            diskinfo = hostinfo.get_disk_dev_info()
            if diskinfo and isinstance(diskinfo,dict):
                for key in diskinfo.keys():
                    host[key] = diskinfo[key]

            host['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            data = json.dumps(host, encoding="UTF-8", ensure_ascii=True)
            if data:
                kfk.produce_kafka_info(config.kafka_sys_topic, data)
        except Exception as ex:
            logger.exception("get_host_json function excute exception:" + str(ex))

    def get_node_json(self, model):
        '''
        将系统运行的性能数据、主机网卡性能数据收集并存入kafka中
        :param model: 传入数据model名
        :return: 数据入kafka
        '''
        nodestat = NodeStat()
        kfk = ProduceKafkaInfo()
        node = {}
        try:
            node['guid'] = str(uuid.uuid1())
            node['data_model'] = model
            node['host_name'] = socket.getfqdn()
            nodesysinfo = nodestat.get_sys_stat_info()
            if nodesysinfo and isinstance(nodesysinfo,dict):
                for key in nodesysinfo.keys():
                    node[key] = nodesysinfo[key]
            nodenetinfo = nodestat.get_net_stat_info()
            if nodenetinfo and isinstance(nodenetinfo,dict):
                for key in nodenetinfo.keys():
                    node[key] = nodenetinfo[key]

            node['cpu_core_used'] = psutil.cpu_percent(interval=1, percpu=True)
            cpu_freq = nodestat.get_cpu_freq_info()
            if util.is_json(cpu_freq):
                node['cpu_core_frq'] = cpu_freq
            else:
                node['cpu_core_frq'] = json.dumps(cpu_freq, encoding="UTF-8", ensure_ascii=True)
            node['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            data = json.dumps(node, encoding="UTF-8", ensure_ascii=True)
            if data:
                kfk.produce_kafka_info(config.kafka_sys_topic, data)
        except Exception as ex:
            logger.exception("get_node_json function excute exception:" + str(ex))

    def get_node_disk_stat_json(self):
        '''
        将节点的磁盘信息和性能数据json化后生产入kafka
        :return: 数据入kafka
        '''
        kfk = ProduceKafkaInfo()
        try:
            node = NodeStat()
            res = node.get_disk_stat_info()
            if res:
                data = json.dumps(res, encoding="UTF-8", ensure_ascii=True)
                kfk.produce_kafka_info(config.kafka_sys_topic, data)
        except Exception as ex:
            logger.exception("get_node_disk_stat_json function excute exception:" + str(ex))

    def get_ring_json(self):
        '''
        获取主机上主要文件的md5值
        :return: 数据入kafka
        '''
        hostinfo = HostInfo()
        kfk = ProduceKafkaInfo()
        rings = hostinfo.get_rings()
        hostname = socket.getfqdn()
        ip = socket.gethostbyname(hostname)
        ring = {}
        ring_ins = {}
        extend = {}
        try:
            for ring_name in rings:
                ring_md5 = hostinfo.get_ring_file_md5(ring_name)
                ring_ins.update({ring_name: ring_md5})
            ring['guid'] = str(uuid.uuid1())
            ring['data_model'] = 'SfoHostRing'
            ring['rings_md5'] = json.dumps(ring_ins,encoding="UTF-8", ensure_ascii=True)
            ring['host_name'] = hostname
            ring['ip_addr'] = ip
            ring['ring_info'] = hostinfo.get_cluster_ring_info()
            if os.path.exists("/etc/swift/passwd"):
                extend['passwdmd5'] = util.excute_command("md5sum /etc/swift/passwd |awk '{print $1}'")
            if os.path.exists("/etc/swift/object-server/object-rep-server.conf"):
                extend['object-rep-server.conf'] = util.excute_command("md5sum /etc/swift/object-server/object-rep-server.conf |awk '{print $1}'")
            if os.path.exists("/etc/swift/object-server/object-server.conf"):
                extend['object-server.conf'] = util.excute_command("md5sum /etc/swift/object-server/object-server.conf |awk '{print $1}'")
            if os.path.exists("/etc/swift/account-server/account-rep-server.conf"):
                extend['account-rep-server.conf'] = util.excute_command("md5sum /etc/swift/account-server/account-rep-server.conf |awk '{print $1}'")
            if os.path.exists("/etc/swift/account-server/account-server.conf"):
                extend['account-server.conf'] = util.excute_command("md5sum /etc/swift/account-server/account-server.conf |awk '{print $1}'")
            if os.path.exists("/etc/swift/container-server/container-rep-server.conf"):
                extend['container-rep-server.conf'] = util.excute_command("md5sum /etc/swift/container-server/container-rep-server.conf |awk '{print $1}'")
            if os.path.exists("/etc/swift/container-server/container-rep-server.conf"):
                extend['container-server.conf'] = util.excute_command("md5sum /etc/swift/container-server/container-server.conf |awk '{print $1}'")
            if os.path.exists("/etc/swift/proxy-server.conf"):
                extend['proxy-server.conf'] = util.excute_command("md5sum /etc/swift/proxy-server.conf |awk '{print $1}'")

            ring['extend'] = json.dumps(extend, encoding="UTF-8", ensure_ascii=True)
            ring['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            data = json.dumps(ring, encoding="UTF-8", ensure_ascii=True)
            if data:
                kfk.produce_kafka_info(config.kafka_sys_topic, data)
        except Exception, ex:
            logger.exception("get_ring_json function excute exception:" + str(ex))

    def get_host_monitor_json(self):
        '''
        获取监控数据
        同时产生主机的CPU、内存、网络和磁盘使用率告警信息
        :return: 数据入kafka
        '''
        pri = ProduceKafkaInfo()
        try:
            data = {}
            netstatinfo = {}
            netuseinfo = {}
            fileinfo = {}
            filerwinfo = {}
            data['guid'] = str(uuid.uuid1())
            data['data_model'] = 'SfoHostMonitor'
            data['cluster_name'] = config.swift_cluster_name
            data['host_name'] = socket.getfqdn()
            #cpu used rate
            cpurate = psutil.cpu_percent(interval=1, percpu=False)
            data['host_cpu_rate'] = cpurate
            if float(cpurate) - 60.0 > 0:
                alarmdata = {}
                alarmdata['guid'] = str(uuid.uuid1())
                alarmdata['data_model'] = 'SfoAlarmLog'
                alarmdata['alarm_device'] = "cpu-rate-{}".format(str(data['host_name']))
                alarmdata['alarm_type'] = "hardware"
                alarmdata['hostname'] = data['host_name']
                alarmdata['device_name'] = 'CPU-USED'
                if float(cpurate) - 80.0 > 0:
                    alarmdata['alarm_message'] = 'host cpu has used {}%,it`s more than 80 percent'.format("%.2f"%cpurate)
                    alarmdata['alarm_level'] = 'critical'
                else:
                    alarmdata['alarm_message'] = 'host cpu has used {}%,it`s more than 60 percent'.format("%.2f"%cpurate)
                    alarmdata['alarm_level'] = 'warning'
                alarmdata['alarm_result'] = '0'
                alarmdata['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                alert = json.dumps(alarmdata,encoding='utf-8',ensure_ascii=True)
                if alert:
                    pri.produce_kafka_info(config.kafka_sys_topic,alert)
            #memery used rate
            memrate = psutil.virtual_memory()
            data['host_mem_rate'] = memrate.percent
            if float(memrate.percent) - 60.0 > 0:
                alarmdata = {}
                alarmdata['guid'] = str(uuid.uuid1())
                alarmdata['data_model'] = 'SfoAlarmLog'
                alarmdata['alarm_device'] = "memory-rate-{}".format(str(data['host_name']))
                alarmdata['alarm_type'] = "hardware"
                alarmdata['hostname'] = data['host_name']
                alarmdata['device_name'] = 'MEM-USED'
                if float(memrate.percent) - 90.0 > 0:
                    alarmdata['alarm_message'] = 'host memory has used {}%,it`s more than 90 percent'.format("%.2f"%memrate.percent)
                    alarmdata['alarm_level'] = 'critical'
                else:
                    alarmdata['alarm_message'] = 'host memory has used {}%,it`s more than 60 percent'.format("%.2f"%memrate.percent)
                    alarmdata['alarm_level'] = 'warning'
                alarmdata['alarm_result'] = '0'
                alarmdata['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                alert = json.dumps(alarmdata,encoding='utf-8',ensure_ascii=True)
                if alert:
                    pri.produce_kafka_info(config.kafka_sys_topic, alert)
            #net stat and used  info
            netstat = psutil.net_if_stats()
            netuse1 = psutil.net_io_counters(pernic=True)
            time.sleep(1)
            netuse2 = psutil.net_io_counters(pernic=True)
            for key in netstat.keys():
                if 'eth' in str(key).lower() or 'bond' in str(key).lower():
                    if str(netstat[key].isup).upper() == 'TRUE':
                        netstatinfo[key] = 'OK'
                        netspeed = netstat[key].speed
                        if netspeed > 0:
                            #byte -> Mb     1048576 = 1024 * 1024
                            sent = (float(netuse2[key].bytes_sent) - float(netuse1[key].bytes_sent))*8/1048576/float(netspeed)
                            recv = (float(netuse2[key].bytes_recv) - float(netuse1[key].bytes_recv))*8/1048576/float(netspeed)
                            if sent - recv > 0:
                                netuseinfo[key] = round(sent,4)
                            else:
                                netuseinfo[key] = round(recv,4)

                            if float(netuseinfo[key]) - 0.3 > 0:
                                alarmdata = {}
                                alarmdata['guid'] = str(uuid.uuid1())
                                alarmdata['data_model'] = 'SfoAlarmLog'
                                alarmdata['alarm_device'] = "{}-rate-{}".format(str(key),str(data['host_name']))
                                alarmdata['alarm_type'] = "hardware"
                                alarmdata['hostname'] = data['host_name']
                                alarmdata['device_name'] = 'NET-USED'
                                if float(netuseinfo[key]) - 0.4 > 0:
                                    alarmdata['alarm_message'] = 'network card traffic has used {}%,it`s more than 40 percent'.format("%.2f"%(float(netuseinfo[key])*100))
                                    alarmdata['alarm_level'] = 'critical'
                                else:
                                    alarmdata['alarm_message'] = 'network card traffic has used {}%,it`s more than 30 percent'.format("%.2f"%(float(netuseinfo[key])*100))
                                    alarmdata['alarm_level'] = 'warning'
                                alarmdata['alarm_result'] = '0'
                                alarmdata['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                                alert = json.dumps(alarmdata, encoding='utf-8', ensure_ascii=True)
                                if alert:
                                    pri.produce_kafka_info(config.kafka_sys_topic, alert)

                        else:
                            netuseinfo[key] = 0.0
                    else:
                        netstatinfo[key] = 'DOWN'
            data['host_net_rate'] = json.dumps(netuseinfo, encoding="UTF-8", ensure_ascii=True)
            data['host_net_stat'] = json.dumps(netstatinfo, encoding="UTF-8", ensure_ascii=True)
            #disk stat
            data['host_disk_stat'] = ''
            #file system info
            disks = psutil.disk_partitions()
            for disk in disks:
                disk_usage = psutil.disk_usage(disk.mountpoint)
                fileinfo[disk.mountpoint] = disk_usage.percent
                if float(disk_usage.percent) - 70.0 > 0:
                    alarmdata = {}
                    alarmdata['guid'] = str(uuid.uuid1())
                    alarmdata['data_model'] = 'SfoAlarmLog'
                    alarmdata['alarm_device'] = "{}-file-rate-{}".format(str(disk.mountpoint), str(data['host_name']))
                    alarmdata['alarm_type'] = "hardware"
                    alarmdata['hostname'] = data['host_name']
                    alarmdata['device_name'] = 'FILE-USED'
                    if float(disk_usage.percent) - 80.0 > 0:
                        alarmdata['alarm_message'] = 'the file system capacity has used {}%,it`s more than 80 percent'.format("%.2f"%disk_usage.percent)
                        alarmdata['alarm_level'] = 'critical'
                    else:
                        alarmdata['alarm_message'] = 'the file system capacity has used {}%,it`s more than 70 percent'.format("%.2f"%disk_usage.percent)
                        alarmdata['alarm_level'] = 'warning'
                    alarmdata['alarm_result'] = '0'
                    alarmdata['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    alert = json.dumps(alarmdata, encoding='utf-8', ensure_ascii=True)
                    if alert:
                        pri.produce_kafka_info(config.kafka_sys_topic, alert)
                filecmd = "touch {}".format(str(disk.mountpoint+'/sfo_test.txt'))
                if util.excute_command(filecmd) == "SUCCESS":
                    filerwinfo[disk.mountpoint] = 'OK'
                else:
                    unwrited = False
                    for retry in range(4):
                        if util.excute_command(filecmd) == "SUCCESS":
                            filerwinfo[disk.mountpoint] = 'OK'
                            unwrited = False
                            break
                        else:
                            unwrited = True
                            time.sleep(1)
                    if unwrited:
                        filerwinfo[disk.mountpoint] = 'ERROR'
                        alarmdata = {}
                        alarmdata['guid'] = str(uuid.uuid1())
                        alarmdata['data_model'] = 'SfoAlarmLog'
                        alarmdata['alarm_device'] = "{}-file-write-{}".format(str(disk.mountpoint), str(data['host_name']))
                        alarmdata['alarm_type'] = "hardware"
                        alarmdata['hostname'] = data['host_name']
                        alarmdata['device_name'] = 'FILE-WRITE'
                        alarmdata['alarm_message'] = 'the file system {} can not write success'.format(str(disk.mountpoint))
                        alarmdata['alarm_level'] = 'critical'
                        alarmdata['alarm_result'] = '0'
                        alarmdata['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        alert = json.dumps(alarmdata, encoding='utf-8', ensure_ascii=True)
                        if alert:
                            pri.produce_kafka_info(config.kafka_sys_topic, alert)
            data['host_file_rate'] = json.dumps(fileinfo, encoding="UTF-8", ensure_ascii=True)
            data['host_rw_file'] = json.dumps(filerwinfo, encoding="UTF-8", ensure_ascii=True)
            #ntp time
            data['host_ntp_time'] = 101.1
            #extend
            extend = {}
            #ntpd.service
            extend['ntpd'] = util.excute_command("systemctl status ntpd.service|grep -w 'Active'|awk 'match($0,/Active:.*\((.*)\)/,a) {print a[1]}'")
            if 'running' != str(extend['ntpd']).strip().lower():
                alarmdata = {}
                alarmdata['guid'] = str(uuid.uuid1())
                alarmdata['data_model'] = 'SfoAlarmLog'
                alarmdata['alarm_device'] = "ntpd-service-{}".format(str(data['host_name']))
                alarmdata['alarm_type'] = "software"
                alarmdata['hostname'] = data['host_name']
                alarmdata['device_name'] = 'NTP Service'
                alarmdata['alarm_message'] = 'the host ntpd service is not running'
                alarmdata['alarm_level'] = 'critical'
                alarmdata['alarm_result'] = '0'
                alarmdata['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                alert = json.dumps(alarmdata, encoding='utf-8', ensure_ascii=True)
                if alert:
                    pri.produce_kafka_info(config.kafka_sys_topic, alert)
            else:
                data['host_ntp_time'] = util.excute_command("ntpq -p |sed -n '3p'|awk '{print $9}'")
            # ntp time alarm
            if type(eval(str(data['host_ntp_time']))) == float:
                if abs(float(data['host_ntp_time'])) - 100.0 > 0:
                    alarmdata = {}
                    alarmdata['guid'] = str(uuid.uuid1())
                    alarmdata['data_model'] = 'SfoAlarmLog'
                    alarmdata['alarm_device'] = "time-offset-{}".format(str(data['host_name']))
                    alarmdata['alarm_type'] = "software"
                    alarmdata['hostname'] = data['host_name']
                    alarmdata['device_name'] = 'Time Offset'
                    alarmdata['alarm_message'] = 'the host time offset was {},it`s off ntp server more than 100 ms'.format("%.2f" % abs(float(data['host_ntp_time'])))
                    alarmdata['alarm_level'] = 'critical'
                    alarmdata['alarm_result'] = '0'
                    alarmdata['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    alert = json.dumps(alarmdata, encoding='utf-8', ensure_ascii=True)
                    if alert:
                        pri.produce_kafka_info(config.kafka_sys_topic, alert)
            #memcached
            extend['memcached'] = util.excute_command("systemctl status memcached |grep -w 'Active'|awk 'match($0,/Active:.*\((.*)\)/,a) {print a[1]}'")
            #rsyncd
            extend['rsyncd'] = util.excute_command("systemctl status rsyncd.service|grep -w 'Active'|awk 'match($0,/Active:.*\((.*)\)/,a) {print a[1]}'")
            data['extend'] = json.dumps(extend, encoding="UTF-8", ensure_ascii=True)
            data['add_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            data = json.dumps(data, encoding="UTF-8", ensure_ascii=True)
            if data:
                pri.produce_kafka_info(config.kafka_sys_topic, data)
        except Exception as ex:
            logger.exception("get_host_monitor_json function excute exception:" + str(ex))

