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
import subprocess
import time
import datetime
import argparse
import traceback
import logging
import json
import hashlib
import math
import copy
import tempfile
from threading import Thread
from sfo_common.config_parser import Config
from dateutil.parser import parse
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex
from ast import literal_eval

logger = logging.getLogger("agent")
config = Config()


class Util(object):
    def __init__(self):
        self.UTC_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
        self.LOCAL_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
        self.index = 624
        self.MT = [0] * 624

    def ensure_dir(self, pathname):
        '''
        确保目录存在
        判断目录是否存在，不存在则创建
        :param pathname:
        :return:
        '''
        dirname = os.path.dirname(pathname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

    def parse_cmdargs(self, module, description):
        '''
        参数拆解
        :param module:
        :param description:
        :return:
        '''
        ap = argparse.ArgumentParser(description=description, add_help=True)
        ap.add_argument('start', action="", help="start {}".format(module))

    def get_ipaddr(self, param):  # HOST / NODE
        '''
        获取主机的ip地址，当存在多个ip地址时需要根据配置前缀进行过滤
        :param param:
        :return:
        '''
        output = ''
        try:
            if 'HOST' == str(param).upper():
                cmdstr = "ip addr show|grep inet|awk '{print $2}'|awk -F'/' '{print $1}'|egrep '" + config.host_ip_prefix + "'|head -1"
                output = self.excute_cmd_os_unit(cmdstr)
            if 'NODE' == str(param).upper():
                cmdstr = "ip addr show|grep inet|awk '{print $2}'|awk -F'/' '{print $1}'|egrep '" + config.node_ip_prefix + "'|head -1"
                output = self.excute_cmd_os_unit(cmdstr)
        except Exception as ex:
            output = str(ex)
        return output

    def excute_command(self, cmdstr):
        '''
        执行linux命令
        :param cmdstr:
        :return:
        '''
        return self.excute_cmd_os_unit(cmdstr)

    def excute_cmd_2file(self,cmd,timeout=30):
        '''
        使用临时文件方式执行linux命令
        :param cmd:
        :param timeout:
        :return:
        '''
        try:
            start = datetime.datetime.now()
            # 得到一个临时文件对象， 调用close后，此文件从磁盘删除
            out_temp = tempfile.TemporaryFile(mode='w+')
            # 获取临时文件的文件号
            fileno = out_temp.fileno()
            # 执行外部shell命令， 输出结果存入临时文件中
            process = subprocess.Popen(cmd, shell=True, stdout=fileno, stderr=fileno,close_fds=True)
            # 检查子进程是否结束
            while process.poll() is None:
                time.sleep(0.1)
                now = datetime.datetime.now()
                if (now - start).seconds > timeout:
                    try:
                        process.terminate()
                    except Exception as e:
                        raise e
            process.communicate()
            # 从临时文件读出shell命令的输出结果
            out_temp.seek(0)
            result = out_temp.read().strip()
            if not result:
                if process.returncode == 0:
                    result = 'SUCCESS'
                else:
                    result = 'Operation failed'
        except Exception as ex:
            logger.info("excute_cmd_2file function excute exception:" + str(ex) + traceback.format_exc())
        finally:
            if process.stdin:
                process.stdin.close()
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
            try:
                process.kill()
            except OSError:
                pass
            if out_temp:
                out_temp.close()
            return result

    def excute_cmd_os_unit(self,cmd):
        '''
        使用os模块执行linux命令
        :param cmd:
        :return:
        '''
        try:
            finfo = os.popen(cmd).read()
            if not finfo:
                res = os.system(cmd)
                if res == 0 or res == 256:
                    return 'SUCCESS'
                else:
                    return 'Operation failed'
            else:
                return finfo
        except Exception as ex:
            logger.info("excute_cmd_os_unit function excute exception:" + str(ex))

    def exct_cmd(self, cmdstr):
        '''
        执行命令返回结果为列表
        :param cmdstr:
        :return:
        '''
        try:
            rec = os.popen(cmdstr).readlines()
            if not rec:
                res = os.system(cmdstr)
                if res == 0:
                    return ['SUCCESS']
                else:
                    return ['Operation failed']
            else:
                return rec
        except OSError as err:
            logger.error("os.popen excute error:%s,the cmd is %s"%(err,cmdstr))
        except Exception as ex:
            logger.exception("excute_cmd_os_unit function excute exception:" + str(ex))

    def check_ip_alive(self,ip):
        '''
        判断ip地址是否可连通
        :param ip:
        :return:
        '''
        result = False
        try:
            cmd = "ping -c 2 {} |sed -n '6p'".format(ip)
            res = self.excute_cmd_2file(cmd,10)
            if "2 received" in res.lower() and "0% packet loss" in res.lower():
                result = True
        except Exception as ex:
            logger.info("check_ip_alive function excute exception:" + str(ex))
        finally:
            return result

    def is_json(self, tag):
        '''
        判断目标对象是否是json
        :param tag:
        :return:
        '''
        result = False
        try:
            res = json.loads(tag)
            if res:
                result = True
        except ValueError:
            result = False
        finally:
            return result

    # return timemin to timemax seconds
    def datediff_seconds(self, timemin, timemax):
        '''
        判断两个时间之间的时间差，单位为秒
        :param timemin:
        :param timemax:
        :return:
        '''
        try:
            time_a = parse(timemax)
            time_b = parse(timemin)
            return (time_a - time_b).total_seconds()
        except Exception as ex:
            raise RuntimeError(str(ex))

    #
    def sha1_encode(self, param):
        '''
        字符编码
        :param param:
        :return:
        '''
        sha1 = hashlib.sha1()
        sha1.update(param.encode('utf-8'))
        return sha1.hexdigest()

    def net_io_counters(self):
        '''
        收集网卡运行数据
        :return:
        '''
        rec = {}
        try:
            lines = self.exct_cmd("cat /proc/net/dev")
            for line in lines[2:]:
                colon = line.rfind(':')
                assert colon > 0, repr(line)
                name = line[:colon].strip()
                fields = line[colon + 1:].strip().split()
                # in
                (bytes_recv,
                 packets_recv,
                 errin,
                 dropin,
                 fifoin,  # unused
                 framein,  # unused
                 compressedin,  # unused
                 multicastin,  # unused
                 # out
                 bytes_sent,
                 packets_sent,
                 errout,
                 dropout,
                 fifoout,  # unused
                 collisionsout,  # unused
                 carrierout,  # unused
                 compressedout) = map(str, fields)
                rec[name] = (bytes_sent, bytes_recv, packets_sent, packets_recv, errin, errout, dropin, dropout)
            return rec
        except Exception as ex:
            logger.info("net_io_counters function excute exception:" + str(ex))

    def unit_conversion(self, value, target_unit=None):
        '''
        target_unit can be  B   KB  MB  GB  TB  PB  EB
        :param value:
        :param target_unit:
        :return:
        '''
        result = 0.0
        try:
            if type(eval(str(value))) == float or type(eval(str(value))) == int or type(eval(str(value))) == long:
                if target_unit:
                    if str(target_unit).strip().upper() == "B":
                        result = value
                    elif str(target_unit).strip().upper() == "KB":
                        result = float(value) / 1024.0
                    elif str(target_unit).strip().upper() == "MB":
                        result = float(value) / 1024.0 / 1024.0
                    elif str(target_unit).strip().upper() == "GB":
                        result = float(value) / 1024.0 / 1024.0 / 1024.0
                    elif str(target_unit).strip().upper() == "TB":
                        result = float(value) / 1024.0 / 1024.0 / 1024.0 / 1024.0
                    elif str(target_unit).strip().upper() == "PB":
                        result = float(value) / 1024.0 / 1024.0 / 1024.0 / 1024.0 / 1024.0
                    elif str(target_unit).strip().upper() == "EB":
                        result = float(value) / 1024.0 / 1024.0 / 1024.0 / 1024.0 / 1024.0 / 1024.0
                    else:
                        result = -2
                else:
                    if float(value) - 1024.0 > 0.0:
                        value = float(value) / 1024.0
                        if float(value) - 1024.0 > 0.0:
                            value = float(value) / 1024.0
                            if float(value) - 1024.0 > 0.0:
                                value = float(value) / 1024.0
                                if float(value) - 1024.0 > 0.0:
                                    value = float(value) / 1024.0
                                    if float(value) - 1024.0 > 0.0:
                                        value = float(value) / 1024.0
                                        if float(value) - 1024.0 > 0.0:
                                            value = float(value) / 1024.0
                                            target_unit = "EB"
                                            result = value
                                        else:
                                            target_unit = "PB"
                                            result = value
                                    else:
                                        target_unit = "TB"
                                        result = value
                                else:
                                    target_unit = "GB"
                                    result = value
                            else:
                                target_unit = "MB"
                                result = value
                        else:
                            target_unit = "KB"
                            result = value
                    else:
                        target_unit = "B"
                        result = value
            else:
                result = -1
        except Exception as ex:
            result = -3
            logger.info("value is {} ,unit_conversion function excute exception:{}".format(str(value), str(ex)))
        finally:
            return "%f %s" % (result, target_unit)

    def encrypt(self, text, key):
        '''
        根据给定的key对text加密
        :param text:
        :param key:
        :return:
        '''
        result = None
        try:
            BS = AES.block_size
            pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
            cipher = AES.new(key)
            ciphertext = cipher.encrypt(pad(text))  # aes加密
            result = b2a_hex(ciphertext)
        except Exception as ex:
            print len(key)
            print "EX:%s" % str(ex)
            logger.info("encrypt function excute exception:" + str(ex))
        finally:
            return result

    def decrypt(self, text, key):
        '''
        根据给定的key对text进行解密
        :param text:
        :param key:
        :return:
        '''
        result = None
        try:
            unpad = lambda s: s[0:-ord(s[-1])]
            cipher = AES.new(key)
            plain_text = a2b_hex(text)
            result = unpad(cipher.decrypt(plain_text))
        except Exception as ex:
            print len(key)
            print "EX:%s" % str(ex)
            logger.info("decrypt function excute exception:" + str(ex))
        finally:
            return result

    def utc2local(self, utc_time_str):
        """UTC时间转本地时间（+8:00）"""
        try:
            ary_utc = datetime.datetime.strptime(utc_time_str, self.UTC_FORMAT)
            now_stamp = time.time()
            local_time = datetime.datetime.fromtimestamp(now_stamp)
            utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
            offset = local_time - utc_time
            local_st = ary_utc + offset
            return local_st.strftime(self.LOCAL_FORMAT)
        except Exception as ex:
            # print "utc2local function excute exception:" + str(ex)
            logger.info("utc2local function excute exception:" + str(ex))

    def local2utc(self, local_time_str):
        """本地时间转UTC时间（-8:00）"""
        try:
            local_time = datetime.datetime.strptime(local_time_str, self.LOCAL_FORMAT)
            time_struct = time.mktime(local_time.timetuple())
            utc_st = datetime.datetime.utcfromtimestamp(time_struct)
            return utc_st.strftime(self.UTC_FORMAT)
        except Exception as ex:
            # print "local2utc function excute exception:" + str(ex)
            logger.info("local2utc function excute exception:" + str(ex))

    def cal_list_p95(self, ls):
        '''
        计算列表的p95值
        :param ls:
        :return:
        '''
        result = 0
        try:
            if ls and len(ls) == 1:
                result = ls[0]
            elif ls and isinstance(ls, list) and len(ls) > 1:
                for i in range(len(ls)):
                    if type(eval(str(ls[i]))) == float or type(eval(str(ls[i]))) == int:
                        ls[i] = float(ls[i])
                    else:
                        ls[i] = 0
                ls.sort()
                p95 = len(ls) * 0.95
                min_index = int(math.floor(p95))
                min_weight = p95 - min_index
                max_index = int(math.ceil(p95))
                max_weight = max_index - p95
                if ls[min_index - 1] and ls[max_index - 1] and str(ls[min_index - 1]).strip() != 'None' and str(
                        ls[max_index - 1]).strip() != 'None':
                    if (type(eval(str(ls[min_index - 1]).strip())) == float or type(
                            eval(str(ls[min_index - 1]).strip())) == int) and (
                                    type(eval(str(ls[max_index - 1]).strip())) == float or type(
                                eval(str(ls[max_index - 1]).strip())) == int):
                        result = '%.2f' % (float(str(ls[min_index - 1]).strip()) * min_weight + float(
                            str(ls[max_index - 1]).strip()) * max_weight)
                    elif (type(eval(str(ls[min_index - 1]).strip())) == float or type(
                            eval(str(ls[min_index - 1]).strip())) == int):
                        result = '%.2f' % ls[min_index - 1]
                    elif (type(eval(str(ls[max_index - 1]).strip())) == float or type(
                            eval(str(ls[max_index - 1]).strip())) == int):
                        result = '%.2f' % ls[max_index - 1]
                    else:
                        result = '%.2f' % 0.0
                elif ls[min_index - 1] and str(ls[min_index - 1]).strip() != 'None':
                    if (type(eval(str(ls[min_index - 1]).strip())) == float or type(
                            eval(str(ls[min_index - 1]).strip())) == int):
                        result = '%.2f' % float(ls[min_index - 1])
                    else:
                        result = '%.2f' % 0.0
                elif ls[max_index - 1] and str(ls[max_index - 1]).strip() != 'None':
                    if (type(eval(str(ls[max_index - 1]).strip())) == float or type(
                            eval(str(ls[max_index - 1]).strip())) == int):
                        result = '%.2f' % float(ls[max_index - 1])
                    else:
                        result = '%.2f' % 0.0
                else:
                    result = '%.2f' % 0.0
            else:
                pass
        except Exception as ex:
            logger.info("cal_list_p95 function excute exception:" + str(ex) + "; the ls is " + str(ls))
        finally:
            return result

    def cal_list_p95_for_list(self, ls):
        '''
        计算列表中元素为列表的p95值
        :param ls:
        :return:
        '''
        result = []
        try:
            if ls:
                if type(ls[0]) is list:
                    index_range = len(ls[0])
                elif type(ls[0]) is str and type(eval(ls[0])) == list:
                    index_range = len(literal_eval(ls[0]))
                else:
                    index_range = 0
                for i in range(index_range):
                    index_list = []
                    for obj_list in ls:
                        if type(eval(str(obj_list))) == list:
                            if type(obj_list) is str:
                                mlist = literal_eval(obj_list)
                            elif type(obj_list) is list:
                                mlist = obj_list
                            else:
                                mlist = []
                            if len(mlist) > i:
                                if mlist[i] != '' or mlist[i] != 'None':
                                    index_list.append(copy.deepcopy(str(mlist[i]).strip()))
                                else:
                                    index_list.append('0.00')
                            else:
                                index_list.append('0.00')
                    result.append(copy.deepcopy(self.cal_list_p95(index_list)))
                    del index_list[:]
        except Exception as ex:
            logger.info("cal_list_p95_for_list function excute exception:" + str(ex) + '; the list is %s' % ls)
        finally:
            return result

    def cal_list_p95_for_json(self, ls):
        '''
        计算json对象列表的每个属性的p95值
        :param ls:
        :return:
        '''
        result = {}
        try:
            if ls:
                if self.is_json(ls[0]):
                    targ = json.loads(ls[0], encoding='UTF-8')
                    if targ:
                        for key in targ.keys():
                            index_list = []
                            for obj in ls:
                                if self.is_json(obj):
                                    obj_ls = json.loads(obj, encoding='UTF-8')
                                    if obj_ls.has_key(key):
                                        index_list.append(copy.deepcopy(str(obj_ls[key]).strip()))
                                elif obj != '{}':
                                    obj_ls = eval(obj)
                                    if obj_ls.has_key(key):
                                        index_list.append(copy.deepcopy(str(obj_ls[key]).strip()))
                                else:
                                    pass
                            if index_list:
                                if type(eval(str(index_list[0]))) == dict:
                                    result[key] = self.cal_list_p95_for_json(index_list)
                                elif type(eval(str(index_list[0]))) == list:
                                    result[key] = self.cal_list_p95_for_list(index_list)
                                elif type(eval(str(index_list[0]))) == int or type(eval(str(index_list[0]))) == float:
                                    result[key] = self.cal_list_p95(index_list)
                                else:
                                    pass
                            else:
                                pass
                elif type(eval(str(ls[0]))) == dict:
                    targ = eval(ls[0])
                    if targ != {}:
                        for key in targ.keys():
                            index_list = []
                            for obj in ls:
                                if self.is_json(obj):
                                    obj_ls = json.loads(obj, encoding='UTF-8')
                                    if obj_ls.has_key(key):
                                        index_list.append(copy.deepcopy(str(obj_ls[key]).strip()))
                                elif obj != '{}':
                                    obj_ls = eval(obj)
                                    if obj_ls.has_key(key):
                                        index_list.append(copy.deepcopy(str(obj_ls[key]).strip()))
                                else:
                                    pass
                            if index_list:
                                if type(eval(str(index_list[0]))) == dict:
                                    result[key] = self.cal_list_p95_for_json(index_list)
                                elif type(eval(str(index_list[0]))) == list:
                                    result[key] = self.cal_list_p95_for_list(index_list)
                                elif type(eval(str(index_list[0]))) == int or type(eval(str(index_list[0]))) == float:
                                    result[key] = self.cal_list_p95(index_list)
                                else:
                                    pass
                            else:
                                pass
                else:
                    pass
        except Exception as ex:
            logger.exception("cal_list_p95_for_json function excute exception:" + str(ex) + '; the json is %s' % ls)
        finally:
            return result
            # return json.dumps(result,encoding='UTF-8',ensure_ascii=True)

    def inter(self,t):
        return (0xFFFFFFFF & t)  # 取最后32位->t

    def twister(self):
        for i in range(self.index):
            y = self.inter((self.MT[i] & 0x80000000) + (self.MT[(i + 1) % self.index] & 0x7fffffff))
            self.MT[i] = self.MT[(i + 397) % self.index] ^ y >> 1
            if y % 2 != 0:
                self.MT[i] = self.MT[i] ^ 0x9908b0df
        self.index = 0

    def exnum(self):
        if self.index >= 624:
            self.twister()
        y = self.MT[self.index]
        y = y ^ y >> 11
        y = y ^ y << 7 & 2636928640
        y = y ^ y << 15 & 4022730752
        y = y ^ y >> 18
        self.index = self.index + 1
        return self.inter(y)

    def mainset(self,seed):
        self.MT[0] = seed  # seed
        for i in range(1, self.index):
            self.MT[i] = self.inter(1812433253 * (self.MT[i - 1] ^ self.MT[i - 1] >> 30) + i)
        return self.exnum()

    def randomint(self,min_num,max_num):
        try:
            so = float(self.mainset(int(time.time()))) / (2 ** 32 - 1)
            rd = min_num + int((max_num - min_num) * so)
            return rd
        except Exception as ex:
            logger.exception("randomint function excute exception:" + str(ex))


class Repeater(Thread):
    # period in second
    def __init__(self, event, function, args=[], period=5.0):
        Thread.__init__(self)
        self.stopped = event
        self.period = period
        self.function = function
        self.args = args

    def run(self):
        while not self.stopped.wait(self.period):
            try:
                # call a function
                self.function(*self.args)
            except Exception as e:
                # try later
                logger.error("{}, did not worked : {}".format(self.function.__name__, e))
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback)
                pass
