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
from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets

GCE_PROJECT_ID = 'briandpe-api'

decorator = OAuth2DecoratorFromClientSecrets(
    os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
    scope='https://www.googleapis.com/auth/compute',
)
compute = build('compute', 'v1beta13')


class MainHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('Hello world!')
        list = compute.instances().list(project=GCE_PROJECT_ID)
        instances = list.execute(decorator.http())
        self.response.write(pformat(instances))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    (decorator.callback_path, decorator.callback_handler()),
], debug=True)
