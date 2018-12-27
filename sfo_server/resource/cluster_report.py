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
import copy

from flask_restful import Resource, marshal_with, fields

from sfo_common.models import SfoCheckReport
from sfo_datahandler import db
from sfo_server import access_logger
from sfo_utils.utils import Util
from sfo_server.decorate import login_required, permission_required

util = Util()
# 输出字段的映射表
cluster_report_fields = {
    "status": fields.Integer,
    "message": fields.String,
    "data":fields.List(
        fields.Nested({
            "cluster_name":fields.String,
            "subject_name":fields.String,
            "item_name":fields.String,
            "check_command":fields.String,
            "check_result":fields.String,
            "check_remark":fields.String,
        })
    ),
}

def get_report_list():
    data = []
    status = ''
    message = ''
    resp = {"status": status, "data": data, "message": message}
    try:
        #yes_time = datetime.datetime.now() + datetime.timedelta(hours=-9)
        #yes_time_str = yes_time.strftime('%Y-%m-%d %H:%M:%S')
        #nowtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sql = "select * from (select * from sfo_check_report_data where add_time > date_add(now(), interval -9 hour))t group by cluster_name,item_name order by cluster_name,subject_name"
        check_list = db.session.query(SfoCheckReport).from_statement(sql)
        #check_list = SfoCheckReport.query.filter(and_(SfoCheckReport.add_time < nowtime,SfoCheckReport.add_time > yes_time_str)).order_by(SfoCheckReport.cluster_name.asc()).all()
        if not check_list:
            status=201
            message="No cluster in env"
        else:
            for check_item in check_list:
                item = {}
                item['cluster_name'] = check_item.cluster_name
                item['subject_name'] = check_item.subject_name
                item['item_name'] = check_item.item_name
                item['check_command'] = check_item.check_command
                if check_item.check_result:
                    item['check_result'] = check_item.check_result
                else:
                    item['check_result'] = "NULL"
                item['check_remark'] = check_item.check_remark
                data.append(copy.deepcopy(item))
            status = 200
            message = "OK"
    except Exception, error:
        status = 501
        message = 'get exception %s from get_report_list' % str(error)
    finally:
        resp.update({"status": status, "data": data, "message": message})
        return resp, status


class ClusterReportApi(Resource):

    resource = (SfoCheckReport, )

    @login_required
    @permission_required(*resource)
    @marshal_with(cluster_report_fields)
    def get(self):
        try:
            resp, status = get_report_list()
            return resp, status
        except Exception, error:
            access_logger.error('Get ClusterReportApi get exception %s' % error)
            status = 500
            message = "Internal Server Error"
            return {'status': status, "message": message}, status