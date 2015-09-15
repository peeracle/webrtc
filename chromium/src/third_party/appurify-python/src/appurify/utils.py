"""
    Copyright 2013 Appurify, Inc
    All rights reserved

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
    License for the specific language governing permissions and limitations
    under the License.
"""
import os
import sys
import time
import math
import platform
import requests
import logging

from . import constants

logging.basicConfig(level=logging.WARNING, format='[%(asctime)s] [%(process)d] %(message)s')


def log(msg, level=None): # pragma: no cover
    """simple logging facility"""
    logging.log(level if level else logging.WARNING, msg)


class AppurifyHttpClientError(Exception):
    pass


class AppurifyHttpClient(object):

    def __init__(self, method, resource, payload=None, files=None, headers=None):
        self.method_name = method
        self.method = getattr(requests, self.method_name)
        self.resource = resource
        self.url = self.url(self.resource)
        self.payload = payload
        self.files = files

        if headers:
            assert type(headers) == dict
        else:
            headers = dict()
        self.headers = headers
        self.headers['User-Agent'] = self.user_agent()

        self.retry_count = 0

    @staticmethod
    def url(resource): # pragma: no cover
        """(defaults: https://live.appurify.com:443/resource/)

        Url can be overridden by specifying following environment variables
        APPURIFY_API_PROTO (default: https)
        APPURIFY_API_HOST (default: live.appurify.com)
        APPURIFY_API_PORT (default: 443)

        Clients and Customers MUST not override this unless instructed by Appurify devs
        """
        return '/'.join(['%s://%s:%s/resource' % (AppurifyHttpClient.proto(), AppurifyHttpClient.host(), AppurifyHttpClient.port()), resource]) + '/'

    @staticmethod
    def proto():
        return os.environ.get('APPURIFY_API_PROTO', constants.API_PROTO)

    @staticmethod
    def host():
        return os.environ.get('APPURIFY_API_HOST', constants.API_HOST)

    @staticmethod
    def port():
        return os.environ.get('APPURIFY_API_PORT', str(constants.API_PORT))

    @staticmethod
    def user_agent(): # pragma: no cover
        """returns string representation of user-agent"""
        implementation = platform.python_implementation()

        if implementation == 'CPython':
            version = platform.python_version()
        elif implementation == 'PyPy':
            version = '%s.%s.%s' % (sys.pypy_version_info.major, sys.pypy_version_info.minor, sys.pypy_version_info.micro)
        elif implementation == 'Jython':
            version = platform.python_version()
        elif implementation == 'IronPython':
            version = platform.python_version()
        else:
            version = 'Unknown'

        try:
            system = platform.system()
            release = platform.release()
        except IOError:
            system = 'Unknown'
            release = 'Unknown'

        return " ".join([
            'appurify-client/%s' % constants.__version__,
            'python-requests/%s' % requests.__version__,
            '%s/%s' % (implementation, version),
            '%s/%s' % (system, release)
        ])

    @staticmethod
    def retry_on_failure():
        return int(os.environ.get('APPURIFY_API_RETRY_ON_FAILURE', constants.API_RETRY_ON_FAILURE))

    @staticmethod
    def max_retry():
        return int(os.environ.get('APPURIFY_API_MAX_RETRY', constants.API_MAX_RETRY))

    @staticmethod
    def retry_delay():
        return int(os.environ.get('APPURIFY_API_RETRY_DELAY', constants.API_RETRY_DELAY))

    @staticmethod
    def api_status():
        """returns api service status from aws status page."""
        api_check = os.environ.get('APPURIFY_STATUS_BASE_URL', constants.API_STATUS_BASE_URL)
        if api_check.lower() == 'none':
            return constants.API_STATUS_UP
        url = '%s/%s.txt' % (api_check, AppurifyHttpClient.host().split('.')[0])
        print url
        r = requests.get(url)
        if r.status_code == 200:
            return int(r.text.strip())
        else:
            return constants.API_STATUS_DOWN

    @staticmethod
    def wait_for_api_service():
        """waits endlessly until api service is up.

        .. todo::

            - support timeouts
        """
        n = 1
        while AppurifyHttpClient.api_status() == constants.API_STATUS_DOWN:
            # restrict max sleep to 2^6 ~ 1 min
            delay = int(math.pow(2, n % 7))
            log('Service is down, will retry in %s seconds...' % delay)
            time.sleep(delay)
            n += 1
        log('API service is back up, resuming...')
        return True

    def is_api_response(self, response):
        """detects if response came from api backend or from higher up in the stack."""
        return 'x-api-server-hostname' in response.headers

    def kwargs(self):
        """returns kwargs for configured requests method."""
        kwargs = dict()

        key = 'params' if self.method_name == 'get' else 'data'
        kwargs[key] = self.payload

        kwargs['headers'] = self.headers
        kwargs['verify'] = False

        if self.files:
            kwargs['files'] = self.files

        return kwargs

    def start(self):
        self.retry_count += 1
        log("HTTP %s %s" % (self.method_name.upper(), self.url))

        try:
            response = self.method(self.url, **self.kwargs())
            if self.is_api_response(response):
                # received response from api backend
                return response
            else:
                # received response from higher up the stack
                log('Received unexpected response from API, waiting for service to resume...')
                exc = AppurifyHttpClientError('API failure with response %s, code %s' % (response.text, response.status_code))
                if os.environ.get('APPURIFY_API_WAIT_FOR_SERVICE', constants.API_WAIT_FOR_SERVICE) == 1:
                    self.wait_for_api_service()
                    return self.retry_or_raise(exc)
                else:
                    raise exc
        except requests.exceptions.ConnectionError as e:
            # either no internet connectivity / dns failures
            # or lb is not responding/down
            log('Connection to API server failed, waiting for service to resume...')
            if os.environ.get('APPURIFY_API_WAIT_FOR_SERVICE', constants.API_WAIT_FOR_SERVICE) == 1:
                self.wait_for_api_service()
                return self.retry_or_raise(AppurifyHttpClientError('API failure with reason %s' % str(e)))
            else:
                raise e

    def retry_or_raise(self, exc):
        if self.retry_on_failure() and self.retry_count < self.max_retry():
            time.sleep(int(math.pow(2, self.retry_count)))
            return self.start()
        raise exc


def get(resource, params): # pragma: no cover
    """make a HTTP GET request on API endpoint"""
    client = AppurifyHttpClient('get', resource, params)
    return client.start()


def post(resource, data, files=None): # pragma: no cover
    """make a HTTP POST request on API endpoint"""
    client = AppurifyHttpClient('post', resource, data, files=files)
    return client.start()


def wget(url, path, verify=True): # pragma: no cover
    """Download a file to specified path"""
    with open(path, 'wb') as f:
        result = requests.get(url, verify=verify)
        f.write(result.content)
    return result.status_code
