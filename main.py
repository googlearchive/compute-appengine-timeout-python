#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
from pprint import pformat

import webapp2
import jinja2
from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets

SAMPLE_NAME = 'Instance timeout helper'
GCE_PROJECT_ID = 'briandpe-api'

decorator = OAuth2DecoratorFromClientSecrets(
    os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
    scope='https://www.googleapis.com/auth/compute',
)
compute = build('compute', 'v1beta13')
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'))


class MainHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        list_api = compute.instances().list(project=GCE_PROJECT_ID)
        result = list_api.execute(decorator.http())
        instances = result['items']

        data = {}
        data['title'] = SAMPLE_NAME
        data['instances'] = instances
        data['raw_instances'] = pformat(instances)

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(data))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    (decorator.callback_path, decorator.callback_handler()),
], debug=True)
