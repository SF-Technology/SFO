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

import json
from flask import request
from sfo_server import access_logger
from test.dataresume import DataResumer
from flask_restful import Resource
from sfo_server.resource.common import used_time


def cluster_dataresumer_logic(data_json):
    """
    集群误删恢复
    :param data_json:
    :return:
    """
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    storage_account = 'AUTH_{account_id}'.format(account_id=data_json['account'])
    data_json['account'] = storage_account
    data_json = json.dumps(data_json)
    data_resumer = DataResumer(data_json)
    is_success = data_resumer.resume()
    if is_success:
        status = 201
        message = 'OK'
    else:
        status = 404
        message = 'Resume Fail'
    resp.update({"status": status, "message": message})
    return resp, status


class ClusterDataResumerAPI(Resource):

    """
    误删恢复api
    response :
        { 'status': 200/404 , "message": message}
    content-type : application/json
    """

    # method_decorators = [access_log_decorate]

    @used_time
    def put(self):
        data_json = request.json
        try:
            if data_json:
                resp, status = cluster_dataresumer_logic(data_json)
            else:
                resp, status = {"status": 400, "message": "data_json is null"}
            return resp, status
        except Exception, error:
            access_logger.error('access ClusterDataResumerAPI get exception %s' % error)
            status = 500
            message = "Internal Server Error %s" % error
            return {'status': status, "message": message}, status
