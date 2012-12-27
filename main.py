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
import datetime
import logging
from pprint import pformat

import jinja2
import webapp2
from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator
from oauth2client.appengine import OAuth2DecoratorFromClientSecrets

SAMPLE_NAME = 'Instance timeout helper'
# Be careful, this application will delete instances unless they're tagged
# with one of the SAFE_TAGS below.
GCE_PROJECT_ID = 'briandpe-api'
TIMEOUT = 60  # minutes
SAFE_TAGS = "production safe".split()

# In pretend mode, deletes are only. Set this to False after you've
# double-checked the status page and you're ready to enable the deletes.
PRETEND_MODE = True

decorator = OAuth2DecoratorFromClientSecrets(
    os.path.join(os.path.dirname(__file__), 'client_secrets.json'),
    scope='https://www.googleapis.com/auth/compute',
)
compute = build('compute', 'v1beta13')
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader('templates'))


def annotate_instances(instances):
    for instance in instances:
        # set _excluded
        excluded = False
        for tag in instance.get('tags', []):
            if tag in SAFE_TAGS:
                excluded = True
                break
        instance['_excluded'] = excluded

        # set _age and _timeout_expired (never True for _excluded instances)
        creation = parse_iso8601tz(instance['creationTimestamp'])
        now = datetime.datetime.now()
        delta = now - creation
        instance['_age'] = delta.seconds / 60
        if delta.seconds > TIMEOUT * 60 and not instance['_excluded']:
            instance['_timeout_expired'] = True
        else:
            instance['_timeout_expired'] = False


def list_instances():
        request = compute.instances().list(project=GCE_PROJECT_ID)
        response = request.execute(http=decorator.http())
        instances = response['items']
        annotate_instances(instances)
        return instances


class MainHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        instances = list_instances()

        config = {}
        config['PRETEND_MODE'] = PRETEND_MODE
        config['SAFE_TAGS'] = SAFE_TAGS
        config['TIMEOUT'] = TIMEOUT
        config['GCE_PROJECT_ID'] = GCE_PROJECT_ID
        data = {}
        data['config'] = config
        data['title'] = SAMPLE_NAME
        data['instances'] = instances
        data['raw_instances'] = pformat(instances)

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(data))


def delete_expired_instances():
    instances = list_instances()

    # filter instances, keep expired instances
    instances = [i for i in instances if i['_timeout_expired']]

    for instance in instances:
        name = instance['name']
        if PRETEND_MODE:
            logging.info("PRETEND DELETE: %s", name)
        else:
            logging.info("DELETE: %s", name)
            request = compute.instances().delete(project=GCE_PROJECT_ID,
                                                 instance=name)
            response = request.execute(http=decorator.http())
            logging.info(response)


class DeleteHandler(webapp2.RequestHandler):
    @decorator.oauth_required
    def get(self):
        delete_expired_instances()


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/cron/delete', DeleteHandler),
    (decorator.callback_path, decorator.callback_handler()),
], debug=True)


# ------------------------------------------------
# helpers
def parse_iso8601tz(date_string):
    """return a datetime object for strings in ISO 8601 format.

    This function only reliably parses strings in exactly this format:
    '2012-12-26T13:31:47.823-08:00'

    sadly, datetime.strptime's %z format is unavailable on many platforms.
    """

    dt = datetime.datetime.strptime(date_string[:-6],
                                    '%Y-%m-%dT%H:%M:%S.%f')

    # parse the timezone offset separately
    delta = datetime.timedelta(minutes=int(date_string[-2:]),
                               hours=int(date_string[-5:-3]))
    if date_string[-6:-5] == u'-':
        delta = delta * -1
    dt = dt - delta
    return dt
