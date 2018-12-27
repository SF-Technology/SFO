#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()
import copy
import gevent
import json
from gevent.pool import Pool
from flask import Flask
# from flask_cors import CORS
from flask_socketio import SocketIO, disconnect
from sfo_server.models import SfoAlarmLog, SfoManagerTaskLogMethod, SfoTasksListMethod
from sfo_server.alarm_module import compare_pre_and_cur_log, category_alarm_level
from sfo_common import db
from sfo_utils.socket_utils import LocalProcessSocketServer
import errno


app = Flask(__name__)
socketio = SocketIO(app, async_mode='gevent_uwsgi')
# socketio = SocketIO(app, async_mode='eventlet')
# CORS(app, resources=r'/*', supports_credentials=True)

thread = None
_pool = None
pre_alarm_logs = None
manager_log_dict = {}


def alarm_bk():
    global pre_alarm_logs
    while True:
        db.session.commit()
        gevent.sleep(5)
        sfo_alarm_logs = db.session.query(SfoAlarmLog).filter_by(alarm_result='0').all()
        if pre_alarm_logs is None:
            pre_alarm_logs = copy.deepcopy(sfo_alarm_logs)
            if sfo_alarm_logs:
                sum_alarm, alarm_dict = category_alarm_level(sfo_alarm_logs)
                socketio.emit('alarm_server',
                              {"data": {
                                  "alarm_total": sum_alarm,
                                  "alarm_detail": alarm_dict,
                              }},
                              namespace='/alarm')
        else:
            if compare_pre_and_cur_log(pre_alarm_logs, sfo_alarm_logs):
                continue
            else:
                pre_alarm_logs = copy.deepcopy(sfo_alarm_logs)
                sum_alarm, alarm_dict = category_alarm_level(sfo_alarm_logs)
                socketio.emit('alarm_server',
                              {"data": {
                                  "alarm_total": sum_alarm,
                                  "alarm_detail": alarm_dict,

                              }},
                              namespace='/alarm')


def install_cluster_percent(taskid, float_percent, status, install_info={}):
    db.session.commit()
    sfo_logs = SfoManagerTaskLogMethod.query_manager_log_by_taskid(taskid)
    cache_install_info = {}
    if sfo_logs:
        for log in sfo_logs:
            excute_desc = log.excute_description
            excute_message = log.excute_message
            cache_install_info[excute_desc] = excute_message
            for key in install_info.keys():
                cache_install_info.pop(key)
        if float_percent != float(1) and status == 200:
            socketio.emit("install_server",
                          {"data": {
                              "percent": str(float(float_percent) * 100) + '%',
                              "message": cache_install_info,
                              "status": status
                            }}
                          ,namespace='/cluster')
            for log in sfo_logs:
                excute_desc = log.excute_description
                excute_message = log.excute_message
                install_info[excute_desc] = excute_message
        else:
            socketio.emit("install_server",
                          {"data": {
                              "percent": str(float(float_percent) * 100) + '%',
                              "message": cache_install_info,
                              "status": status
                                }
                           }
                          , namespace='/cluster')


def socket_data_recv():
    local_soc_server = LocalProcessSocketServer(host='127.0.0.1', port=54444)
    conn, addr = local_soc_server.soc_server.accept()
    count = 0
    while count <= 30:
        try:
            data = conn.recv(1024)
            if data:
                data = json.loads(data)
                float_percent = data.get('float_percent')
                taskid = data.get('taskid')
                status = data.get('status')
                install_cluster_percent(taskid=taskid,
                                        float_percent=float_percent,
                                        status=status)
            else:
                count += 1
                gevent.sleep(1)
        except Exception, error:
            if error.errno == errno.EWOULDBLOCK:
                pass
            elif error.errno == errno.ECONNRESET:
                pass
            else:
                print error
    else:
        db.session.close()
        db.session.remove()
        conn.close()


@socketio.on('connect', namespace='/alarm')
def connect():
    global thread
    global pre_alarm_logs
    pre_alarm_logs = None
    _pool = Pool(1)
    _pool.apply_async(func=alarm_bk)


@socketio.on('disconnect', namespace='/alarm')
def socket_disconnect():
    disconnect(namespace='/alarm')


@socketio.on('connect', namespace='/cluster')
def install_cluster():
    _pool = Pool(1)
    _pool.apply_async(func=socket_data_recv)


@socketio.on('disconnect', namespace='/cluster')
def socket_disconnect():
    disconnect(namespace='/cluster')


if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5555)
    except Exception, error:
        pass