#
# Copyright (c) 2017-2018, The Storage Networking Industry Association.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# Neither the name of The Storage Networking Industry Association (SNIA) nor
# the names of its contributors may be used to endorse or promote products
# derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
#  THE POSSIBILITY OF SUCH DAMAGE.
#

#storagegroups_api.py

import json, os
import traceback
import shutil

import logging
import g
import urllib3

from flask import jsonify, request
from flask_restful import Resource
from api_emulator.utils import update_collections_json
from .constants import *
from .templates.storagegroups import get_StorageGroups_instance

members =[]
member_ids = []
foo = False
config = {}
INTERNAL_ERROR = 500


def create_path(*args):
    trimmed = [str(arg).strip('/') for arg in args]
    return os.path.join(*trimmed)


# StorageGroups API
class StorageGroupsAPI(Resource):
    def __init__(self, **kwargs):
        logging.info('StorageGroupsAPI init called')
        self.root = PATHS['Root']
        self.storage_services = PATHS['StorageServices']['path']
        self.storage_groups = PATHS['StorageServices']['storage_groups']

    # HTTP GET
    def get(self, storage_service, storage_groups):
        path = create_path(self.root, self.storage_services, storage_service, self.storage_groups, storage_groups, 'index.json')
        try:
            storage_groups_json = open(path)
            data = json.load(storage_groups_json)
        except Exception as e:
            traceback.print_exc()
            raise Exception("Unable read file because of following error::{}".format(e))
        return jsonify(data)

    # HTTP POST
    # - Create the resource (since URI variables are available)
    # - Update the members and members.id lists
    # - Attach the APIs of subordinate resources (do this only once)
    # - Finally, create an instance of the subordiante resources
    def post(self, storage_service, storage_groups):
        logging.info('StorageGroupsAPI PUT called')
        try:
            global config
            global foo

            wildcards = {'s_id':storage_service, 'sg_id': storage_groups, 'rb': g.rest_base}
            config=get_StorageGroups_instance(wildcards)

            members.append(config)
            member_ids.append({'@odata.id': config['@odata.id']})

            # Create instances of subordinate resources, then call put operation
            # not implemented yet

            path = create_path(self.root, self.storage_services, storage_service, self.storage_groups, storage_groups)
            if not os.path.exists(path):
                os.mkdir(path)
            else:
                # This will execute when POST is called for more than one time for a resource
                return config, 500
            with open(os.path.join(path, "index.json"), "w") as fd:
                fd.write(json.dumps(config, indent=4, sort_keys=True))

            # update the collection json file with new added resource
            collection_path = os.path.join(self.root, self.storage_services, storage_service, self.storage_groups, 'index.json')
            update_collections_json(path=collection_path, link=config['@odata.id'])
            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        logging.info('StorageGroupsAPI put exit')
        return resp


    # HTTP DELETE
    def delete(self,storage_service, storage_groups):
        
        path = os.path.join(self.root, self.storage_services, storage_service, self.storage_groups, storage_groups)
        print (path)
        delPath = path.replace('Resources','/redfish/v1')
        path2 = os.path.join(self.root, self.storage_services, storage_service, self.storage_groups, 'index.json')
        
        try:
            with open(path2,"r") as pdata:
                pdata = json.load(pdata)
                
            data = {
            "@odata.id":delPath
            }            
            resp = 200
            jdata = data["@odata.id"].split('/')
           
            path1 = os.path.join(self.root, self.storage_services, storage_service, self.storage_groups, jdata[len(jdata)-1])
            shutil.rmtree(path1)
            pdata['Members'].remove(data)
            pdata['Members@odata.count'] = int(pdata['Members@odata.count']) - 1
          
            with open(path2,"w") as jdata:
                json.dump(pdata,jdata)
                       

        except Exception as e:
            return {"error": "Unable read file because of following error::{}".format(e)}, 500

        return jsonify(resp)


# StorageGroups Collection API
class StorageGroupsCollectionAPI(Resource):

    def __init__(self):
        self.root = PATHS['Root']
        self.storage_services = PATHS['StorageServices']['path']
        self.storage_groups = PATHS['StorageServices']['storage_groups']

    def get(self, storage_service):
        path = os.path.join(self.root, self.storage_services, storage_service, self.storage_groups, 'index.json')
        try:
            storage_groups_json = open(path)
            data = json.load(storage_groups_json)
        except Exception as e:
            traceback.print_exc()
            return {"error": "Unable read file because of following error::{}".format(e)}, 500

        return jsonify(data)

    def put(self):
        pass

    def verify(self,config):
        #TODO: implement a method to verify that the POST'ed data is valid
        return True,{}

    # The POST command should be for adding multiple instances. For now, just add one.
    def post(self):
        pass



class CreateStorageGroups (Resource):
    def __init__(self):
        self.root = PATHS['Root']
        self.storage_services = PATHS['StorageServices']['path']
        self.storage_groups = PATHS['StorageServices']['storage_groups']

    # Attach APIs for subordinate resource(s). Attach the APIs for a resource collection and its singletons
    def put(self,storage_service):
        logging.info('CreateStorageGroups put started.')
        try:
            path = create_path(self.root, self.storage_services, storage_service, self.storage_groups)
            if not os.path.exists(path):
                os.mkdir(path)
            else:
                logging.info('The given path : {} already Exist.'.format(path))
            config={
                     "@Redfish.Copyright": "Copyright 2015-2016 SNIA. All rights reserved.",
                      "@odata.context": "/redfish/v1/$metadata#StorageGroups.StorageGroups",
                      "@odata.id": "/redfish/v1/StorageServices/$metadata#/StorageGroups",
                      "@odata.type": "#StorageGroupsCollection.1.0.0.StorageGroupsCollection",
                      "Name": "StorageGroups Collection",
                      "Members@odata.count": 0,
                      "Members": [
                      ]
                    }
            with open(os.path.join(path, "index.json"), "w") as fd:
                fd.write(json.dumps(config, indent=4, sort_keys=True))

            resp = config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        logging.info('CreateStorageGroups put exit.')
        return resp
