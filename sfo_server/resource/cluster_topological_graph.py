#!/usr/bin/env python
# -*- coding:utf-8 -*-
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
import json
from sfo_server.models import SfoClusterMethod, db
from flask_restful import Resource, request
from sfo_common.config_parser import Config
from sfo_server.decorate import login_required, permission_required

global_config = Config()


def add_graph_logic(cluster_name, file_stg):
    status = ''
    message = ''
    resp = {"status": status, "message": message}
    sfo_clu = SfoClusterMethod.query_cluster_by_cluster_name(cluster_name=cluster_name)
    if sfo_clu:
        extend_json = sfo_clu.extend
        extend = json.loads(extend_json)
        topologic_path = os.path.join(global_config.sfo_server_temp_file, 'topologic')
        if not os.path.exists(topologic_path):
            os.makedirs(topologic_path)
        save_path = os.path.join(topologic_path, cluster_name)
        file_stg.save(save_path)
        extend['topologic'] = save_path
        sfo_clu.extend = json.dumps(extend)
        db.session.add(sfo_clu)
        db.session.commit()
        status = 200
        message = 'OK'
    else:
        status = 404
        message = 'Not Found %s cluster' % cluster_name
    resp.update({"status": status, "message": message})
    return resp, status


class TopologicalGraphAPI(Resource):

    resource = (SfoClusterMethod, )

    @login_required
    @permission_required(*resource)
    def post(self, cluster_name):
        try:
            file_stg = request.files.get('file')
            if not file_stg:
                raise ValueError('file is not null')
            resp, status = add_graph_logic(cluster_name, file_stg)
            return resp, status
        except ValueError, error:
            status = 400
            message = str(error)
            return {'status': status, "message": message}, status
        except Exception, error:
            status = 500
            message = str(error)
            return {'status': status, "message": message}, status