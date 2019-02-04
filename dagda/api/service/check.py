#
# Licensed to Dagda under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Dagda licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

import json
import datetime
from flask import Blueprint
from exception.dagda_error import DagdaError
from log.dagda_logger import DagdaLogger
from api.internal.internal_server import InternalServer
import pdb
# -- Global

check_api = Blueprint('check_api', __name__)


# Check docker by image name
@check_api.route('/v1/check/images/<path:image_name>', methods=['POST'])
def check_docker_by_image_name(image_name):
    # -- Check input
    if not image_name:
        return json.dumps({'err': 400, 'msg': 'Bad image name'}, sort_keys=True), 400
    metadata = {}
    output = ''
 # -- Docker pull from remote registry if it is necessary
    try:
        pulled = False
        if not InternalServer.get_docker_driver().is_docker_image(image_name):
            if ':' in image_name:
                tmp = image_name.split(':')[0]
                tag = image_name.split(':')[1]
                msg = 'Error: image library/' + image_name + ':' + tag + ' not found'
                output = InternalServer.get_docker_driver().docker_pull(tmp, tag=tag)
            else:
                msg = 'Error: image library/' + image_name + ':latest not found'
                output = InternalServer.get_docker_driver().docker_pull(image_name)
            if 'errorDetail' in output:
                DagdaLogger.get_logger().error(msg)
                raise DagdaError(msg)
            pulled = True
    except Exception as ex:
        message = "Unexpected exception of type {0} occurred while pulling the docker image: {1!r}" \
            .format(type(ex).__name__, ex.get_message() if type(ex).__name__ == 'DagdaError' else ex.args)
        DagdaLogger.get_logger().error(message)
        return json.dumps({'err': 404, 'msg': 'Image name not found'}, sort_keys=True), 404
    
  

    # -- Process request
    data = {}
    data['image_name'] = image_name
    data['timestamp'] = datetime.datetime.now().timestamp()
    data['status'] = 'Analyzing'
    
     
    
    metadata=InternalServer.get_docker_driver().get_image_inspect_info(image_name)   
    data['metadata']=metadata
    DagdaLogger.get_logger().info("metadata is %s " % metadata)
    #get digest data from registry
    registry_info=InternalServer.get_docker_driver().get_image_info(image_name)
    digest=registry_info['Descriptor']['digest']
    
    data['image_digest']=digest
    
    DagdaLogger.get_logger().info("register data is %s " % registry_info)

    output = {}
    
    output['metadata']=metadata
    output['image_digest']=digest
     
 
    
    match = False
    
    #check if image_name with matching digest already exist, 
    result=InternalServer.get_mongodb_driver().get_docker_image_history(image_name, image_digest=digest)
    if len(result)>=1:
        id=result[0]['id']
        output['msg'] = 'Aanalysis of <' + image_name + '> with matching digest already exist '
        output['history']=result
         
        #if there is no exception on previous run, go ahead declare it match and return the result
        if result[0]['status'].find("exception")<0:
          
            match=True
            DagdaLogger.get_logger().info('Aanalysis of < %s > with matching digest already exist ' % image_name)
         
        else:
          
            DagdaLogger.get_logger().info('Aanalysis of < %s > with matching digest  exist, status contains exception, will rerun report ' % image_name)
          
    if not match:
        id = InternalServer.get_mongodb_driver().insert_docker_image_scan_result_to_history(data)
        InternalServer.get_dagda_edn().put({'msg': 'check_image', 'image_name': image_name, '_id': str(id),
                                        'pulled': pulled, 'image_digest': digest})
        output['msg'] = 'Accepted the analysis of <' + image_name + '>'
  
      
    output['id'] = str(id)
    return json.dumps(output, sort_keys=True), 202


# Check docker by container id
@check_api.route('/v1/check/containers/<string:container_id>', methods=['POST'])
def check_docker_by_container_id(container_id):
    
    # -- Check input
    if not container_id:
        return json.dumps({'err': 400, 'msg': 'Bad container id'}, sort_keys=True), 400

    # -- Retrieves docker image name
    try:
        image_name = InternalServer.get_docker_driver().get_docker_image_name_by_container_id(container_id)
    except Exception as ex:
        message = "Unexpected exception of type {0} occurred while getting the docker image name: {1!r}" \
            .format(type(ex).__name__, ex.get_message() if type(ex).__name__ == 'DagdaError' else ex.args)
        DagdaLogger.get_logger().error(message)
        return json.dumps({'err': 404, 'msg': 'Container Id not found'}, sort_keys=True), 404

    # -- Process request
    data = {}
    data['image_name'] = image_name
    data['timestamp'] = datetime.datetime.now().timestamp()
    data['status'] = 'Analyzing'
    id = InternalServer.get_mongodb_driver().insert_docker_image_scan_result_to_history(data)
    InternalServer.get_dagda_edn().put({'msg': 'check_container', 'container_id': container_id, '_id': str(id)})

    # -- Return
    output = {}
    output['id'] = str(id)
    output['msg'] = 'Accepted the analysis of <' + image_name + '> with id: ' + container_id
    return json.dumps(output, sort_keys=True), 202
